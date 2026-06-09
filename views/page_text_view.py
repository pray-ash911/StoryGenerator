# views/page_text_view.py
# ─────────────────────────────────────────────
# PURPOSE: Generate and approve page text for current page.
# Part one of the page loop (text → image).
# Runs once per page, current_page_index times total.
#
# Flow:
#   1. Read current beat from approved outline
#   2. Detect any new side characters in the beat
#   3. If new side character → show mini-bible form first
#   4. Generate page text via Groq
#   5. Human edits, then approves
#   6. Save text → advance to page_image step
#
# State keys used:
#   session_state.current_page_index  → which page we're on
#   session_state.outline             → locked beats
#   session_state.pages               → approved pages accumulate here
#   session_state.side_characters     → grows when new chars detected
#   session_state.page_text_draft     → working copy of current page text
# ─────────────────────────────────────────────

import streamlit as st

from api.groq_api import (
    generate_page_text,
    extract_side_characters,
    generate_side_character_description,
    extract_scene_setting,
)

from state.story_state import (
    save_page_text,
    advance_step,
)


# Common words that should NOT be treated as character names.
# Why needed?
# Because the character detector looks for Capitalized Words.
#
# Example:
# "Suddenly Maya opened the door"
#
# "Suddenly" is capitalized because it starts a sentence,
# but it is NOT a character.
#
# Without this list, false characters would constantly appear.
SKIP_WORDS = {
    "the", "a", "an", "in", "on", "at", "to", "and", "but", "or",
    "for", "of", "with", "by", "from", "into", "through",
    "she", "he", "they", "it", "her", "his", "their",
    "wow", "oh", "ah", "hello", "please", "thank",
    "suddenly", "finally", "meanwhile", "then",
    "today", "tomorrow", "morning", "night",
    "red", "blue", "green", "yellow",
    "adventure", "magical", "secret", "beautiful",
}


def _get_prev_page_text() -> str | None:
    """
    Returns the PREVIOUS approved page text.

    Why do we need this?
    So the AI remembers story continuity.

    Example:
    Page 1:
        Maya finds a magic key.

    Page 2:
        AI should continue naturally from that event.

    Without previous page context,
    every page feels disconnected.
    """

    current_index = st.session_state.current_page_index

    # Page 1 has no previous page
    if current_index == 0:
        return None

    pages = st.session_state.pages

    # Return the last approved page text
    if pages:
        return pages[-1]["text"]

    return None


def _get_characters_on_page(beat: str) -> list[str]:
    """
    Returns all characters that appear in the current beat.

    Example:
        ["main", "Bobo", "Luna"]
    """

    # Main character is always on the page
    characters = ["main"]

    # Convert beat to lowercase for easy matching
    beat = beat.lower()

    # Check every side character
    for char in st.session_state.side_characters:

        # If character name appears in beat,
        # add it to the page character list
        if char["name"].lower() in beat:
            characters.append(char["name"])

    return characters


def _is_new_side_character(name: str) -> bool:
    """
    Returns True if character is new.
    Returns False if character already exists.
    """

    for char in st.session_state.side_characters:

        # Compare names in lowercase
        # so "Bobo" and "bobo" are treated the same
        if char["name"].lower() == name.lower():
            return False

    return True


def _detect_new_characters(beat: str) -> list[str]:
    """
    Detects possible NEW character names from the beat text using Groq API.
    Uses st.session_state to cache results and avoid redundant API calls.
    """
    if isinstance(beat, dict):
        beat = beat.get("beat", "")

    main_character_name = st.session_state.settings["character_name"]

    current_index = st.session_state.current_page_index
    cache_key = f"detected_chars_page_{current_index}"

    if cache_key not in st.session_state:
        with st.spinner("AI is scanning beat for side characters..."):
            try:
                detected_names = extract_side_characters(
                    beat=beat,
                    main_character_name=main_character_name
                )
            except Exception as e:
                st.error(f"Error extracting side characters: {e}")
                detected_names = []
            
            cleaned_names = []
            for name in detected_names:
                clean = name.strip(".,!?;:\"'()-")
                if clean and clean.lower() != main_character_name.lower():
                    if clean.lower() not in SKIP_WORDS:
                        cleaned_names.append(clean)
            
            st.session_state[cache_key] = cleaned_names

    return st.session_state[cache_key]


