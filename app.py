import random
import pandas as pd
import streamlit as st
from pathlib import Path

import helpers
import ui

# --- Session State -----------------------------------------------------------
class SessionState:
    """A class to manage session state keys."""
    LEARNER = "learner"
    DECK_NAME = "deck_name"
    PAGE = "page"
    CARD_INDEX = "card_index"
    KEYBOARD_INPUT = "keyboard_input"

    @staticmethod
    def init():
        """Initialize session state with default values."""
        if SessionState.LEARNER not in st.session_state:
            st.session_state[SessionState.LEARNER] = "You"
        if SessionState.DECK_NAME not in st.session_state:
            st.session_state[SessionState.DECK_NAME] = None
        if SessionState.PAGE not in st.session_state:
            st.session_state[SessionState.PAGE] = "Home"
        if SessionState.CARD_INDEX not in st.session_state:
            st.session_state[SessionState.CARD_INDEX] = 0
        if SessionState.KEYBOARD_INPUT not in st.session_state:
            st.session_state[SessionState.KEYBOARD_INPUT] = ""

# --- Main App -----------------------------------------------------------------
st.set_page_config(
    page_title="Tamil Buddy",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)

helpers.init_directories()
SessionState.init()

# --- Sidebar -----------------------------------------------------------------
st.sidebar.title("Tamil Buddy")

learner = st.sidebar.text_input(
    "Learner name",
    value=st.session_state[SessionState.LEARNER]
)
if learner != st.session_state[SessionState.LEARNER]:
    st.session_state[SessionState.LEARNER] = learner

available_decks = helpers.list_decks()
if not available_decks:
    st.sidebar.error("No decks found in data/decks.")
    st.stop()

deck_name = st.sidebar.selectbox(
    "Deck",
    available_decks,
    index=available_decks.index(st.session_state[SessionState.DECK_NAME])
    if st.session_state[SessionState.DECK_NAME] in available_decks
    else 0
)
if deck_name != st.session_state[SessionState.DECK_NAME]:
    st.session_state[SessionState.DECK_NAME] = deck_name
    st.session_state[SessionState.CARD_INDEX] = 0

page = st.sidebar.radio(
    "Go to",
    ["Home", "Learn (Flashcards)", "Quiz", "Type (Translit)", "Type (Tamil KB)", "Alphabet", "Progress", "About"],
    index=["Home", "Learn (Flashcards)", "Quiz", "Type (Translit)", "Type (Tamil KB)", "Alphabet", "Progress", "About"].index(st.session_state[SessionState.PAGE])
)
if page != st.session_state[SessionState.PAGE]:
    st.session_state[SessionState.PAGE] = page
    st.session_state[SessionState.CARD_INDEX] = 0




# --- Pages -------------------------------------------------------------------
if page == "Home":
    st.header("Welcome to Tamil Buddy!")
    st.markdown("""
    Your personal companion for learning Tamil. Choose a learning mode from the sidebar:

    *   **Learn (Flashcards):** Practice vocabulary and phrases with spaced repetition.
    *   **Quiz:** Test your knowledge with multiple-choice questions.
    *   **Type (Translit):** Practice typing Tamil words using transliteration.
    *   **Type (Tamil KB):** Practice typing Tamil words using an on-screen Tamil keyboard.
    *   **Alphabet:** Explore the Tamil alphabet with transliterations and audio.
    *   **Progress:** Track your learning progress and manage your data.
    *   **About:** Learn more about Tamil Buddy.

    To get started, select a deck from the sidebar.
    """)
