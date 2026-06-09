# views/export_view.py

import streamlit as st
from utils.pdf_export import export_pdf
from state.story_state import advance_step


def render():

    character_name = st.session_state.settings["character_name"]
    total_pages = st.session_state.settings["num_pages"]

    st.title("📚 Your Story is Ready!")
    st.markdown(
        f"**{character_name}'s story** — {total_pages} pages. Review and download below."
    )
    st.divider()

    st.subheader("📖 Full Book Preview")

    pages = st.session_state.pages

    for page in pages:
        with st.container(border=True):
            col_img, col_text = st.columns([1, 1])

            with col_img:
                if page["image_url"]:
                    st.image(
                        page["image_url"],
                        caption=f"Page {page['page_number']}",
                        use_container_width=True,
                    )
                else:
                    st.warning(f"No image for page {page['page_number']}")

            with col_text:
                st.markdown(f"**Page {page['page_number']}**")
                st.markdown(page["text"])
                st.caption(f"📌 {page['beat']}")

        st.divider()

    st.subheader("⬇️ Export")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("📄 Generate PDF", use_container_width=True, type="primary"):
            with st.spinner("Building your PDF..."):
                pdf_bytes = export_pdf(
                    pages=pages,
                    title=f"{character_name}'s Story",
                )

            if pdf_bytes:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"{character_name.lower()}_story.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

    with col2:
        if st.button(
            "🔁 Start New Story",
            use_container_width=True,
            help="Clears everything and starts from scratch.",
        ):
            pipeline = st.session_state.get("sdxl_pipeline", None)

            for key in list(st.session_state.keys()):
                if key != "sdxl_pipeline":
                    del st.session_state[key]

            if pipeline:
                st.session_state.sdxl_pipeline = pipeline

            st.rerun()