def _render_side_character_form(new_names: list[str], beat: str, art_style: str) -> bool:
    """
    Shows confirmation UI for newly detected characters.

    HUMAN DECISION REQUIRED:
    
    AI detection is NOT perfect.

    So the human decides:
    - Yes → real character
    - No  → false detection

    Returns:
        True  → all handled
        False → still pending
    """

    st.subheader("👥 New Characters Detected")

    st.markdown(
        "Confirm whether these are real story characters."
    )

    # Create tracker only once
    if "pending_side_chars" not in st.session_state:
        st.session_state.pending_side_chars = {}
        with st.spinner("AI is drafting side character descriptions..."):
            for name in new_names:
                try:
                    desc = generate_side_character_description(
                        character_name=name,
                        beat=beat,
                        art_style=art_style
                    )
                except Exception as e:
                    desc = ""
                st.session_state.pending_side_chars[name] = {
                    "confirmed": False,
                    "description": desc
                }

    all_confirmed = True

    for name in new_names:

        pending = st.session_state.pending_side_chars.get(name, {})

        # Already handled
        if pending.get("confirmed"):

            if pending["description"] == "skipped":
                st.info(f"⏭️ {name} skipped")
            else:
                st.success(f"✅ {name} added")

            continue

        all_confirmed = False

        with st.container(border=True):

            st.markdown(f"### {name}")

            description = st.text_input(
                label=f"Describe {name}",
                value=pending.get("description", ""),
                placeholder=(
                    "e.g. tiny green dragon with golden wings"
                ),
                key=f"side_char_desc_{name}",
            )

            col1, col2 = st.columns(2)

            # ADD CHARACTER
            with col1:

                if st.button(
                    f"✅ Add {name}",
                    key=f"add_{name}",
                    use_container_width=True,
                ):

                    if not description.strip():
                        st.error("Please add a description.")
                    else:

                        # Save side character
                        st.session_state.side_characters.append({

                            "name": name,

                            "bible": {
                                "description": description.strip()
                            },

                            "reference_image_bytes": None,

                            "reference_seed": None,

                            "first_appears_on_page":
                                st.session_state.current_page_index,
                        })

                        # Mark as handled
                        st.session_state.pending_side_chars[name] = {
                            "confirmed": True,
                            "description": description.strip(),
                        }

                        st.rerun()

            # SKIP CHARACTER
            with col2:

                if st.button(
                    "❌ Not a character",
                    key=f"skip_{name}",
                    use_container_width=True,
                ):

                    st.session_state.pending_side_chars[name] = {
                        "confirmed": True,
                        "description": "skipped",
                    }

                    st.rerun()

    return all_confirmed


