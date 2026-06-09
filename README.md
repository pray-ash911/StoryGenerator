# Story Generator

An AI-powered application that generates illustrated children's stories with custom characters, text, and imagery. Built with Streamlit, leveraging cutting-edge AI models for story creation and image generation.

## Features

- **Character Design**: Generate consistent character designs with detailed descriptions (appearance, clothing, personality traits)
- **Story Generation**: Create multi-page story outlines tailored to specific age groups
- **Page-by-Page Content**: Generate unique text and descriptive prompts for each story page
- **AI Image Generation**: Automatically create illustrations using z Image Turbo
- **PDF Export**: Compile finished stories into professional PDF format with images and text
- **Interactive Workflow**: Step-by-step guided process from setup to final export
- **Customizable Settings**: Control character names, target age groups, page count, and art styles

## Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/) - interactive web interface
- **Story & Character AI**: [Groq API](https://groq.com/) with Llama 4 Scout 17B model
- **Image Generation**: z Image Turbo model
- **PDF Export**: [FPDF](https://py-pdf.github.io/fpdf2/)
- **Deep Learning**: PyTorch, Transformers, Accelerate

## Requirements

- Python 3.11 or higher
- 8GB+ RAM recommended (16GB+ for optimal image generation)
- GPU with CUDA support (optional but recommended for faster image generation)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd StoryGenerator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

## Setup

### Required API Keys

The application requires a Groq API key for text generation. Create a `.streamlit/secrets.toml` file in your project directory:

```toml
GROQ_API_KEY = "your-groq-api-key-here"
```

You can get a free API key from [Groq Console](https://console.groq.com/).

### First Run

The first time you run the application, it will download and cache the z Image Turbo model. This may take several minutes depending on your internet connection.

## Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Follow the workflow steps**:
   - **Setup**: Enter character name, target age group, number of pages, and art style
   - **Character Bible**: Review/edit the generated character design details
   - **Story Outline**: Review the story beats for each page
   - **Page Text**: Edit the story text for each page
   - **Page Images**: Generate images for each page (based on the text descriptions)
   - **Export**: Compile and download your story as a PDF

## Project Structure

```
StoryGenerator/
├── app.py                    # Main Streamlit application entry point
├── pyproject.toml           # Project dependencies and metadata
├── README.md                # This file
├── api/
│   ├── groq_api.py         # Groq API integration for story/character generation
│   ├── image_api.py        # Image generation API wrapper
│   └── prompt_builder.py   # Utility for constructing AI prompts
├── models/
│   └── model_loader.py     # z Image Turbo model loading and caching
├── state/
│   └── story_state.py      # Streamlit session state management
├── utils/
│   └── pdf_export.py       # PDF creation and export functionality
└── views/
    ├── setup_view.py       # Initial character and story setup
    ├── bible_view.py       # Character design bible editor
    ├── outline_view.py     # Story outline review/edit
    ├── page_text_view.py   # Page text editor
    ├── page_image_view.py  # Image generation interface
    └── export_view.py      # PDF export interface
```

## Workflow

The application follows a linear workflow to ensure all necessary information is gathered before generation:

```
Setup → Character Bible → Outline → Page Text → Page Images → Export
```

Each step builds on the previous one, allowing you to review and edit content before proceeding.

## Configuration

### Environment Variables

- `PYTORCH_CUDA_ALLOC_CONF`: Set to `expandable_segments:True` for GPU memory optimization (default)

### Customization

You can modify default settings and behavior by editing the relevant view files in the `views/` directory. The state management in `state/story_state.py` handles all session persistence.

## Performance Tips

- **GPU Acceleration**: For significantly faster image generation, use a GPU with CUDA support
- **Model Caching**: The first run downloads and caches models. Subsequent runs will be much faster
- **Image Generation**: Generating images takes the longest (~30-60 seconds per page). Plan accordingly

## Troubleshooting

**Model Download Issues**
- Ensure you have sufficient disk space (15GB+) for model caching
- Check your internet connection for stability

**Out of Memory Errors**
- The `PYTORCH_CUDA_ALLOC_CONF` setting helps with GPU memory management
- Reduce the number of pages in your story to use less memory
- Close other applications to free up system RAM

**API Errors**
- Verify your Groq API key is correct and active
- Check your Groq account for rate limits

## License

This project is provided as-is for educational and creative purposes.

---

