# views/setup_view.py

import streamlit as st

# Import helper functions for saving state
from state.story_state import save_settings, advance_step


def render():
    """
    Render the setup screen.

    This is the first screen of the app where the user:
    - enters character name
    - selects age group
    - selects number of pages
    - selects illustration style
    """

    # Main page heading
    st.title("📖 Kids Story Generator")

    # Small introduction text
    st.markdown(
        "Fill in the story details below. "
        "You will approve each step before moving forward."
    )

    st.divider()


    # st.form groups all inputs together.
    # Streamlit only reruns when submit button is clicked.
    with st.form("setup_form"):

        # Character section
        st.subheader("🧒 Main Character")


        # User enters main character name
        character_name = st.text_input(
            label="Character Name",
            placeholder="e.g. Maya, Leo, Zara..."
        )


        st.divider()


        # Story settings section
        st.subheader("📚 Story Settings")


        # Select target reader age group.
        # This affects story vocabulary and image mood.
        age_group = st.selectbox(
            label="Reader Age Group",

            options=[
                "4-6",
                "6-8",
                "8-12"
            ],

            index=1
        )


        # Number of story pages.
        # More pages = longer story.
        num_pages = st.slider(
            label="Number of Pages",

            min_value=4,
            max_value=16,

            value=8,
            step=2
        )


        st.divider()


        # Art style section
        st.subheader("🎨 Illustration Style")


        # Select image illustration style.
        # Same style is used for all pages.
        art_style = st.radio(
            label="Choose Illustration Style",

            options=[
                "watercolor",
                "pencil_sketch",
                "flat_vector",
                "oil_painting"
            ],

            index=0,

            # Converts internal values into readable labels
            format_func=lambda x: {

                "watercolor":
                    "🎨 Soft Watercolor",

                "pencil_sketch":
                    "✏️ Pencil Sketch",

                "flat_vector":
                    "🟦 Flat Vector",

                "oil_painting":
                    "🖼️ Oil Painting",

            }[x]
        )


        st.divider()


        # Submit button
        submitted = st.form_submit_button(
            label="Continue →",
            use_container_width=True,
            type="primary"
        )


    # Runs only when button is clicked
    if submitted:


        # Remove extra spaces from name
        character_name = character_name.strip()


        # Character name is required
        if not character_name:

            st.error(
                "Please enter a character name."
            )

            st.stop()


        # Minimum length validation
        if len(character_name) < 2:

            st.error(
                "Character name must be at least 2 characters."
            )

            st.stop()


        # Save validated settings into session_state
        save_settings(
            name=character_name,
            age_group=age_group,
            num_pages=num_pages,
            art_style=art_style,
        )


        # Move app to next screen
        advance_step("bible")


        # Refresh app immediately
        st.rerun()


    # Live preview section
    # Shows selected values before submission
    if character_name:

        st.divider()

        st.subheader("📋 Story Preview")


        # Create 3 columns for preview stats
        col1, col2, col3 = st.columns(3)


        # Character preview
        with col1:

            st.metric(
                label="Character",
                value=character_name
            )


        # Page count preview
        with col2:

            st.metric(
                label="Pages",
                value=f"{num_pages} pages"
            )


        # Age group preview
        with col3:

            st.metric(
                label="Age Group",
                value=f"{age_group} years"
            )


        # Final summary message
        st.info(
            f"You are creating a {num_pages}-page story "
            f"for {age_group} year olds starring "
            f"{character_name} in "
            f"{art_style.replace('_', ' ')} style."
        )
