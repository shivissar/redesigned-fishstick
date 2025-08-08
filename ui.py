
import streamlit as st

# Simple on-screen Tamil keyboard
VOWELS = ["அ","ஆ","இ","ஈ","உ","ஊ","எ","ஏ","ஐ","ஒ","ஓ","ஔ","ஃ"]
CONSONANTS_ROW1 = ["க","ங","ச","ஞ","ட","ண","த","ந","ப","ம"]
CONSONANTS_ROW2 = ["ய","ர","ல","வ","ழ","ள","ற","ன"]
SIGNS = ["ா","ி","ீ","ு","ூ","ெ","ே","ை","ொ","ோ","ௌ","்"]

def render_keyboard(state_key: str):
    st.caption("On‑screen Tamil keyboard")
    # Vowels
    cols = st.columns(len(VOWELS))
    for i, ch in enumerate(VOWELS):
        if cols[i].button(ch, key=f"{state_key}_v_{i}"):
            st.session_state[state_key] += ch

    # Consonants
    cols = st.columns(len(CONSONANTS_ROW1))
    for i, ch in enumerate(CONSONANTS_ROW1):
        if cols[i].button(ch, key=f"{state_key}_c1_{i}"):
            st.session_state[state_key] += ch

    cols = st.columns(len(CONSONANTS_ROW2))
    for i, ch in enumerate(CONSONANTS_ROW2):
        if cols[i].button(ch, key=f"{state_key}_c2_{i}"):
            st.session_state[state_key] += ch

    # Signs
    cols = st.columns(len(SIGNS))
    for i, ch in enumerate(SIGNS):
        if cols[i].button(ch, key=f"{state_key}_s_{i}"):
            st.session_state[state_key] += ch

    # Controls
    c1, c2, c3 = st.columns(3)
    if c1.button("⌫ Backspace"):
        st.session_state[state_key] = st.session_state[state_key][:-1]
    if c2.button("Space"):
        st.session_state[state_key] += " "
    if c3.button("Clear"):
        st.session_state[state_key] = ""

# Transliterations with diacritical marks
TAMIL_TRANSLITERATIONS = {
    # Vowels
    "அ": "a", "ஆ": "ā", "இ": "i", "ஈ": "ī", "உ": "u", "ஊ": "ū",
    "எ": "e", "ஏ": "ē", "ஐ": "ai", "ஒ": "o", "ஓ": "ō", "ஔ": "au",
    "ஃ": "akh",
    # Consonants (example, full list would be extensive)
    "க": "ka", "ங": "ṅa", "ச": "ca", "ஞ": "ña", "ட": "ṭa", "ண": "ṇa",
    "த": "ta", "ந": "na", "ப": "pa", "ம": "ma", "ய": "ya", "ர": "ra",
    "ல": "la", "வ": "va", "ழ": "ḻa", "ள": "ḷa", "ற": "ṟa", "ன": "ṉa",
    # Grantha letters (if applicable, for completeness)
    "ஜ": "ja", "ஷ": "ṣa", "ஸ": "sa", "ஹ": "ha", "க்ஷ": "kṣa", "ஸ்ரீ": "śrī"
}

def render_alphabet_page(helpers):
    """Renders the Tamil alphabet page with transliterations and audio."""
    st.header("Tamil Alphabet")

    st.subheader("Vowels (உயிரெழுத்துக்கள்)")
    for char in VOWELS:
        col1, col2, col3 = st.columns([1, 2, 3])
        with col1:
            st.write(f"## {char}")
        with col2:
            st.write(f"*{TAMIL_TRANSLITERATIONS.get(char, '')}*")
        with col3:
            with st.spinner("Generating audio for Tamil character..."):
                audio_file = helpers.tts_for_alphabet(char)
                if audio_file.exists():
                    st.audio(str(audio_file))

    st.subheader("Consonants (மெய்யெழுத்துக்கள்)")
    all_consonants = CONSONANTS_ROW1 + CONSONANTS_ROW2
    for char in all_consonants:
        col1, col2, col3 = st.columns([1, 2, 3])
        with col1:
            st.write(f"## {char}")
        with col2:
            st.write(f"*{TAMIL_TRANSLITERATIONS.get(char, '')}*")
        with col3:
            with st.spinner("Generating audio for Tamil character..."):
                audio_file = helpers.tts_for_alphabet(char)
                if audio_file.exists():
                    st.audio(str(audio_file))
