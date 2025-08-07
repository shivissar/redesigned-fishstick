# Tamil Buddy — Streamlit App (v2)

Additions in v2:
- **Audio prompts** (Tamil) via cached text‑to‑speech.
- **On‑screen Tamil keyboard** for typing practice.
- **Multi‑deck** spaced repetition (switch between `core`, `travel`, `food`; add your own CSVs in `data/decks/`).

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Using Gemini CLI to grow your deck
1. Install ✨ Gemini CLI (pick one):
   - Homebrew: `brew install gemini-cli`
   - Node: `npm install -g @google/gemini-cli`
   - One‑off: `npx @google/gemini-cli`
2. Authenticate (free tier works):
   - `export GEMINI_API_KEY="YOUR_KEY"`  # from Google AI Studio
3. Generate phrases from a topic (non‑interactive one‑shot):
```bash
# Ask Gemini to emit JSON for 20 beginner phrases about 'market shopping'.
gemini -p "$(cat scripts/prompts/topic_to_json.md)" -- -t "market shopping" > /tmp/newdeck.json
python scripts/json_to_csv.py /tmp/newdeck.json data/decks/shopping.csv
```

## Files
- `app.py` — Streamlit app
- `data/decks/*.csv` — deck files
- `scripts/prompts/topic_to_json.md` — prompt template for Gemini CLI
- `scripts/json_to_csv.py` — convert Gemini JSON → CSV deck
