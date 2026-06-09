# app.py

import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import streamlit as st

# State manager
from state.story_state import init_state

# Import all app screens/views
from views import (
    setup_view,
    bible_view,
    outline_view,
    page_text_view,
    page_image_view,
    export_view,
)


# Configure browser tab
# Must be first Streamlit command
st.set_page_config(
    page_title="Story Generator",
    page_icon="📖",
    layout="centered"
)


# Initialize session state variables
# Safe to run every rerun
init_state()

if "sdxl_pipeline" not in st.session_state:
    with st.spinner("⏳ Loading image model... (first time only, ~60 seconds)"):
        from models.model_loader import get_pipeline
        get_pipeline()
        
# Steps shown in progress bar
STEPS = [
    "setup",
    "bible",
    "outline",
    "page_text",
    "page_image",
    "export"
]

# User-friendly step names
STEP_LABELS = {
    "setup": "⚙️ Setup",
    "bible": "📝 Character",
    "outline": "🗂️ Outline",
    "page_text": "✍️ Page Text",
    "page_image": "🎨 Page Image",
    "export": "📚 Export",
}


# Current active step
current_step = st.session_state.current_step


# Show progress bar at top
cols = st.columns(len(STEPS))

for i, step in enumerate(STEPS):

    with cols[i]:

        # Current step
        if step == current_step:

            st.markdown(
                f"**{STEP_LABELS[step]}**",
                help=f"Current step: {STEP_LABELS[step]}"
            )

        # Completed steps
        elif STEPS.index(step) < STEPS.index(current_step):

            st.markdown(
                f"<span style='color:gray'>✓ {STEP_LABELS[step]}</span>",
                unsafe_allow_html=True
            )

        # Upcoming steps
        else:

            st.markdown(
                f"<span style='color:lightgray'>{STEP_LABELS[step]}</span>",
                unsafe_allow_html=True
            )


# Divider below progress bar
st.divider()


# Route to correct screen/view
if current_step == "setup":

    setup_view.render()

elif current_step == "bible":

    bible_view.render()

elif current_step == "outline":

    outline_view.render()

elif current_step == "page_text":

    page_text_view.render()

elif current_step == "page_image":

    page_image_view.render()

elif current_step == "export":

    export_view.render()

# Safety check
else:

    st.error(f"Unknown step: '{current_step}'")