def render():
    """
    Main Streamlit screen renderer.

    app.py calls this when:
        current_step == "page_text"
    """

    # CURRENT PAGE NUMBER
    current_index = st.session_state.current_page_index

    # TOTAL PAGES IN STORY
    total_pages = st.session_state.settings["num_pages"]

    # MAIN CHARACTER NAME
    character_name = (
        st.session_state.settings["character_name"]
    )

    # TARGET AGE GROUP
    age_group = st.session_state.settings["age_group"]

    # APPROVED CHARACTER BIBLE
    bible = st.session_state.main_character["bible"]

    # CURRENT STORY BEAT
    current_beat = st.session_state.outline[current_index]

    # PAGE HEADER
    st.title(f"✍️ Page {current_index + 1} of {total_pages}")

    st.progress(
        value=current_index / total_pages,
        text=f"Page {current_index + 1} of {total_pages}"
    )

    st.divider()

    # SHOW CURRENT STORY BEAT
    st.markdown("### 📌 Story Beat")

    st.info(current_beat)

    st.caption(
        "The generated text should follow this beat."
    )

    st.divider()

    # DETECT NEW SIDE CHARACTERS
    new_characters = _detect_new_characters(current_beat)

    if new_characters:

        truly_new = [

            name
            for name in new_characters

            if _is_new_side_character(name)
        ]

        if truly_new:

            art_style = st.session_state.settings["art_style"]
            all_confirmed = _render_side_character_form(
                truly_new,
                current_beat,
                art_style
            )

            # STOP HERE until human handles characters
            if not all_confirmed:

                st.warning(
                    "Please confirm or skip new characters."
                )

                return

            # Cleanup tracker after completion
            if "pending_side_chars" in st.session_state:
                del st.session_state.pending_side_chars

    # Used to force fresh textarea after regeneration
    if "page_text_gen_count" not in st.session_state:
        st.session_state.page_text_gen_count = 0

    # GENERATE TEXT ONLY ON FIRST LOAD
    #
    # Important:
    # Streamlit reruns constantly.
    #
    # Without this check,
    # API would regenerate on every rerun.
    if "page_text_draft" not in st.session_state:

        with st.spinner(
            f"Writing page {current_index + 1}..."
        ):

            generated_text = generate_page_text(

                character_name=character_name,

                age_group=age_group,

                beat=current_beat,

                prev_page_text=_get_prev_page_text(),

                bible=bible,
            )

        st.session_state.page_text_draft = generated_text

    # TEXT EDITOR
    st.subheader("📄 Page Text")

    edited_text = st.text_area(

        label="Page Text",

        value=st.session_state.page_text_draft,

        height=180,

        key=(
            f"page_text_editor_"
            f"{current_index}_"
            f"{st.session_state.page_text_gen_count}"
        ),

        label_visibility="collapsed",
    )

    # Keep draft updated live
    st.session_state.page_text_draft = edited_text

    # WORD COUNT FEEDBACK
    word_count = (
        len(edited_text.split())
        if edited_text.strip()
        else 0
    )

    if word_count == 0:
        st.caption("⚠️ Text is empty.")

    elif word_count < 15:
        st.caption(f"📝 {word_count} words — a bit short.")

    elif word_count <= 60:
        st.caption(f"✅ {word_count} words — good length.")

    else:
        st.caption(f"📝 {word_count} words — maybe too long.")

    st.divider()

    # SHOW PREVIOUS PAGE FOR CONTINUITY
    if current_index > 0 and st.session_state.pages:

        with st.expander("📖 Previous Page"):

            previous_text = (
                st.session_state.pages[-1]["text"]
            )

            st.markdown(f"*{previous_text}*")

    # ACTION BUTTONS
    col1, col2 = st.columns([1, 2])

    # REGENERATE BUTTON
    with col1:

        if st.button(
            "🔄 Regenerate",
            use_container_width=True,
        ):

            # Delete old draft
            del st.session_state.page_text_draft

            # Force new textarea widget
            st.session_state.page_text_gen_count += 1

            st.rerun()

    # APPROVE BUTTON
    with col2:

        if st.button(
            "✅ Approve Text →",
            use_container_width=True,
            type="primary",
        ):

            # VALIDATION

            if not edited_text.strip():
                st.error("Page text cannot be empty.")
                st.stop()

            if len(edited_text.strip()) < 20:
                st.error("Page text is too short.")
                st.stop()

            # Detect which characters appear on page
            characters_on_page = (
                _get_characters_on_page(current_beat)
            )

            # Extract scene setting using AI
            with st.spinner("AI is extracting scene setting..."):
                try:
                    previous_settings = [
                        p.get("scene_setting")
                        for p in st.session_state.pages
                        if p.get("scene_setting")
                    ]
                    scene_setting = extract_scene_setting(
                        text=current_beat,
                        previous_settings=previous_settings,
                        page_number=current_index + 1
                    )
                except Exception as e:
                    st.error(f"Error extracting scene setting: {e}")
                    scene_setting = "outdoor daytime, natural setting"

            # Save approved page text
            save_page_text(

                page_number=current_index + 1,

                beat=current_beat,

                text=edited_text.strip(),

                characters_on_page=characters_on_page,

                scene_setting=scene_setting,
            )

            # Cleanup temporary state
            del st.session_state.page_text_draft

            if "pending_side_chars" in st.session_state:
                del st.session_state.pending_side_chars

            # Move to image generation step
            advance_step("page_image")

            st.rerun()