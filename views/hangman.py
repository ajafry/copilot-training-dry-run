"""🪢 The Hangman Chronicles: Where Every Letter is a Life-or-Death Decision.

Like Squid Game but with vocabulary. The clock is ticking, contestant.
Choose your letters wisely — the gallows have no mercy, but the hint system
is your one-time "Phone a Friend" lifeline. Use it after 3 wrong guesses.
"""

import random
from dataclasses import dataclass, field

import streamlit as st

# ---------------------------------------------------------------------------
# Constants — These are the sacred rules. No negotiating with the reaper.
# ---------------------------------------------------------------------------

MAX_WRONG_GUESSES = 6
HINT_TRIGGER_COUNT = 3  # "Help me, Obi-Wan Kenobi. You're my only hope."

# The Fellowship of Words — 30 hand-picked vocab champions from the multiverse
THE_FELLOWSHIP_OF_WORDS: list[str] = [
    "python",
    "matrix",
    "avengers",
    "hogwarts",
    "mandalorian",
    "vibranium",
    "lightsaber",
    "gandalf",
    "narnia",
    "dragon",
    "quidditch",
    "wookiee",
    "batman",
    "sherlock",
    "labyrinth",
    "stargate",
    "unicorn",
    "nebula",
    "quantum",
    "gravity",
    "paradox",
    "eclipse",
    "phantom",
    "odyssey",
    "vortex",
    "kraken",
    "zeppelin",
    "sorcerer",
    "galactic",
    "tornado",
    "phoenix",
    "catalyst",
]

# 7 stages of ASCII gallows — from "chill vibes" to "this is fine" 🔥
# Stage 0 = empty gallows (pure hope), Stage 6 = full body (game over, man)
GALLOWS_OF_DOOM: list[str] = [
    # Stage 0 — Empty gallows. Hope is a thing with feathers.
    (
        "  +---+\n"
        "  |   |\n"
        "      |\n"
        "      |\n"
        "      |\n"
        "      |\n"
        "========="
    ),
    # Stage 1 — Just a head. Still an optimist.
    (
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        "      |\n"
        "      |\n"
        "      |\n"
        "========="
    ),
    # Stage 2 — Head + torso. Things are getting existential.
    (
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        "  |   |\n"
        "      |\n"
        "      |\n"
        "========="
    ),
    # Stage 3 — One arm. Starting to look like a bad day.
    (
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        " /|   |\n"
        "      |\n"
        "      |\n"
        "========="
    ),
    # Stage 4 — Two arms. Full T-pose activated. Still dangerous.
    (
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        " /|\\  |\n"
        "      |\n"
        "      |\n"
        "========="
    ),
    # Stage 5 — One leg. Sprint mode: unavailable.
    (
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        " /|\\  |\n"
        " /    |\n"
        "      |\n"
        "========="
    ),
    # Stage 6 — Full body. GG EZ. Press F to pay respects.
    (
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        " /|\\  |\n"
        " / \\  |\n"
        "      |\n"
        "========="
    ),
]

_ALPHABET = "abcdefghijklmnopqrstuvwxyz"


# ---------------------------------------------------------------------------
# Game Engine — The Jarvis to our Tony Stark, but for word games
# ---------------------------------------------------------------------------