if page == "Learn (Flashcards)":
    deck = helpers.load_deck(deck_name)
    progress = helpers.load_progress(learner, deck_name)
    st.header(f"Learn — Flashcards ({deck_name})")
    colA, colB, colC = st.columns(3)
    with colA:
        categories = ["All"] + sorted(deck["category"].unique().tolist())
        cat = st.selectbox("Category", categories, index=0)
    with colB:
        order = st.selectbox("Order", ["Due first", "Random", "Ascending id"], index=0)
    with colC:
        audio_on = st.checkbox("Play Tamil audio", value=True)

    pool = deck.copy() if cat == "All" else deck[deck["category"] == cat].copy()
    due = helpers.due_cards(pool, progress)
    if order == "Due first":
        show_df = pd.concat([due, pool[~pool["id"].isin(due["id"])]]) if not due.empty else pool
    elif order == "Ascending id":
        show_df = pool.sort_values("id")
    else:
        show_df = pool.sample(frac=1, random_state=random.randint(0, 9999))

    if show_df.empty:
        st.info("No cards available.")
    else:
        total_cards = len(show_df)
        idx = st.session_state[SessionState.CARD_INDEX] % total_cards
        row = show_df.iloc[idx]
        state = helpers.get_card_state(progress, int(row["id"]))

        st.progress((idx + 1) / total_cards, text=f"Card {idx + 1} of {total_cards}")

        with st.container(border=True):
            st.write(f"**Card {int(row['id'])}** · Box **{state['box']}** · Due **{state['due']}**")

            st.markdown(f"### {row['tamil']}")
            if audio_on:
                with st.spinner("Generating Tamil audio for this card..."):
                    mp3 = helpers.tts_file(deck_name, int(row["id"]), row["tamil"])
                if mp3.exists():
                    st.audio(str(mp3))
                elif not helpers.GTTS_AVAILABLE:
                    st.caption("Install gTTS for audio: `pip install gTTS` (requires internet).")

            if st.toggle("Show transliteration"):
                st.write(row["translit"])
            if st.toggle("Show English"):
                st.write(row["english"])

            st.markdown("--- ") # Separator for buttons

            c1, c2, c3 = st.columns(3)
            if c1.button("I knew it ✅"):
                helpers.update_card_progress(progress, int(row["id"]), correct=True)
                helpers.save_progress(learner, deck_name, progress)
                st.session_state[SessionState.CARD_INDEX] += 1
                st.rerun()
            if c2.button("So‑so 🤔"):
                # Treat as neither correct nor incorrect, just show next card
                st.session_state[SessionState.CARD_INDEX] += 1
                st.rerun()
            if c3.button("I missed it ❌"):
                helpers.update_card_progress(progress, int(row["id"]), correct=False)
                helpers.save_progress(learner, deck_name, progress)
                st.session_state[SessionState.CARD_INDEX] += 1
                st.rerun()

elif page == "Quiz":
    deck = helpers.load_deck(deck_name)
    progress = helpers.load_progress(learner, deck_name)
    st.header(f"Quiz — Multiple Choice ({deck_name})")
    colA, colB = st.columns(2)
    with colA:
        direction = st.selectbox("Direction", ["Tamil → English", "English → Tamil"], index=0)
    with colB:
        categories = ["All"] + sorted(deck["category"].unique().tolist())
        cat = st.selectbox("Category", categories, index=0)

    pool = deck.copy() if cat == "All" else deck[deck["category"] == cat].copy()

    if pool.empty:
        st.info("No cards in this category.")
    else:
        with st.container(border=True):
            qrow = pool.sample(1, random_state=random.randint(0, 9999)).iloc[0]
            prompt_side = "tamil_to_english" if direction == "Tamil → English" else "english_to_tamil"
            
            if prompt_side == "tamil_to_english":
                correct_answer = qrow["english"]
                distractors = pool[pool["id"] != qrow["id"]]["english"].sample(min(3, len(pool)-1)).tolist()
            else:
                correct_answer = qrow["tamil"]
                distractors = pool[pool["id"] != qrow["id"]]["tamil"].sample(min(3, len(pool)-1)).tolist()

            options = distractors + [correct_answer]
            random.shuffle(options)

            if prompt_side == "tamil_to_english":
                st.subheader(qrow["tamil"])
            else:
                st.subheader(qrow["english"])

            choice = st.radio("Pick one:", options, index=None)
            if st.button("Check"):
                is_correct = (choice == correct_answer)
                if is_correct:
                    st.success("Correct!")
                else:
                    st.error(f"Not quite. Correct answer: {correct_answer}")
                helpers.update_card_progress(progress, int(qrow["id"]), is_correct)
                helpers.save_progress(learner, deck_name, progress)

