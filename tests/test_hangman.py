"""Tests for HangmanEngine — because even the Grim Reaper needs unit tests.

We test the brains of the operation (HangmanEngine) in pure isolation,
no Streamlit summoned, no gallows drawn — just raw logic vs. pytest.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from views.hangman import (
    GALLOWS_OF_DOOM,
    HINT_TRIGGER_COUNT,
    MAX_WRONG_GUESSES,
    THE_FELLOWSHIP_OF_WORDS,
    HangmanEngine,
)

# ---------------------------------------------------------------------------
# Word bank sanity checks — the multiverse must hold at least 30 champions
# ---------------------------------------------------------------------------


def test_fellowship_has_at_least_thirty_words() -> None:
    """The Fellowship shall not be smaller than thirty."""
    assert len(THE_FELLOWSHIP_OF_WORDS) >= 30


def test_fellowship_contains_only_lowercase_alpha_words() -> None:
    """Every word in the bank must be lowercase and purely alphabetic."""
    for word in THE_FELLOWSHIP_OF_WORDS:
        assert word.isalpha() and word == word.lower(), (
            f"'{word}' violates the sacred naming law"
        )


def test_gallows_has_seven_stages() -> None:
    """Seven stages of ASCII art — from chill to dramatic finale."""
    assert len(GALLOWS_OF_DOOM) == MAX_WRONG_GUESSES + 1


# ---------------------------------------------------------------------------
# HangmanEngine — initial state — "In the beginning there was a blank word"
# ---------------------------------------------------------------------------


def test_engine_starts_with_no_guesses() -> None:
    engine = HangmanEngine(secret_word="python")
    assert engine.correct_guesses == set()
    assert engine.wrong_guesses == set()


def test_engine_masked_word_is_all_underscores_at_start() -> None:
    engine = HangmanEngine(secret_word="python")
    assert engine.masked_word == "_ _ _ _ _ _"


def test_engine_wrong_count_starts_at_zero() -> None:
    engine = HangmanEngine(secret_word="python")
    assert engine.wrong_count == 0


def test_engine_is_not_over_at_start() -> None:
    engine = HangmanEngine(secret_word="python")
    assert not engine.is_over
    assert not engine.is_won
    assert not engine.is_lost


# ---------------------------------------------------------------------------
# HangmanEngine.guess — the moment of truth
# ---------------------------------------------------------------------------


def test_correct_guess_returns_true_and_updates_correct_set() -> None:
    engine = HangmanEngine(secret_word="matrix")
    result = engine.guess("m")
    assert result is True
    assert "m" in engine.correct_guesses
    assert engine.wrong_count == 0


def test_wrong_guess_returns_false_and_updates_wrong_set() -> None:
    engine = HangmanEngine(secret_word="matrix")
    result = engine.guess("z")
    assert result is False
    assert "z" in engine.wrong_guesses
    assert engine.wrong_count == 1


def test_guess_is_case_insensitive() -> None:
    """Uppercase inputs should be treated as lowercase — no discrimination."""
    engine = HangmanEngine(secret_word="gandalf")
    result = engine.guess("G")
    assert result is True
    assert "g" in engine.correct_guesses


def test_duplicate_correct_guess_is_ignored() -> None:
    """Déjà vu cache — already correct letters do nothing."""
    engine = HangmanEngine(secret_word="avengers")
    engine.guess("a")
    engine.guess("a")
    assert engine.correct_guesses == {"a"}
    assert engine.wrong_count == 0


def test_duplicate_wrong_guess_is_ignored() -> None:
    """Déjà vu cache — already wrong letters do nothing either."""
    engine = HangmanEngine(secret_word="batman")
    engine.guess("z")
    engine.guess("z")
    assert engine.wrong_guesses == {"z"}
    assert engine.wrong_count == 1


def test_non_alpha_guess_returns_false_and_changes_nothing() -> None:
    engine = HangmanEngine(secret_word="batman")
    result = engine.guess("3")
    assert result is False
    assert engine.correct_guesses == set()
    assert engine.wrong_guesses == set()


def test_multi_char_guess_returns_false_and_changes_nothing() -> None:
    engine = HangmanEngine(secret_word="batman")
    result = engine.guess("ab")
    assert result is False
    assert engine.correct_guesses == set()
    assert engine.wrong_guesses == set()


# ---------------------------------------------------------------------------
# HangmanEngine win / loss conditions — "You Win" vs "You Died"
# ---------------------------------------------------------------------------


def test_is_won_after_all_letters_guessed() -> None:
    engine = HangmanEngine(secret_word="yoda")
    for letter in "yoda":
        engine.guess(letter)
    assert engine.is_won
    assert engine.is_over
    assert not engine.is_lost


def test_is_lost_after_max_wrong_guesses() -> None:
    engine = HangmanEngine(secret_word="yoda")
    for letter in "bcfghij":  # none of these are in "yoda"
        if engine.is_lost:
            break
        engine.guess(letter)
    assert engine.is_lost
    assert engine.is_over
    assert not engine.is_won


def test_masked_word_reveals_correct_guesses_only() -> None:
    engine = HangmanEngine(secret_word="dragon")
    engine.guess("d")
    engine.guess("r")
    assert engine.masked_word == "d r _ _ _ _"


# ---------------------------------------------------------------------------
# HangmanEngine.gallows_stage — ASCII art progression
# ---------------------------------------------------------------------------


def test_gallows_stage_zero_at_start() -> None:
    engine = HangmanEngine(secret_word="phantom")
    assert engine.gallows_stage == GALLOWS_OF_DOOM[0]


def test_gallows_advances_with_wrong_guesses() -> None:
    engine = HangmanEngine(secret_word="phantom")
    engine.guess("z")
    assert engine.gallows_stage == GALLOWS_OF_DOOM[1]
    engine.guess("x")
    assert engine.gallows_stage == GALLOWS_OF_DOOM[2]


def test_gallows_stage_caps_at_max() -> None:
    """Even if we somehow exceed MAX_WRONG_GUESSES, we stay at the last stage."""
    engine = HangmanEngine(
        secret_word="phantom",
        wrong_guesses={"a", "b", "c", "d", "e", "f", "g"},  # 7 wrong — over the limit
    )
    assert engine.gallows_stage == GALLOWS_OF_DOOM[MAX_WRONG_GUESSES]


# ---------------------------------------------------------------------------
# HangmanEngine.hint_available — the Obi-Wan "only hope" feature
# ---------------------------------------------------------------------------


def test_hint_available_at_trigger_count() -> None:
    engine = HangmanEngine(secret_word="nebula")
    for letter in "xyz":  # exactly HINT_TRIGGER_COUNT wrong guesses
        engine.guess(letter)
    assert engine.wrong_count == HINT_TRIGGER_COUNT
    assert engine.hint_available


def test_hint_not_available_below_trigger_count() -> None:
    engine = HangmanEngine(secret_word="nebula")
    engine.guess("z")  # only 1 wrong
    assert not engine.hint_available


def test_hint_not_available_if_already_deployed() -> None:
    engine = HangmanEngine(secret_word="nebula", hint_deployed=True)
    engine.wrong_guesses = {"a", "b", "c"}  # meets trigger count
    assert not engine.hint_available


def test_hint_not_available_when_game_is_over() -> None:
    engine = HangmanEngine(secret_word="nebula")
    for letter in "bcdfgz":  # 6 wrong → game over
        engine.guess(letter)
    assert engine.is_lost
    assert not engine.hint_available


# ---------------------------------------------------------------------------
# HangmanEngine.deploy_hint — the Oracle speaks
# ---------------------------------------------------------------------------


def test_deploy_hint_reveals_an_unguessed_letter() -> None:
    engine = HangmanEngine(secret_word="quantum")
    engine.wrong_guesses = {"b", "c", "d"}  # trigger met
    revealed = engine.deploy_hint()
    assert revealed is not None
    assert revealed in "quantum"
    assert revealed in engine.correct_guesses
    assert engine.hint_deployed is True


def test_deploy_hint_returns_none_when_unavailable() -> None:
    engine = HangmanEngine(secret_word="quantum")  # 0 wrong guesses — no hint yet
    result = engine.deploy_hint()
    assert result is None


def test_deploy_hint_can_only_be_used_once() -> None:
    engine = HangmanEngine(secret_word="quantum")
    engine.wrong_guesses = {"b", "c", "d"}
    first = engine.deploy_hint()
    second = engine.deploy_hint()  # hint_deployed is now True
    assert first is not None
    assert second is None


def test_deploy_hint_does_not_reveal_already_guessed_letter() -> None:
    engine = HangmanEngine(secret_word="eclipse")
    # Pre-fill all but one letter as correct
    engine.correct_guesses = {"e", "c", "l", "i", "p", "s"}  # only "e" repeated; "e" done
    engine.wrong_guesses = {"b", "z", "x"}  # trigger met
    revealed = engine.deploy_hint()
    # The only unguessed letter is nothing — all unique letters already guessed
    # "eclipse" = e,c,l,i,p,s,e — unique: e,c,l,i,p,s
    # all already in correct_guesses → unguessed list is empty
    assert revealed is None