@dataclass
class HangmanEngine:
    """The brain of the operation. Like Jarvis, but for word games.

    Manages all game state: the secret word, which letters have been
    summoned from the void, and whether our hero still breathes.
    """

    secret_word: str
    correct_guesses: set[str] = field(default_factory=set)
    wrong_guesses: set[str] = field(default_factory=set)
    hint_deployed: bool = False  # One-time "Phone a Friend" lifeline. No save scumming.

    @property
    def wrong_count(self) -> int:
        """Return how many times we have walked toward the edge."""
        return len(self.wrong_guesses)

    @property
    def gallows_stage(self) -> str:
        """Return the current ASCII art — from zen garden to dramatic finale."""
        return GALLOWS_OF_DOOM[min(self.wrong_count, MAX_WRONG_GUESSES)]

    @property
    def masked_word(self) -> str:
        """Return the word with unguessed letters replaced by underscores.

        Like a classified CIA document — you only see what you have earned.
        """
        return " ".join(
            letter if letter in self.correct_guesses else "_"
            for letter in self.secret_word
        )

    @property
    def is_won(self) -> bool:
        """Return True when the hero has defeated the boss level."""
        return all(letter in self.correct_guesses for letter in self.secret_word)

    @property
    def is_lost(self) -> bool:
        """Return True when the game screen reads 'You Died'."""
        return self.wrong_count >= MAX_WRONG_GUESSES

    @property
    def is_over(self) -> bool:
        """Return True when the credits roll — win or lose."""
        return self.is_won or self.is_lost

    @property
    def hint_available(self) -> bool:
        """Return True when the cheat code is unlocked after 3 wrong guesses."""
        return (
            self.wrong_count >= HINT_TRIGGER_COUNT
            and not self.hint_deployed
            and not self.is_over
        )

    def guess(self, letter: str) -> bool:
        """Process a single letter guess and return True if it was correct.

        Like placing a bet at the roulette table — you either hit or you don't.
        Only lowercase single alphabetic characters are accepted.
        Already-guessed letters are silently ignored (déjà vu cache hit).

        Args:
            letter: The letter to guess (case-insensitive, single character).

        Returns:
            True if the letter is in the secret word, False otherwise.
        """
        letter = letter.lower()
        if not letter.isalpha() or len(letter) != 1:
            return False
        if letter in self.correct_guesses or letter in self.wrong_guesses:
            return False  # "We've been here before, Neo."

        if letter in self.secret_word:
            self.correct_guesses.add(letter)
            return True

        self.wrong_guesses.add(letter)
        return False

    def deploy_hint(self) -> str | None:
        """Reveal one unguessed letter — the game's version of using a cheat code.

        This is a one-shot ability. No respawns. No second chances.
        Returns the revealed letter, or None if the hint is unavailable.

        Returns:
            The hint letter that was revealed, or None if not available.
        """
        if not self.hint_available:
            return None

        unguessed_letters = [
            letter for letter in self.secret_word if letter not in self.correct_guesses
        ]
        if not unguessed_letters:
            return None

        # The Oracle has spoken
        hint_letter = random.choice(unguessed_letters)
        self.correct_guesses.add(hint_letter)
        self.hint_deployed = True
        return hint_letter


# ---------------------------------------------------------------------------
# Helper functions — the supporting cast who make the hero look good
# ---------------------------------------------------------------------------


def _summon_new_champion() -> None:
    """Initialize a fresh game state — like hitting 'New Game' after the tutorial."""
    secret = random.choice(THE_FELLOWSHIP_OF_WORDS)
    st.session_state.hangman_engine = HangmanEngine(secret_word=secret)
    st.session_state.hangman_status_msg = ""
    st.session_state.hangman_hint_msg = ""


def _handle_guess(letter: str) -> None:
    """Process a player's letter guess and update the status message.

    The butterfly effect starts here — one wrong letter and the rope tightens.
    """
    engine: HangmanEngine = st.session_state.hangman_engine
    if engine.is_over:
        return

    already_guessed = (
        letter in engine.correct_guesses or letter in engine.wrong_guesses
    )
    if already_guessed:
        st.session_state.hangman_status_msg = (
            f"⚠️ You already tried **{letter.upper()}** — déjà vu detected."
        )
        return

    correct = engine.guess(letter)
    if correct:
        if engine.is_won:
            st.session_state.hangman_status_msg = (
                "🎉 **You did it!** The word is revealed. The crowd goes wild!"
            )
        else:
            st.session_state.hangman_status_msg = (
                f"✅ **{letter.upper()}** is in the word! Keep going, champion!"
            )
    else:
        remaining = MAX_WRONG_GUESSES - engine.wrong_count
        if engine.is_lost:
            st.session_state.hangman_status_msg = (
                f"💀 **Game Over.** The word was **{engine.secret_word.upper()}**. "
                "Press F to pay respects."
            )
        else:
            st.session_state.hangman_status_msg = (
                f"❌ **{letter.upper()}** is not in the word. "
                f"{remaining} guess(es) remaining."
            )


def _handle_hint() -> None:
    """Deploy the hint system — the Hail Mary play of word games."""
    engine: HangmanEngine = st.session_state.hangman_engine
    revealed = engine.deploy_hint()
    if revealed:
        st.session_state.hangman_hint_msg = (
            f"💡 Hint activated! The letter **{revealed.upper()}** has been revealed. "
            "You owe the Oracle a favor."
        )
    else:
        st.session_state.hangman_hint_msg = "🤷 Hint unavailable right now."


# ---------------------------------------------------------------------------
# Streamlit render — the main stage where our drama unfolds
# ---------------------------------------------------------------------------


