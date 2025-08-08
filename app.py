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
    ["Home", "Learn (Flashcards)", "Quiz", "Fill-in-the-Blanks", "Type (Translit)", "Type (Tamil KB)", "Alphabet", "Browse Cards", "Progress", "About"],
    index=["Home", "Learn (Flashcards)", "Quiz", "Fill-in-the-Blanks", "Type (Translit)", "Type (Tamil KB)", "Alphabet", "Browse Cards", "Progress", "About"].index(st.session_state[SessionState.PAGE])
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

if page == "Learn (Flashcards)":
    deck = helpers.load_deck(deck_name)
    progress = helpers.load_progress(learner, deck_name)
    st.header(f"Learn — Flashcards ({deck_name})")
    colA, colB = st.columns([3, 1])
    with colA:
        categories = ["All"] + sorted(deck["category"].unique().tolist())
        cat = st.selectbox("What to study?", categories, index=0)
    with colB:
        audio_on = st.checkbox("Play audio", value=True)

    st.write("How to study?")
    c1, c2, c3 = st.columns(3)
    if c1.button("Smart Sort (Due First)"):
        order = "Due first"
    elif c2.button("Random"):
        order = "Random"
    elif c3.button("A-Z"):
        order = "Ascending id"
    else:
        order = "Due first"

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

            if "image" in row and pd.notna(row["image"]):
                st.image(row["image"])

            st.markdown(f"<h3 style='font-size: 40px;'>{row['tamil']}</h3>", unsafe_allow_html=True)
            if audio_on:
                with st.spinner("Generating Tamil audio for this card..."):
                    mp3 = helpers.tts_file(deck_name, int(row["id"]), row["tamil"])
                if mp3.exists():
                    st.audio(str(mp3))
                elif not helpers.GTTS_AVAILABLE:
                    st.caption("Install gTTS for audio: `pip install gTTS` (requires internet).")

            if st.toggle("Show transliteration"):
                st.markdown(f"<p style='font-size: 20px;'>{row['translit']}</p>", unsafe_allow_html=True)
            if st.toggle("Show English"):
                st.markdown(f"<p style='font-size: 20px;'>{row['english']}</p>", unsafe_allow_html=True)

            st.markdown("--- ") # Separator for buttons

            c1, c2, c3, c4 = st.columns(4)
            if c1.button("I knew it ✅"):
                st.session_state[SessionState.SCORE], st.session_state[SessionState.STREAK] = helpers.update_card_progress(
                    progress, int(row["id"]), correct=True, 
                    current_score=st.session_state[SessionState.SCORE], 
                    current_streak=st.session_state[SessionState.STREAK]
                )
                st.session_state[SessionState.LEVEL] = helpers.calculate_level(st.session_state[SessionState.SCORE])
                helpers.save_progress(learner, deck_name, progress)
                st.session_state[SessionState.CARD_INDEX] += 1
                st.rerun()
            if c2.button("So‑so 🤔"):
                # Treat as neither correct nor incorrect, just show next card
                st.session_state[SessionState.CARD_INDEX] += 1
                st.session_state[SessionState.STREAK] = 0 # Break streak
                st.rerun()
            if c3.button("Hard 😩"):
                st.session_state[SessionState.SCORE], st.session_state[SessionState.STREAK] = helpers.update_card_progress(
                    progress, int(row["id"]), correct=False, hard_mode=True, 
                    current_score=st.session_state[SessionState.SCORE], 
                    current_streak=st.session_state[SessionState.STREAK]
                )
                st.session_state[SessionState.LEVEL] = helpers.calculate_level(st.session_state[SessionState.SCORE])
                helpers.save_progress(learner, deck_name, progress)
                st.session_state[SessionState.CARD_INDEX] += 1
                st.rerun()
            if c4.button("I missed it ❌"):
                st.session_state[SessionState.SCORE], st.session_state[SessionState.STREAK] = helpers.update_card_progress(
                    progress, int(row["id"]), correct=False, 
                    current_score=st.session_state[SessionState.SCORE], 
                    current_streak=st.session_state[SessionState.STREAK]
                )
                st.session_state[SessionState.LEVEL] = helpers.calculate_level(st.session_state[SessionState.SCORE])
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
            if direction == "Tamil → English":
                question = f"{qrow['tamil']} ({qrow['translit']})"
                correct_answer = qrow['english']
                options = [correct_answer] + pool[pool['id'] != qrow['id']].sample(min(3, len(pool)-1))['english'].tolist()
            else: # English → Tamil
                question = qrow['english']
                correct_answer = f"{qrow['tamil']} ({qrow['translit']})"
                
                other_choices = pool[pool['id'] != qrow['id']].sample(min(3, len(pool)-1))
                options = [correct_answer] + [f"{row['tamil']} ({row['translit']})" for _, row in other_choices.iterrows()]

            st.markdown(f"<h3 style='font-size: 30px;'>{question}</h3>", unsafe_allow_html=True)
            with st.spinner("Generating Tamil audio..."):
                mp3 = helpers.tts_file(deck_name, int(qrow["id"]), qrow["tamil"])
            if mp3.exists():
                st.audio(str(mp3))
            elif not helpers.GTTS_AVAILABLE:
                st.caption("Install gTTS for audio: `pip install gTTS` (requires internet).")
            random.shuffle(options)

            choice = st.radio("Pick one:", options, index=None, key="quiz_choice")
            
            col_check, col_next = st.columns(2)

            if col_check.button("Check", disabled=st.session_state.get("quiz_checked", False)):
                st.session_state["quiz_checked"] = True
                is_correct = (choice == correct_answer)
                st.session_state[SessionState.SCORE], st.session_state[SessionState.STREAK] = helpers.update_card_progress(
                    progress, int(qrow["id"]), is_correct, 
                    current_score=st.session_state[SessionState.SCORE], 
                    current_streak=st.session_state[SessionState.STREAK]
                )
                st.session_state[SessionState.LEVEL] = helpers.calculate_level(st.session_state[SessionState.SCORE])
                if is_correct:
                    st.success("Correct!")
                else:
                    st.error(f"Not quite. Correct answer: {correct_answer}")
                helpers.save_progress(learner, deck_name, progress)
                st.session_state["current_qrow"] = qrow # Store qrow for next button
                st.session_state["correct_answer"] = correct_answer # Store correct_answer for next button
                # st.rerun() # Removed rerun here

            if st.session_state.get("quiz_checked", False):
                if col_next.button("Next Question"):
                    st.session_state["quiz_checked"] = False
                    st.session_state[SessionState.CARD_INDEX] += 1 # Advance card index for next question
                    st.rerun()

