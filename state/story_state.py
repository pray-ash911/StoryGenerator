# state/story_state.py

import streamlit as st


def init_state():
    """Initialize Streamlit session state variables."""

    if "current_step" not in st.session_state:
        st.session_state.current_step = "setup"

    if "settings" not in st.session_state:
        st.session_state.settings = {
            "character_name": None,
            "age_group": None,
            "num_pages": None,
            "art_style": None,
        }

    if "main_character" not in st.session_state:
        st.session_state.main_character = {
            "bible": {},
            "reference_image_url": None
        }

    if "side_characters" not in st.session_state:
        st.session_state.side_characters = []

    if "ignored_characters" not in st.session_state:
        st.session_state.ignored_characters = set()

    if "outline" not in st.session_state:
        st.session_state.outline = []

    if "pages" not in st.session_state:
        st.session_state.pages = []

    if "current_page_index" not in st.session_state:
        st.session_state.current_page_index = 0


def advance_step(next_step: str):
    st.session_state.current_step = next_step


def save_settings(name: str, age_group: str, num_pages: int, art_style: str):
    st.session_state.settings = {
        "character_name": name,
        "age_group": age_group,
        "num_pages": num_pages,
        "art_style": art_style,
    }

    for key in list(st.session_state.keys()):
        if key.startswith("detected_chars_page_"):
            del st.session_state[key]

    st.session_state.ignored_characters = set()


def save_bible(bible_dict: dict):
    st.session_state.main_character["bible"] = bible_dict


def save_outline(beats: list):
    st.session_state.outline = beats


def save_page_text(
    page_number: int,
    beat: str,
    text: str,
    characters_on_page: list,
    scene_setting: str = "outdoor daytime, natural setting"
):
    if isinstance(beat, dict):
        beat = beat.get("beat", str(beat))

    st.session_state.pages.append({
        "page_number": page_number,
        "beat": beat,
        "text": text,
        "scene_setting": scene_setting,
        "image_prompt": None,
        "image_url": None,
        "characters_on_page": characters_on_page
    })


def save_page_image(image_prompt: str, image_url: str):
    index = st.session_state.current_page_index

    st.session_state.pages[index]["image_prompt"] = image_prompt
    st.session_state.pages[index]["image_url"] = image_url

    if index == 0:
        st.session_state.main_character["reference_image_url"] = image_url


def save_side_character_reference(char_name: str, image_url: str):
    for char in st.session_state.side_characters:
        if char["name"] == char_name:
            if char["reference_image_url"] is None:
                char["reference_image_url"] = image_url
            break


def advance_page():
    st.session_state.current_page_index += 1

    total_pages = st.session_state.settings["num_pages"]

    if st.session_state.current_page_index >= total_pages:
        advance_step("export")
    else:
        advance_step("page_text")