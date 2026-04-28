"""Tests for calculator module behavior."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from views import calculator


def _set_fake_state(monkeypatch: pytest.MonkeyPatch, expr: str = "", result: str = "") -> SimpleNamespace:
    state = SimpleNamespace(calc_expr=expr, calc_result=result)
    fake_streamlit = SimpleNamespace(session_state=state)
    monkeypatch.setattr(calculator, "st", fake_streamlit)
    return state


def test_factorial_returns_expected_values() -> None:
    assert calculator.factorial(0) == 1
    assert calculator.factorial(1) == 1
    assert calculator.factorial(5) == 120


@pytest.mark.parametrize("value", [-1, 2.5, "3"])
def test_factorial_returns_error_value_for_invalid_inputs(value: object) -> None:
    result = calculator.factorial(value)  # type: ignore[arg-type]
    assert result == -1, f"Expected -1 for invalid input {value}, got {result}"


def test_append_updates_expression_and_clears_result(monkeypatch: pytest.MonkeyPatch) -> None:
    state = _set_fake_state(monkeypatch, expr="12", result="15")

    calculator._append("+")

    assert state.calc_expr == "12+"
    assert state.calc_result == ""


def test_clear_resets_expression_and_result(monkeypatch: pytest.MonkeyPatch) -> None:
    state = _set_fake_state(monkeypatch, expr="7*6", result="42")

    calculator._clear()

    assert state.calc_expr == ""
    assert state.calc_result == ""


def test_backspace_removes_last_character_and_clears_result(monkeypatch: pytest.MonkeyPatch) -> None:
    state = _set_fake_state(monkeypatch, expr="123", result="123")

    calculator._backspace()

    assert state.calc_expr == "12"
    assert state.calc_result == ""


def test_evaluate_returns_result_for_valid_expression(monkeypatch: pytest.MonkeyPatch) -> None:
    state = _set_fake_state(monkeypatch, expr="(2+3)*4")

    calculator._evaluate()

    assert state.calc_result == "20"


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("1+2+3", "6"),
        ("3*2+1", "7"),
        ("8/2+5", "9.0"),
        ("9-3-1", "5"),
    ],
)
def test_evaluate_returns_result_for_expression_without_parentheses(
    monkeypatch: pytest.MonkeyPatch,
    expr: str,
    expected: str,
) -> None:
    state = _set_fake_state(monkeypatch, expr=expr)

    calculator._evaluate()

    assert state.calc_result == expected


@pytest.mark.parametrize("expr", ["", "2+abc", "__import__('os').system('dir')"])
def test_evaluate_returns_error_for_invalid_expression(
    monkeypatch: pytest.MonkeyPatch,
    expr: str,
) -> None:
    state = _set_fake_state(monkeypatch, expr=expr)

    calculator._evaluate()

    assert state.calc_result == "Error"


def test_evaluate_returns_error_on_runtime_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    state = _set_fake_state(monkeypatch, expr="1/0")

    calculator._evaluate()

    assert state.calc_result == "Error"
