# views/bible_view.py

import streamlit as st
from api.groq_api import generate_bible
from state.story_state import save_bible, advance_step


FIELD_LABELS = {
    "hair": "💇 Hair",
    "clothes": "👕 Clothes & Accessories",
    "face": "😊 Face & Features",
    "build": "🧍 Body & Build",
    "extras": "🎒 Extra Details",
}


def render():

    character_name = st.session_state.settings["character_name"]
    art_style = st.session_state.settings["art_style"]
    age_group = st.session_state.settings["age_group"]

    st.title(f"📝 Design {character_name}")
    st.markdown(f"Generate and edit the appearance of **{character_name}**.")
    st.divider()

    if "bible_gen_count" not in st.session_state:
        st.session_state.bible_gen_count = 0

    if "bible_draft" not in st.session_state:
        with st.spinner(f"Designing {character_name}..."):
            st.session_state.bible_draft = generate_bible(
                character_name=character_name,
                age_group=age_group,
                art_style=art_style,
            )

    st.subheader(f"✏️ {character_name}'s Appearance")

    edited_bible = {}

    for field_key, field_label in FIELD_LABELS.items():
        current_value = st.session_state.bible_draft.get(field_key, "")

        edited_value = st.text_input(
            field_label,
            value=current_value,
            key=f"bible_field_{field_key}_{st.session_state.bible_gen_count}",
        )

        edited_bible[field_key] = edited_value

    st.divider()

    with st.expander("👁️ Prompt Preview"):
        preview_parts = [v for v in edited_bible.values() if v.strip()]

        if preview_parts:
            st.markdown(f"**{character_name}**: " + ", ".join(preview_parts))
            st.caption("Used in image generation prompts.")
        else:
            st.caption("Fill the fields to see preview.")

    st.divider()

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("🔄 Regenerate", use_container_width=True):
            del st.session_state.bible_draft
            st.session_state.bible_gen_count += 1
            st.rerun()

    with col2:
        if st.button(
            f"🔒 Lock {character_name}'s Appearance →",
            use_container_width=True,
            type="primary",
        ):
            if not edited_bible.get("hair", "").strip():
                st.error("Please fill hair description.")
                st.stop()

            if not edited_bible.get("clothes", "").strip():
                st.error("Please fill clothes description.")
                st.stop()

            save_bible(edited_bible)
            del st.session_state.bible_draft
            advance_step("outline")
            st.rerun()

    st.divider()

    with st.expander("ℹ️ Side Characters"):
        st.markdown(
            "Side characters are automatically detected during story generation."
        )