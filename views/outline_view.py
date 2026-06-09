# views/outline_view.py

import streamlit as st
from api.groq_api import generate_outline
from state.story_state import save_outline, advance_step


def render():

    settings = st.session_state.settings
    character_name = settings["character_name"]
    age_group = settings["age_group"]
    num_pages = settings["num_pages"]
    art_style = settings["art_style"]
    bible = st.session_state.main_character["bible"]

    st.title("🗂️ Story Outline")
    st.markdown(
        f"Create the story flow for **{character_name}**. Each beat = one page."
    )
    st.divider()

    if "outline_gen_count" not in st.session_state:
        st.session_state.outline_gen_count = 0

    if "outline_draft" not in st.session_state:
        with st.spinner("Writing your story..."):
            st.session_state.outline_draft = generate_outline(
                character_name=character_name,
                age_group=age_group,
                num_pages=num_pages,
                bible=bible,
            )

    st.subheader("✏️ Story Beats")
    st.caption("Edit or reorder the beats below.")

    draft = st.session_state.outline_draft
    num_beats = len(draft)

    for i, beat in enumerate(draft):

        col_num, col_text, col_up, col_dn = st.columns([0.5, 6, 0.6, 0.6])

        with col_num:
            st.markdown(f"**P{i+1}**")

        with col_text:
            new_value = st.text_input(
                f"Page {i+1}",
                value=beat,
                key=f"beat_{i}_{st.session_state.outline_gen_count}",
                label_visibility="collapsed",
                placeholder=f"What happens on page {i+1}?",
            )
            st.session_state.outline_draft[i] = new_value

        with col_up:
            if st.button(
                "▲",
                key=f"up_{i}_{st.session_state.outline_gen_count}",
                disabled=(i == 0),
            ):
                draft[i], draft[i - 1] = draft[i - 1], draft[i]
                st.session_state.outline_draft = draft
                st.rerun()

        with col_dn:
            if st.button(
                "▼",
                key=f"dn_{i}_{st.session_state.outline_gen_count}",
                disabled=(i == num_beats - 1),
            ):
                draft[i], draft[i + 1] = draft[i + 1], draft[i]
                st.session_state.outline_draft = draft
                st.rerun()

    st.divider()

    with st.expander("👁️ Story Preview"):
        for i, beat in enumerate(st.session_state.outline_draft):
            if beat.strip():
                st.markdown(f"**Page {i+1}:** {beat}")
            else:
                st.markdown(f"⚠️ Page {i+1} is empty")

    st.divider()

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("🔄 Regenerate", use_container_width=True):
            del st.session_state.outline_draft
            st.session_state.outline_gen_count += 1
            st.rerun()

    with col2:
        if st.button(
            "✅ Approve Outline →",
            use_container_width=True,
            type="primary",
        ):
            current_draft = st.session_state.outline_draft
            empty_beats = [i + 1 for i, b in enumerate(current_draft) if not b.strip()]

            if empty_beats:
                st.error(f"Pages {empty_beats} are empty.")
                st.stop()

            if len(current_draft) != num_pages:
                st.warning(
                    f"Expected {num_pages} beats but found {len(current_draft)}."
                )

            save_outline(current_draft)
            del st.session_state.outline_draft
            advance_step("page_text")
            st.rerun()

    st.divider()

    with st.expander("💡 Writing Tips"):
        st.markdown(
            "Good story beats should:\n"
            "- One clear event per page\n"
            "- Easy to visualize\n"
            "- Naturally connect to next page\n\n"
            "Example: 'Maya finds a glowing door in the garden.'"
        )