elif page == "Type (Translit)":
    deck = helpers.load_deck(deck_name)
    progress = helpers.load_progress(learner, deck_name)
    st.header(f"Type — Transliteration ({deck_name})")
    st.write("Type the **transliteration** (Latin letters) for the Tamil text shown.")
    row = deck.sample(1, random_state=random.randint(0, 9999)).iloc[0]
    st.subheader(row["tamil"])
    ans = st.text_input("Transliteration (e.g., 'vanakkam')", value="")
    if st.button("Check"):
        normalized_ans = helpers.normalize(ans)
        normalized_translit = helpers.normalize(row["translit"])
        is_correct = normalized_ans == normalized_translit
        if is_correct:
            st.success("Correct!")
        else:
            st.error("Not quite. Here's the comparison:")
            st.markdown(f"Expected: `{row['translit']}`")
            st.markdown(f"Your Answer: `{ans}`")
            st.markdown(f"Difference: {helpers.highlight_diff(normalized_translit, normalized_ans)}", unsafe_allow_html=True)
        helpers.update_card_progress(progress, int(row["id"]), is_correct)
        helpers.save_progress(learner, deck_name, progress)

elif page == "Type (Tamil KB)":
    deck = helpers.load_deck(deck_name)
    progress = helpers.load_progress(learner, deck_name)
    st.header(f"Type — Tamil Keyboard ({deck_name})")
    st.write("Use the on‑screen keyboard to type the **Tamil** for the English prompt.")
    row = deck.sample(1, random_state=random.randint(0, 9999)).iloc[0]
    st.subheader(row["english"])
    
    st.text_input("Your Tamil answer", key=SessionState.KEYBOARD_INPUT)
    ui.render_keyboard(SessionState.KEYBOARD_INPUT)

    if st.button("Check"):
        user_input = st.session_state.get(SessionState.KEYBOARD_INPUT, "").strip()
        target = str(row["tamil"]).strip()
        is_correct = (user_input == target)
        if is_correct:
            st.success("Correct!")
        else:
            st.error("Not quite. Here's the comparison:")
            st.markdown(f"Expected: `{target}`")
            st.markdown(f"Your Answer: `{user_input}`")
            st.markdown(f"Difference: {helpers.highlight_diff(target, user_input)}", unsafe_allow_html=True)
        helpers.update_card_progress(progress, int(row["id"]), is_correct)
        helpers.save_progress(learner, deck_name, progress)

elif page == "Progress":
    deck = helpers.load_deck(deck_name)
    progress = helpers.load_progress(learner, deck_name)
    st.header(f"Progress ({deck_name})")
    boxes = {i: 0 for i in range(1, 6)}
    for cid in deck["id"].tolist():
        boxes[helpers.get_card_state(progress, int(cid))["box"]] += 1
    st.write("Cards per box:")
    st.write(pd.DataFrame([boxes]))
    due = helpers.due_cards(deck, progress)
    st.write(f"**Due today:** {len(due)}")

    export_data = helpers.json.dumps(progress, ensure_ascii=False, indent=2)
    st.download_button("Export progress JSON", data=export_data, file_name=f"tamil_progress_{learner}_{deck_name}.json", mime="application/json")

    up = st.file_uploader("Import progress JSON", type=["json"])
    if up:
        try:
            loaded = helpers.json.load(up)
            if isinstance(loaded, dict):
                helpers.save_progress(learner, deck_name, loaded)
                st.success("Progress imported successfully! The page will now reload to reflect the changes.")
                st.rerun()
            else:
                st.error("Invalid format. The imported file should be a JSON dictionary.")
        except Exception as e:
            st.error(f"Failed to import: {e}")

elif page == "Alphabet":
    ui.render_alphabet_page(helpers)

elif page == "About":
    st.header("About")
    st.markdown("""
**Tamil Buddy** (v2) adds audio, keyboard, and multiple decks.  
- Add CSVs to **data/decks/** (columns: `id,category,tamil,translit,english`).  
- Use **scripts/prompts/topic_to_json.md** with **Gemini CLI** to grow decks.  
""")