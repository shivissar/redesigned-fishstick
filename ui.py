
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
