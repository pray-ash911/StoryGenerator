# api/groq_api.py
import json
import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"


def _call(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    return response.choices[0].message.content.strip()


def generate_bible(character_name: str, age_group: str, art_style: str) -> dict:
    system_prompt = """
You are a children's book character designer.
Return ONLY valid JSON with these keys:
hair, clothes, face, build, extras

STRICT RULES:
- hair: MUST be exactly: "curly brown hair" — always these exact words
- clothes: MUST be exactly one of these formats:
  "bright yellow t-shirt, blue shorts, white sneakers"
  "bright red t-shirt, green shorts, brown shoes"  
  "bright orange t-shirt, blue shorts, white shoes"
  Pick ONE. NO dresses. NO skirts. NO hats. NO aprons.
- face: "round face, young child, big eyes, warm smile"
- build: "small child, wiry and energetic"
- extras: leave empty string ""
"""
    user_prompt = f"""
Character name: {character_name}
Reader age group: {age_group}
Art style: {art_style}

Generate character. Follow the STRICT RULES exactly.
Clothes = t-shirt + shorts + shoes ONLY. Nothing else.
"""
    raw = _call(system_prompt, user_prompt, temperature=0.3)  # ← lower temp for consistency
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        st.warning("Bible formatting issue. Please edit manually.")
        return {"hair": "", "clothes": "", "face": "", "build": "", "extras": ""}

def generate_outline(
    character_name: str,
    age_group: str,
    num_pages: int,
    bible: dict
) -> list:
    bible_text = "\n".join([f"- {key}: {value}" for key, value in bible.items()])
    system_prompt = """
You are a children's story writer.
Return ONLY a JSON array of story beats.
"""
    user_prompt = f"""
Create a {num_pages}-page children's story.
Character: {character_name}
Character details:
{bible_text}
Rules:
- One beat per page
- Fun and imaginative
- Child-friendly
- Clear beginning, middle, and end
"""
    raw = _call(system_prompt, user_prompt, temperature=0.9)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        beats_raw = json.loads(raw)
        beats = []
        for beat in beats_raw:
            if isinstance(beat, dict):
                beats.append(beat.get("beat", str(beat)))
            else:
                beats.append(str(beat))
        if len(beats) != num_pages:
            st.warning(f"Expected {num_pages} beats but got {len(beats)}")
        return beats
    except json.JSONDecodeError:
        st.warning("Outline formatting issue.")
        return ["" for _ in range(num_pages)]


def generate_page_text(
    character_name: str,
    age_group: str,
    beat: str,
    prev_page_text: str | None,
    bible: dict
) -> str:
    bible_text = ", ".join([f"{k}: {v}" for k, v in bible.items()])
    if prev_page_text:
        prev_text_section = f"Previous page:\n{prev_page_text}"
    else:
        prev_text_section = "This is the first page."
    system_prompt = f"""
You are a children's book author.
Write simple and imaginative text for {age_group} year olds.
Character appearance:
{bible_text}
"""
    user_prompt = f"""
Story beat:
{beat}

{prev_text_section}

Rules:
- Write EXACTLY 4 sentences
- Each sentence MAX 8 words — strictly no longer
- Use simple words a {age_group} year old knows
- Refer to the character as {character_name}
- No long descriptions — action and feeling only
- If beat mentions creatures or magical beings, describe them 
  as clearly NON-HUMAN (tiny glowing blobs, floating stars, 
  colorful paint splashes) — NEVER as children or people

GOOD example (4 sentences, max 8 words each):
"{character_name} runs into the glowing forest smiling.
The trees twinkle with tiny golden lights.
Colorful blobs dance and spin around him.
{character_name} laughs and follows the bouncing lights."

BAD example (too long, do not do this):
"{character_name} is a little boy with curly brown hair who 
is wearing a yellow t-shirt and feeling very curious about 
the magical forest full of tall trees."
"""
    return _call(system_prompt, user_prompt, temperature=0.7)


def extract_side_characters(beat: str, main_character_name: str) -> list[str]:
    system_prompt = """
    You are a character extraction tool.
    Extract ONLY legitimate living characters or creatures (e.g., 'Dragon', 'Luna', 'Old Man') from the text.
    DO NOT extract inanimate objects, ordinary words that happen to be capitalized, or pronouns.
    Return ONLY a JSON array of strings containing the character names.
    If there are no side characters, return an empty array: []
    """
    user_prompt = f"""
    Main character (ignore this one): {main_character_name}
    Text to analyze:
    {beat}
    """
    raw = _call(system_prompt, user_prompt, temperature=0.1)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        chars = json.loads(raw)
        if isinstance(chars, list):
            return [str(c) for c in chars]
        return []
    except json.JSONDecodeError:
        return []


def extract_scene_setting(
    text: str,
    previous_settings: list[str] = None,
    page_number: int = 1
) -> str:

    avoid_block = ""
    if previous_settings:
        avoid_lines = "\n".join(f"- {s}" for s in previous_settings if s)
        avoid_block = f"\nAvoid these already-used settings:\n{avoid_lines}"

    page_hints = {
        1: "starting location — open, bright, wide, inviting",
        2: "transition — new place, threshold, path, or doorway",
        3: "discovery — magical, colorful, unique landmark",
        4: "return — warm, golden, familiar, homeward feeling",
    }
    hint = page_hints.get(page_number, "specific unique location")

    system_prompt = f"""
You are a background setting extractor for image generation.
Read the text and describe WHERE the scene takes place in 10-12 words.
Page role: {hint}

RULES:
- Extract the ACTUAL location from the text — do not invent one
- Each page must look visually different from all others
- Describe COLOR, LIGHT, and key VISUAL ELEMENTS of that specific place
- Never repeat the same dominant element (window, trees, flowers) twice
- If the story stays in one location, describe a DIFFERENT ANGLE or DETAIL each page

BAD — vague and repetitive:
- colorful room with window
- bright room with sunlight
- indoor space with light

GOOD — specific and visually distinct:
- sunlit wooden desk covered in open books and colored pencils
- narrow stone staircase with glowing lanterns on each step  
- rooftop garden at sunset, city lights beginning to twinkle
- cozy kitchen corner, warm oven glow, herbs hanging overhead
{avoid_block}
"""
    user_prompt = f"Text to analyze:\n{text}"
    raw = _call(system_prompt, user_prompt, temperature=0.6)
    return raw.strip().strip('"')


def generate_side_character_description(
    character_name: str,
    beat: str,
    art_style: str,
) -> str:
    system_prompt = f"""
You are a children's book character designer.
Given a character name and story context, describe their appearance in sentence (8-12 words max).
Focus on visual traits only: species, color, size, key clothing or features.
Art style: {art_style}
Keep it child-friendly and whimsical.
Return ONLY the description string, no quotes, no extra text.
"""
    user_prompt = f"""
Character name: {character_name}
Story context: {beat}
Write a short visual description for {character_name}.
"""
    raw = _call(system_prompt, user_prompt, temperature=0.7)
    return raw.strip().strip('"').strip("'")