elif page == "Fill-in-the-Blanks":
    deck = helpers.load_deck(deck_name)
    progress = helpers.load_progress(learner, deck_name)
    st.header(f"Fill-in-the-Blanks ({deck_name})")

    colA, colB = st.columns(2)
    with colA:
        categories = ["All"] + sorted(deck["category"].unique().tolist())
        cat = st.selectbox("Category", categories, index=0)
    with colB:
        st.empty() # Placeholder for future options

    pool = deck.copy() if cat == "All" else deck[deck["category"] == cat].copy()

    if pool.empty:
        st.info("No cards in this category.")
    else:
        with st.container(border=True):
            qrow = pool.sample(1, random_state=random.randint(0, 9999)).iloc[0]
            english_sentence = qrow["english"]
            words = english_sentence.split()
            
            if len(words) > 1:
                # Randomly select a word to mask
                masked_word_index = random.randint(0, len(words) - 1)
                masked_word = words[masked_word_index]
                
                # Create the question sentence with a blank
                question_words = words[:masked_word_index] + ["_____"] + words[masked_word_index+1:]
                question_sentence = " ".join(question_words)
                
                st.markdown(f"<h3 style='font-size: 30px;'>{question_sentence}</h3>", unsafe_allow_html=True)
                user_answer = st.text_input("Your answer:", key="fill_in_blank_answer")

                col_check, col_next = st.columns(2)

                if col_check.button("Check", disabled=st.session_state.get("fill_in_blank_checked", False)):
                    st.session_state["fill_in_blank_checked"] = True
                    is_correct = (helpers.normalize(user_answer) == helpers.normalize(masked_word))
                    st.session_state[SessionState.SCORE], st.session_state[SessionState.STREAK] = helpers.update_card_progress(
                        progress, int(qrow["id"]), is_correct, 
                        current_score=st.session_state[SessionState.SCORE], 
                        current_streak=st.session_state[SessionState.STREAK]
                    )
                    st.session_state[SessionState.LEVEL] = helpers.calculate_level(st.session_state[SessionState.SCORE])
                    if is_correct:
                        st.success("Correct!")
                    else:
                        st.error(f"Not quite. Correct answer: {masked_word}")
                    helpers.save_progress(learner, deck_name, progress)

                if st.session_state.get("fill_in_blank_checked", False):
                    if col_next.button("Next Question"):
                        st.session_state["fill_in_blank_checked"] = False
                        st.session_state[SessionState.CARD_INDEX] += 1 # Advance card index for next question
                        st.rerun()
            else:
                st.info("This card does not have enough words for a fill-in-the-blanks question.")
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

    if st.button("Check"):
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