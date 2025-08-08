
import json
import datetime
import pandas as pd
from pathlib import Path

# --- Constants ----------------------------------------------------------------
# Get the absolute path of the directory containing this script, which is the project root
PROJECT_ROOT = Path(__file__).parent.resolve()
# Define paths relative to the project root
DECKS_DIR = PROJECT_ROOT / "data" / "decks"
PROGRESS_DIR = PROJECT_ROOT / ".progress"
AUDIO_DIR = PROJECT_ROOT / ".audio"

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

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
    """
    Returns a DataFrame of cards that are due for review.
    This is optimized to use vectorized pandas operations.
    """
    if not progress:
        # If no progress, all cards are considered new and thus due.
        return deck.copy()

    now = today()

    # Create a DataFrame from the progress dictionary
    progress_df = pd.DataFrame.from_dict(progress, orient='index')
    if progress_df.empty:
        return deck.copy()

    progress_df.index = progress_df.index.astype(int)

    # Convert 'due' column to date objects, coercing errors
    progress_df['due'] = pd.to_datetime(progress_df['due'], errors='coerce').dt.date

    # Get IDs of cards that are due from the progress data
    # NaT dates (from coerce) will not satisfy the condition, which is correct
    due_in_progress_ids = progress_df[progress_df['due'] <= now].index

    # Get IDs of new cards (in the deck but not in progress)
    deck_ids = set(deck['id'])
    progress_ids = set(progress_df.index)
    new_card_ids = list(deck_ids - progress_ids)

    # Combine the two lists of due card IDs
    due_ids = list(due_in_progress_ids) + new_card_ids

    return deck[deck["id"].isin(due_ids)].copy()

def normalize(s: str) -> str:
    """Normalizes a string by stripping whitespace and converting to lowercase."""
    return (s or "").strip().lower()

def highlight_diff(expected: str, actual: str) -> str:
    """
    Compares two strings and returns an HTML string with differences highlighted.
    Correct characters are green, incorrect are red.
    """
    html_output = []
    min_len = min(len(expected), len(actual))

    for i in range(min_len):
        if expected[i] == actual[i]:
            html_output.append(f"<span style='color: green;'>{actual[i]}</span>")
        else:
            html_output.append(f"<span style='color: red;'>{actual[i]}</span>")

    # Add remaining characters from the longer string
    if len(actual) > len(expected):
        for i in range(min_len, len(actual)):
            html_output.append(f"<span style='color: red;'>{actual[i]}</span>")
    elif len(expected) > len(actual):
        # If expected is longer, show missing characters as red placeholders
        for i in range(min_len, len(expected)):
            html_output.append(f"<span style='color: red;'>_</span>") # Placeholder for missing char

    return "".join(html_output)

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

def tts_for_alphabet(character: str) -> Path:
    """Generates and caches a TTS audio file for a single Tamil character."""
    alphabet_audio_dir = AUDIO_DIR / "_alphabet"
    alphabet_audio_dir.mkdir(parents=True, exist_ok=True)
    # Use a sanitized filename for the character
    safe_char_name = "".join(c for c in character if c.isalnum())
    mp3 = alphabet_audio_dir / f"{safe_char_name}.mp3"
    if GTTS_AVAILABLE and not mp3.exists():
        try:
            # The pronunciation of a standalone consonant is often with an implicit 'a' sound,
            # so we add the vowel sign 'அ' to help gTTS pronounce it more naturally.
            # This is a heuristic and may not be perfect for all characters.
            text_to_speak = character
            if len(character) == 1 and '\u0b80' <= character <= '\u0bff': # In Tamil unicode block
                if character not in "அஆஇஈஉஊஎஏஐஒஓஔஃ": # If it's a consonant
                    text_to_speak = character + " " + "அ"

            gTTS(text=text_to_speak, lang="ta").save(str(mp3))
        except Exception:
            # Fail silently if TTS fails
            pass
    return mp3
