# ✈️ GitHub Copilot Demo App

> *"I asked GitHub Copilot to write this README. It also asked if it could refactor my life choices while it was at it."*

A [Streamlit](https://streamlit.io/) web app built to showcase the jaw-dropping, finger-saving, coffee-preserving capabilities of **GitHub Copilot** — your AI pair-programmer who never judges your 3 AM commit messages.

---

## 🤔 What Is This?

This project is a **live, interactive demo** designed for GitHub Copilot training sessions and dry runs. It's the kind of app that makes audiences go *"oooh"* and *"aaah"* — and occasionally *"wait, did it just write that entire function by itself?"* (Yes. Yes it did.)

The app has three pages:

| Page | What It Does | Fun Level |
|------|-------------|-----------|
| 🏠 **Home** | Showcases the top 10 GitHub Copilot features | 📈 Educational |
| 🧮 **Calculator** | A clean node-style calculator built entirely in Streamlit | 🔢 Mathy |
| 💡 **Code Generation Lab** | Live coding exercises where Copilot fills in the blanks | 🤯 Mind-blowing |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- A virtual environment (because mixing dependencies is a recipe for chaos and regret)
- GitHub Copilot (obviously — this is a Copilot demo, not a notepad)

### Installation

```bash
# Clone the repo (you probably already did this)
git clone https://github.com/ajafry/copilot-training-dry-run.git
cd copilot-training-dry-run

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
# Or if you're living without uv (bold choice):
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

Your browser will open automatically. If it doesn't, check the terminal for the local URL (usually `http://localhost:8501`). Marvel at the UI. Take screenshots. Tell your friends.

---

## 🗂️ Project Structure

```
copilot-training-dry-run/
├── app.py               # Main entry point — sidebar navigation, page routing
├── requirements.txt     # Python dependencies (just Streamlit, we're minimalists)
└── views/
    ├── __init__.py
    ├── home.py          # Top-10 Copilot features showcase
    ├── calculator.py    # Node-style on-screen calculator
    ├── codegen_lab.py   # Live code generation exercises
    └── styles.py        # Shared CSS styles and footer
```

---

## 💡 The Code Generation Lab (a.k.a. The Star of the Show)

The **Code Generation Lab** is where the magic happens during live demos. It contains six classic coding exercises — each with a docstring and a stub — that GitHub Copilot fills in for you in real time:

1. **Reverse a String** — because every coding workshop starts here
2. **Palindrome Check** — "racecar" is just "racecar" backwards, and Copilot knows it
3. **FizzBuzz** — the interview question that haunts developers in their sleep
4. **Celsius to Fahrenheit** — for those of us who refuse to think in Fahrenheit
5. **Count Vowels** — a, e, i, o, u and sometimes Copilot
6. **Find Max** — finding the biggest number without `max()`, because suffering builds character

Open `views/codegen_lab.py` in VS Code, delete a `pass`, and watch Copilot autocomplete the entire implementation. Then refresh the Streamlit app to see it run live. Gasps optional but encouraged.

---

## 🤖 About GitHub Copilot

GitHub Copilot is an AI pair-programmer that:

- **Autocompletes code** before you even finish thinking about it
- **Answers questions** in plain English inside your editor
- **Reviews pull requests** so your teammates don't have to (they'll still do it anyway, but now they have backup)
- **Writes tests**, **generates documentation**, and **suggests shell commands**
- **Operates autonomously** in Agent Mode, planning and implementing multi-step tasks end-to-end

Essentially, it's like having a senior engineer on call 24/7 who never gets tired, never complains about the codebase, and never steals your lunch from the fridge.

---

## 🙏 Acknowledgements

Built with ❤️ (and a suspiciously large amount of Copilot assistance) using:

- [Streamlit](https://streamlit.io/) — the fastest way to turn Python into a web app
- [GitHub Copilot](https://github.com/features/copilot) — the AI that wrote 40% of this README and is very proud of it

---

> *"Any sufficiently advanced AI is indistinguishable from a very fast intern."*
