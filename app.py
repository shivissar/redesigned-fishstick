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
    SCORE = "score"
    LEVEL = "level"
    STREAK = "streak"

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
        if SessionState.SCORE not in st.session_state:
            st.session_state[SessionState.SCORE] = 0
        if SessionState.LEVEL not in st.session_state:
            st.session_state[SessionState.LEVEL] = 1
        if SessionState.STREAK not in st.session_state:
            st.session_state[SessionState.STREAK] = 0

# --- Main App -----------------------------------------------------------------
st.set_page_config(
    page_title="Tamil Buddy",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    div[data-testid="stRadio"] label p {
        font-size: 20px; /* Adjust as needed */
    }
</style>
""", unsafe_allow_html=True)

helpers.init_directories()
SessionState.init()

# --- Sidebar -----------------------------------------------------------------
st.sidebar.title("Tamil Buddy")

st.sidebar.markdown(f"**Score:** {st.session_state[SessionState.SCORE]}")
st.sidebar.markdown(f"**Level:** {st.session_state[SessionState.LEVEL]}")
st.sidebar.markdown(f"**Streak:** {st.session_state[SessionState.STREAK]}")

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
    ["Home", "Quiz", "Type (Translit)", "Type (Tamil KB)", "Alphabet", "Browse Cards", "Progress", "About"],
    index=["Home", "Quiz", "Type (Translit)", "Type (Tamil KB)", "Alphabet", "Browse Cards", "Progress", "About"].index(st.session_state[SessionState.PAGE])
)
if page != st.session_state[SessionState.PAGE]:
    st.session_state[SessionState.PAGE] = page
    st.session_state[SessionState.CARD_INDEX] = 0




# --- Pages -------------------------------------------------------------------
if page == "Home":
    st.header("Welcome to Tamil Buddy!")
    st.markdown("""
    Your personal companion for learning Tamil. Choose a learning mode from the sidebar:

    *   **Quiz:** Test your knowledge with multiple-choice questions.
    *   **Type (Translit):** Practice typing Tamil words using transliteration.
    *   **Type (Tamil KB):** Practice typing Tamil words using an on-screen Tamil keyboard.
    *   **Alphabet:** Explore the Tamil alphabet with transliterations and audio.
    *   **Browse Cards:** View all flashcards by category.
    *   **Progress:** Track your learning progress and manage your data.
    *   **About:** Learn more about Tamil Buddy.

    To get started, select a deck from the sidebar.
    """)
elif page == "Browse Cards":
    st.header("Browse All Flashcards")
    all_decks = helpers.list_decks()
    total_cards_count = 0

    for deck_name_item in all_decks:
        deck_df = helpers.load_deck(deck_name_item)
        total_cards_count += len(deck_df)
        st.subheader(f"Deck: {deck_name_item.replace('_', ' ').title()}")
        
        # Group by category and display
        for category, group in deck_df.groupby("category"):
            st.markdown(f"#### Category: {category.title()}")
            for index, row in group.iterrows():
                st.markdown(f"**{row['tamil']}** ({row['translit']}) - {row['english']}")
            st.markdown("--- ")
    st.markdown(f"### Total Flashcards: {total_cards_count}")



elif page == "Quiz":
    deck = helpers.load_deck(deck_name)
    progress = helpers.load_progress(learner, deck_name)
    st.header(f"Quiz — Multiple Choice ({deck_name})")

    # Initialize quiz state
    if 'quiz_question' not in st.session_state:
        st.session_state.quiz_question = None
    if 'quiz_options' not in st.session_state:
        st.session_state.quiz_options = []
    if 'quiz_correct_answer' not in st.session_state:
        st.session_state.quiz_correct_answer = None
    if 'quiz_user_answer' not in st.session_state:
        st.session_state.quiz_user_answer = None
    if 'quiz_answer_submitted' not in st.session_state:
        st.session_state.quiz_answer_submitted = False

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
        # Load a new question if one isn't already loaded
        if st.session_state.quiz_question is None:
            qrow = pool.sample(1, random_state=random.randint(0, 9999)).iloc[0]
            if direction == "Tamil → English":
                st.session_state.quiz_question = f"{qrow['tamil']} ({qrow['translit']})"
                st.session_state.quiz_correct_answer = qrow['english']
                options = [st.session_state.quiz_correct_answer] + pool[pool['id'] != qrow['id']].sample(min(3, len(pool)-1))['english'].tolist()
            else:  # English → Tamil
                st.session_state.quiz_question = qrow['english']
                st.session_state.quiz_correct_answer = f"{qrow['tamil']} ({qrow['translit']})"
                other_choices = pool[pool['id'] != qrow['id']].sample(min(3, len(pool)-1))
                options = [st.session_state.quiz_correct_answer] + [f"{row['tamil']} ({row['translit']})" for _, row in other_choices.iterrows()]
            
            random.shuffle(options)
            st.session_state.quiz_options = options
            st.session_state.qrow = qrow

        st.markdown(f"<h3 style='font-size: 30px;'>{st.session_state.quiz_question}</h3>", unsafe_allow_html=True)
        
        qrow = st.session_state.qrow
        with st.spinner("Generating Tamil audio..."):
            mp3 = helpers.tts_file(deck_name, int(qrow["id"]), qrow["tamil"])
        if mp3.exists():
            st.audio(str(mp3))
        elif not helpers.GTTS_AVAILABLE:
            st.caption("Install gTTS for audio: `pip install gTTS` (requires internet).")

        user_answer = st.radio("Pick one:", st.session_state.quiz_options, index=None, key=f"quiz_radio_{st.session_state[SessionState.CARD_INDEX]}")

        if not st.session_state.quiz_answer_submitted:
            if st.button("Submit", key=f"submit_quiz_{st.session_state[SessionState.CARD_INDEX]}"):
                st.session_state.quiz_user_answer = user_answer
                st.session_state.quiz_answer_submitted = True
                st.rerun()
        else:
            is_correct = (st.session_state.quiz_user_answer == st.session_state.quiz_correct_answer)
            if is_correct:
                st.success("Correct!")
            else:
                st.error(f"Not quite. Correct answer: {st.session_state.quiz_correct_answer}")

            st.session_state[SessionState.SCORE], st.session_state[SessionState.STREAK] = helpers.update_card_progress(
                progress, int(qrow["id"]), is_correct,
                current_score=st.session_state[SessionState.SCORE],
                current_streak=st.session_state[SessionState.STREAK]
            )
            st.session_state[SessionState.LEVEL] = helpers.calculate_level(st.session_state[SessionState.SCORE])
            helpers.save_progress(learner, deck_name, progress)

            if st.button("Next Question", key=f"next_quiz_{st.session_state[SessionState.CARD_INDEX]}"):
                # Reset quiz state for the next question
                st.session_state.quiz_question = None
                st.session_state.quiz_options = []
                st.session_state.quiz_correct_answer = None
                st.session_state.quiz_user_answer = None
                st.session_state.quiz_answer_submitted = False
                st.session_state[SessionState.CARD_INDEX] += 1
                st.rerun()

elif page == "Type (Translit)":
    deck = helpers.load_deck(deck_name)
    progress = helpers.load_progress(learner, deck_name)
    st.header(f"Type — Transliteration ({deck_name})")
    st.write("Type the **transliteration** (Latin letters) for the Tamil text shown.")
    row = deck.sample(1, random_state=random.randint(0, 9999)).iloc[0]
    st.subheader(row["tamil"])
    ans = st.text_input("Transliteration (e.g., 'vanakkam')", value="")
    if st.button("Check", key="check_translit"):
        normalized_ans = helpers.normalize(ans)
        normalized_translit = helpers.normalize(row["translit"])
        is_correct = normalized_ans == normalized_translit
        st.session_state[SessionState.SCORE], st.session_state[SessionState.STREAK] = helpers.update_card_progress(
            progress, int(row["id"]), is_correct, 
            current_score=st.session_state[SessionState.SCORE], 
            current_streak=st.session_state[SessionState.STREAK]
        )
        st.session_state[SessionState.LEVEL] = helpers.calculate_level(st.session_state[SessionState.SCORE])
        if is_correct:
            st.success("Correct!")
        else:
            st.error("Not quite. Here's the comparison:")
            st.markdown(f"Expected: `{row['translit']}`")
            st.markdown(f"Your Answer: `{ans}`")
            st.markdown(f"Difference: {helpers.highlight_diff(normalized_translit, normalized_ans)}", unsafe_allow_html=True)
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

    if st.button("Check", key="check_tamil_kb"):
        user_input = st.session_state.get(SessionState.KEYBOARD_INPUT, "").strip()
        target = str(row["tamil"]).strip()
        is_correct = (user_input == target)
        st.session_state[SessionState.SCORE], st.session_state[SessionState.STREAK] = helpers.update_card_progress(
            progress, int(row["id"]), is_correct, 
            current_score=st.session_state[SessionState.SCORE], 
            current_streak=st.session_state[SessionState.STREAK]
        )
        st.session_state[SessionState.LEVEL] = helpers.calculate_level(st.session_state[SessionState.SCORE])
        if is_correct:
            st.success("Correct!")
        else:
            st.error("Not quite. Here's the comparison:")
            st.markdown(f"Expected: `{target}`")
            st.markdown(f"Your Answer: `{user_input}`")
            st.markdown(f"Difference: {helpers.highlight_diff(target, user_input)}", unsafe_allow_html=True)
        helpers.save_progress(learner, deck_name, progress)

elif page == "Progress":
    deck = helpers.load_deck(deck_name)
    progress = helpers.load_progress(learner, deck_name)
    st.header(f"Progress ({deck_name})")

    boxes = {f"Box {i}": 0 for i in range(1, 6)}
    for cid in deck["id"].tolist():
        box_num = helpers.get_card_state(progress, int(cid))["box"]
        boxes[f"Box {box_num}"] += 1

    st.subheader("Cards per Box")
    st.bar_chart(pd.DataFrame(boxes, index=[0]))

    due = helpers.due_cards(deck, progress)
    st.subheader(f"Due Today: {len(due)}")

    st.subheader("Data Management")
    export_data = helpers.json.dumps(progress, ensure_ascii=False, indent=2)
    st.download_button("Export Progress JSON", data=export_data, file_name=f"tamil_progress_{learner}_{deck_name}.json", mime="application/json")

    up = st.file_uploader("Import Progress JSON", type=["json"])
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