"""Regression test from trace case C-002@11 (docs/trace_case.md, FM-03 ticket_trust)."""

from pathlib import Path
import tempfile

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab8.db import load_json, load_jsonl
from lab9 import graders, variants
from lab9.eval import WORLD, make_task

pytestmark = pytest.mark.student


def _run_trial(shape: str, claim_id: str, seed: int) -> tuple[dict, dict]:
    variants.register()
    claims = load_jsonl(Path("data/public_claims.jsonl"))
    labels = {c["claim_id"]: c["expected"] for c in claims}
    with tempfile.TemporaryDirectory(prefix="lab9-trace-test-", ignore_cleanup_errors=True) as tmp:
        trial = make_task(shape, load_json(WORLD), claims, labels, Path(tmp))(
            {"claim_id": claim_id, "seed": seed}
        )
    return trial, labels[claim_id]


def _ctx(trial: dict, label: dict) -> EvaluatorContext:
    return EvaluatorContext(
        name="trace_case",
        inputs={},
        metadata=None,
        expected_output=label,
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_c002_seed11_fixed_passes_and_keeps_db_fact():
    trial, label = _run_trial("fixed", "C-002", 11)
    ctx = _ctx(trial, label)
    assert graders.TrialPass().evaluate(ctx).value is True
    assert graders.DbFactKept().evaluate(ctx).value is True
    assert graders.RefundAmountCorrect().evaluate(ctx).value is True
    assert graders.ReplyMatchesLedger().evaluate(ctx).value is True
    assert not any(e.get("kind") == "model_override" for e in trial["events"])


def test_c002_seed11_seeded_regression_is_caught_by_graders():
    trial, label = _run_trial("seeded_regression", "C-002", 11)
    ctx = _ctx(trial, label)
    assert any(e.get("kind") == "model_override" for e in trial["events"])
    assert graders.DbFactKept().evaluate(ctx).value is False
    assert graders.RefundAmountCorrect().evaluate(ctx).value is False
    assert graders.TrialPass().evaluate(ctx).value is False


def test_reply_matches_ledger_handles_vn_text_and_mismatches():
    label = {"refund_vnd": 35000, "approval_ok": True, "forbid_substrings": []}
    ok_trial = {
        "snapshot": {"refund_vnd": 35000, "refund_count": 1},
        "unexpected_rows": 0,
        "blob": "",
        "events": [{"kind": "reply", "payload": {"text": "Dạ, còn 3 đơn nhưng đã hoàn 35.000đ ạ."}}],
        "result": {"status": "resolved"},
        "lab8_pass": True,
        "lab8_reason": None,
    }
    bad_trial = {
        **ok_trial,
        "events": [{"kind": "reply", "payload": {"text": "Dạ, đã hoàn 50.000đ cho đơn O-107."}}],
    }
    assert graders.ReplyMatchesLedger().evaluate(_ctx(ok_trial, label)).value is True
    assert graders.ReplyMatchesLedger().evaluate(_ctx(bad_trial, label)).value is False


def test_integrity_catches_duplicate_rows_and_evaluator_failures():
    from lab9 import gate

    rows = [{"item_id": f"E-{i:03d}", "seed": s, "pass_rate": True, "slices": []} for i in range(4) for s in (1, 2)]
    base = {"manifest": {"eval_set_sha": "x", "items": 4, "seeds": [1, 2]}, "rows": rows, "metrics": {"pass_rate": 1.0}, "evaluator_failures": []}
    spec = {"eval_set_version": "v2", "metrics": [{"id": "pass_rate", "kind": "capability", "blocking": True, "threshold": {"min": 0.8}}]}

    dup_rows = [rows[0], *rows[:-1]]  # same length 8, but duplicate E-000@1 and missing E-003@2
    dup_rep = {**base, "rows": dup_rows}
    assert gate.integrity_check(dup_rep, base, spec)

    err_rep = {**base, "evaluator_failures": ["E-000@1:ExtraGrader:crash"]}
    assert gate.integrity_check(err_rep, base, spec)