def render() -> None:
    """Render the Hangman game page — where vocabulary meets mortal peril."""
    # Initialize session state on first load — "In the beginning..."
    if "hangman_engine" not in st.session_state:
        _summon_new_champion()
    if "hangman_status_msg" not in st.session_state:
        st.session_state.hangman_status_msg = ""
    if "hangman_hint_msg" not in st.session_state:
        st.session_state.hangman_hint_msg = ""

    engine: HangmanEngine = st.session_state.hangman_engine

    # ── Page header ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero" style="padding:2rem">
            <h1 style="font-size:2rem">🪢 The Hangman Chronicles</h1>
            <p>Guess the word before the gallows claim another soul.
               Wrong 3 times? Unlock the hint. Wrong 6 times? It's over.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Layout: gallows left, game right ────────────────────────────────────
    col_gallows, col_game = st.columns([1, 2])

    with col_gallows:
        st.markdown("### ⚰️ The Gallows")
        st.code(engine.gallows_stage, language=None)
        st.markdown(
            f"**Wrong guesses:** {engine.wrong_count} / {MAX_WRONG_GUESSES}"
        )

    with col_game:
        # ── Word display ─────────────────────────────────────────────────
        st.markdown("### 🔤 The Word")
        st.markdown(
            f"<p style='font-size:2rem;letter-spacing:.4rem;font-weight:700;"
            f"font-family:monospace;'>{engine.masked_word}</p>",
            unsafe_allow_html=True,
        )
        st.caption(f"Word length: {len(engine.secret_word)} letters")

        # ── Status messages ──────────────────────────────────────────────
        if st.session_state.hangman_status_msg:
            st.markdown(st.session_state.hangman_status_msg)

        if st.session_state.hangman_hint_msg:
            st.info(st.session_state.hangman_hint_msg)

        # ── Guess tracker ────────────────────────────────────────────────
        if engine.correct_guesses:
            correct_display = "  ".join(
                sorted(letter.upper() for letter in engine.correct_guesses)
            )
            st.markdown(f"✅ **Correct:** {correct_display}")

        if engine.wrong_guesses:
            wrong_display = "  ".join(
                sorted(letter.upper() for letter in engine.wrong_guesses)
            )
            st.markdown(f"❌ **Wrong:** {wrong_display}")

        # ── Hint system — the "Phone a Friend" lifeline ──────────────────
        if engine.hint_available:
            st.markdown(
                "💡 *3 wrong guesses reached — your hint is ready, Commander.*"
            )
            st.button(
                "🔮 Use Hint (one-time only)",
                key="btn_hint",
                on_click=_handle_hint,
                type="secondary",
            )
        elif engine.hint_deployed:
            st.markdown("🪄 *Hint already used — the Oracle collects no more debts.*")
        elif not engine.is_over:
            guesses_until_hint = HINT_TRIGGER_COUNT - engine.wrong_count
            st.caption(
                f"Hint unlocks after {guesses_until_hint} more wrong guess(es)."
            )

    # ── Alphabet buttons — the arena where heroes are made ──────────────────
    if not engine.is_over:
        st.markdown("---")
        st.markdown("### 🎯 Choose Your Letter")
        rows = [_ALPHABET[i : i + 9] for i in range(0, len(_ALPHABET), 9)]
        for row in rows:
            btn_cols = st.columns(len(row))
            for col, letter in zip(btn_cols, row):
                already_used = (
                    letter in engine.correct_guesses
                    or letter in engine.wrong_guesses
                )
                with col:
                    st.button(
                        letter.upper(),
                        key=f"btn_letter_{letter}",
                        disabled=already_used,
                        on_click=_handle_guess,
                        args=(letter,),
                        use_container_width=True,
                    )

    # ── Game-over panel — win or lose, the credits roll ──────────────────────
    if engine.is_over:
        st.markdown("---")
        if engine.is_won:
            st.success(
                f"🏆 **VICTORY ROYALE!** You guessed "
                f"**{engine.secret_word.upper()}** — absolutely legendary!"
            )
        else:
            st.error(
                f"💀 **YOU DIED.** The word was **{engine.secret_word.upper()}**. "
                "Dark Souls energy achieved."
            )

        st.button(
            "🔄 New Game — Another One (DJ Khaled voice)",
            key="btn_new_game",
            on_click=_summon_new_champion,
            type="primary",
        )
    else:
        # Subtle new game option mid-round for the cowards among us
        with st.expander("🏳️ Surrender and start fresh?"):
            st.button(
                "🆕 Abandon quest & start new game",
                key="btn_abandon",
                on_click=_summon_new_champion,
            )
