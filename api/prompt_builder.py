# api/prompt_builder.py

ART_STYLES = {
    "watercolor": (
        "Soft watercolor children's book illustration, "
        "gentle brushstrokes, warm pastel palette, "
        "whimsical and dreamlike quality"
    ),
    "pencil_sketch": (
        "Pencil sketch children's book illustration, "
        "fine ink outlines, light watercolor wash, "
        "classic storybook feel like Quentin Blake"
    ),
    "flat_vector": (
        "Flat vector children's book illustration, "
        "bold clean outlines, bright solid colors, "
        "modern and playful like a picture book app"
    ),
    "oil_painting": (
        "Oil painting children's book illustration, "
        "rich textures, warm earthy tones, "
        "classic fairy tale storybook aesthetic"
    ),
    "anime": (
        "anime illustration, sharp detailed line art, "
        "dynamic composition, vibrant saturated colors, "
        "cel shaded lighting, detailed character design, "
        "professional anime key visual style"
    ),
}

NEGATIVE_PROMPT_BASE = (
    "ugly, deformed, blurry, text, watermark, "
    "realistic photo, violence, "
    "repetitive background, same location, "
    "character from behind, tiny distant figure, "
    "dress, gown, apron, overalls, "
    "teenager, adult,"
)

NEGATIVE_PROMPT_MONO = (
    f"{NEGATIVE_PROMPT_BASE}anime, cartoon, cel shading, "
)

MOOD_KEYWORDS = {
    "dark": "soft shadows, moonlight",
    "scary": "gentle mysterious, warm moonlight",
    "lost": "soft blue tones",
    "happy": "bright warm sunlight",
    "sad": "muted blue-grey tones",
    "excited": "bright vibrant colors",
    "magical": "glowing light, sparkles",
    "forest": "dappled sunlight, green tones",
    "night": "soft moonlight, deep blue sky",
    "morning": "golden sunrise, dewy",
    "underwater": "blue-green light",
    "flying": "bright open sky",
    "home": "warm indoor lighting",
    "garden": "soft natural daylight",
}

DEFAULT_MOOD = "warm inviting light"

AGE_SOFTENING = {
    "4-6": "gentle, safe, comforting",
    "6-8": "gentle, age-appropriate, warm",
    "8-12": "mildly adventurous, child-appropriate",
}


def _format_side_character(bible: dict, name: str) -> str:
    if not bible:
        return (
            f"({name}, positioned separately beside main character, "
            f"NOT a human, NOT a child:1.4)"
        )

    desc = bible.get("description", "").strip()
    if not desc:
        desc = ", ".join(v for v in bible.values() if v)

    if desc:
        desc = desc.split(".")[0].strip()
        return (
            f"({name}, {desc}, "
            f"clearly a {name} NOT a human, NOT a child, "
            f"positioned separately beside main character:1.6)"
        )

    return (
        f"({name}, "
        f"clearly a {name} NOT a human, NOT a child, "
        f"positioned separately beside main character:1.6)"
    )


def _bible_to_string(bible: dict, character_name: str) -> str:
    if not bible:
        return character_name
    description = ", ".join(v for v in bible.values() if v)
    return f"{character_name}: {description}"


def _extract_mood(beat: str, age_group: str) -> str:
    beat_lower = beat.lower()
    softening = AGE_SOFTENING.get(age_group, AGE_SOFTENING["6-8"])

    for keyword, mood in MOOD_KEYWORDS.items():
        if keyword in beat_lower:
            return f"{mood}, {softening}"

    return f"{DEFAULT_MOOD}, {softening}"


def _scene_from_text(page_text: str, beat: str) -> str:
    if page_text and page_text.strip():
        return page_text.strip()

    if isinstance(beat, dict):
        beat = beat.get("beat", "")
    elif isinstance(beat, str) and beat.startswith("{") and "'beat':" in beat:
        try:
            import ast
            parsed = ast.literal_eval(beat)
            if isinstance(parsed, dict):
                beat = parsed.get("beat", "")
        except:
            pass

    return beat


def build_image_prompt(
    page_text: str,
    beat: str,
    art_style: str,
    age_group: str,
    main_character_name: str,
    main_character_bible: dict,
    scene_setting: str,
    side_characters_on_page: list[dict] = None,
) -> str:

    style = ART_STYLES.get(art_style, ART_STYLES["watercolor"])
    main_char_desc = _bible_to_string(main_character_bible, main_character_name)

    side_char_descs = []
    if side_characters_on_page:
        for char in side_characters_on_page:
            side_char_descs.append(
                _format_side_character(
                    char.get("bible", {}),
                    char.get("name", "character")
                )
            )

    side_chars_text = ", ".join(side_char_descs) if side_char_descs else ""

    scene = _scene_from_text(page_text, beat)
    mood = _extract_mood(beat, age_group)

    negative_prompt = (
        NEGATIVE_PROMPT_BASE
        if art_style == "anime"
        else NEGATIVE_PROMPT_MONO
    )

    parts = [
        "COMPOSITION: child and animal companion both visible and facing viewer, "
        "child large in foreground, animal beside child."
        if side_chars_text else
        "COMPOSITION: full body child facing viewer, large in foreground, NOT from behind, NOT tiny.",

        style,

        f"WITH: {side_chars_text}." if side_chars_text else "",

        f"SCENE SETTING: ({scene_setting}:1.5).",
        f"MAIN ACTION: {scene}.",
        f"MAIN CHARACTER: {main_char_desc}.",
        f"Mood and lighting: {mood}.",
        f"Negative: {negative_prompt}",
    ]

    return " ".join(p for p in parts if p.strip())


def build_side_character_prompt(
    character_name: str,
    art_style: str,
    brief_description: str,
) -> str:

    style = ART_STYLES.get(art_style, ART_STYLES["watercolor"])

    return (
        f"{style}. "
        f"Character: {character_name}, {brief_description}. "
        f"Friendly, child-appropriate. "
        f"Negative: {NEGATIVE_PROMPT_BASE}"
    )