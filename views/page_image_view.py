import streamlit as st

from api.image_api import (
    generate_first_image,
    generate_with_consistency,
)

from api.prompt_builder import build_image_prompt
from state.story_state import save_page_image, advance_page


def _get_side_characters_on_page(characters_on_page: list) -> list[dict]:

    side_chars = []

    for char_key in characters_on_page:

        if char_key == "main":
            continue

        for char in st.session_state.side_characters:
            if char["name"] == char_key:
                side_chars.append(char)
                break

    return side_chars


def render():

    index = st.session_state.current_page_index
    total_pages = st.session_state.settings["num_pages"]

    character_name = st.session_state.settings["character_name"]
    age_group = st.session_state.settings["age_group"]
    art_style = st.session_state.settings["art_style"]

    bible = st.session_state.main_character["bible"]

    current_page = st.session_state.pages[index]

    approved_text = current_page["text"]
    beat = current_page["beat"]
    scene_setting = current_page.get(
        "scene_setting", "outdoor daytime, natural setting"
    )
    chars_on_page = current_page["characters_on_page"]

    st.title(f"🎨 Page {index + 1} Illustration")

    st.progress(
        value=(index + 0.5) / total_pages,
        text=f"Generating illustration {index + 1} of {total_pages}",
    )

    st.divider()

    st.markdown("**📄 Approved page text:**")
    st.info(f'"{approved_text}"')

    st.divider()

    if "current_image_prompt" not in st.session_state:

        side_chars = _get_side_characters_on_page(chars_on_page)

        prompt = build_image_prompt(
            page_text=approved_text,
            beat=beat,
            art_style=art_style,
            age_group=age_group,
            main_character_name=character_name,
            main_character_bible=bible,
            scene_setting=scene_setting,
            side_characters_on_page=side_chars,
        )

        st.session_state.current_image_prompt = prompt

    st.subheader("🔧 Image Prompt")

    edited_prompt = st.text_area(
        "Image prompt",
        value=st.session_state.current_image_prompt,
        height=150,
        key="prompt_editor",
        label_visibility="collapsed",
    )

    st.session_state.current_image_prompt = edited_prompt

    st.divider()

    if "current_image_bytes" not in st.session_state:

        if st.button(
            "🎨 Generate Illustration",
            use_container_width=True,
            type="primary",
        ):

            with st.spinner("Generating illustration... (~20 seconds)"):

                if index == 0:

                    image_bytes, seed = generate_first_image(
                        prompt=edited_prompt
                    )

                    if image_bytes:
                        st.session_state.main_character[
                            "reference_image_bytes"
                        ] = image_bytes

                        st.session_state.main_character["locked_seed"] = seed

                else:

                    image_bytes, seed = generate_with_consistency(
                        prompt=edited_prompt,
                        reference_image_bytes=st.session_state.main_character[
                            "reference_image_bytes"
                        ],
                        locked_seed=st.session_state.main_character[
                            "locked_seed"
                        ],
                        character_name=character_name,
                        page_index=index,
                    )

                if image_bytes:
                    st.session_state.current_image_bytes = image_bytes
                    st.rerun()

    if "current_image_bytes" in st.session_state:

        st.subheader("🖼️ Generated Illustration")

        st.image(
            st.session_state.current_image_bytes,
            caption=f"Page {index + 1} — {beat}",
            use_container_width=True,
        )

        st.divider()

        def _lock_side_character_references():

            for char in st.session_state.side_characters:

                if (
                    char["name"] in chars_on_page
                    and char["reference_image_bytes"] is None
                    and char["first_appears_on_page"] == index
                ):

                    char["reference_image_bytes"] = (
                        st.session_state.current_image_bytes
                    )

                    char["reference_seed"] = st.session_state.main_character[
                        "locked_seed"
                    ]

        col1, col2 = st.columns([1, 2])

        with col1:

            if st.button(
                "🔄 Regenerate",
                use_container_width=True,
            ):
                del st.session_state.current_image_bytes
                st.rerun()

        with col2:

            if st.button(
                "✅ Approve Illustration →",
                use_container_width=True,
                type="primary",
            ):

                _lock_side_character_references()

                save_page_image(
                    image_prompt=edited_prompt,
                    image_url=st.session_state.current_image_bytes,
                )

                del st.session_state.current_image_bytes
                del st.session_state.current_image_prompt

                advance_page()
                st.rerun()