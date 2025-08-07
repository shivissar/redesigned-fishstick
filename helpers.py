
import json
import datetime
import pandas as pd
from pathlib import Path

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

DECKS_DIR = Path("data/decks")
PROGRESS_DIR = Path(".progress")
AUDIO_DIR = Path(".audio")

def init_directories():
    """Create necessary directories if they don't exist."""
    DECKS_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)

def list_decks():
    """Returns a sorted list of available deck names."""
    return sorted([p.stem for p in DECKS_DIR.glob("*.csv")])

def load_deck(deck_name: str) -> pd.DataFrame:
    """Loads a deck from a CSV file into a pandas DataFrame."""
    df = pd.read_csv(DECKS_DIR / f"{deck_name}.csv")
    df["id"] = df["id"].astype(int)
    return df

def progress_path(learner: str, deck_name: str) -> Path:
    """Constructs a safe file path for a learner's progress file."""
    safe_learner = "".join(c for c in learner if c.isalnum() or c in ("-", "_")).strip() or "learner"
    safe_deck = "".join(c for c in deck_name if c.isalnum() or c in ("-", "_")).strip() or "deck"
    return PROGRESS_DIR / f"progress_{safe_learner}_{safe_deck}.json"

def load_progress(learner: str, deck_name: str) -> dict:
    """Loads a learner's progress for a specific deck."""
    p = progress_path(learner, deck_name)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_progress(learner: str, deck_name: str, data: dict):
    """Saves a learner's progress for a specific deck."""
    p = progress_path(learner, deck_name)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def today():
    """Returns the current date."""
    return datetime.date.today()

def schedule_from_box(box: int) -> datetime.date:
    """Calculates the next due date for a card based on its box number."""
    intervals = {1: 1, 2: 2, 3: 4, 4: 7, 5: 15}
    return today() + datetime.timedelta(days=intervals.get(box, 1))

def get_card_state(progress: dict, card_id: int) -> dict:
    """Retrieves the state of a card from the progress data."""
    return progress.get(str(card_id), {"box": 1, "due": str(today())})

def set_card_state(progress: dict, card_id: int, box: int, due: datetime.date):
    """Updates the state of a card in the progress data."""
    progress[str(card_id)] = {"box": int(box), "due": str(due)}

def update_card_progress(progress: dict, card_id: int, correct: bool):
    """Updates the card's box and due date based on whether the answer was correct."""
    state = get_card_state(progress, card_id)
    if correct:
        new_box = min(state["box"] + 1, 5)
        set_card_state(progress, card_id, new_box, schedule_from_box(new_box))
    else:
        set_card_state(progress, card_id, 1, schedule_from_box(1))

def due_cards(deck: pd.DataFrame, progress: dict) -> pd.DataFrame:
    """Returns a DataFrame of cards that are due for review."""
    due_ids, now = [], today()
    for cid in deck["id"].tolist():
        state = get_card_state(progress, cid)
        try:
            due_date = datetime.date.fromisoformat(state["due"])
        except (ValueError, TypeError):
            due_date = now
        if due_date <= now:
            due_ids.append(cid)
    return deck[deck["id"].isin(due_ids)].copy()

def normalize(s: str) -> str:
    """Normalizes a string by stripping whitespace and converting to lowercase."""
    return (s or "").strip().lower()

def tts_file(deck_name: str, phrase_id: int, text_tamil: str) -> Path:
    """Generates and caches a text-to-speech audio file for a Tamil phrase."""
    audio_deck_dir = AUDIO_DIR / deck_name
    audio_deck_dir.mkdir(parents=True, exist_ok=True)
    mp3 = audio_deck_dir / f"{phrase_id}.mp3"
    if GTTS_AVAILABLE and not mp3.exists():
        try:
            gTTS(text=text_tamil, lang="ta").save(str(mp3))
        except Exception:
            # Fail silently if TTS fails
            pass
    return mp3
