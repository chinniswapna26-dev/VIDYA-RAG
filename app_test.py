import json
import math
import re
from pathlib import Path
from collections import Counter


# ==================================================
# SETTINGS
# ==================================================

BASE_DIR = Path(__file__).parent

EMBEDDINGS_FILE = BASE_DIR / "data" / "textbooks" / "embeddings.json"
SAMPLE_FILE = BASE_DIR / "data" / "textbooks" / "sample_passages.json"

MAX_ANSWER_SENTENCES = 3
MIN_PASSAGE_SCORE = 0.12


# ==================================================
# TOPIC KEYWORDS
# ==================================================

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "be", "been", "being", "do", "does", "did",
    "how", "what", "why", "when", "where", "who",
    "which", "explain", "describe", "tell", "me",
    "of", "to", "in", "on", "at", "for", "from",
    "by", "with", "and", "or", "but", "it", "its",
    "this", "that", "these", "those", "we", "you",
    "your", "their", "they", "our", "can", "could",
    "would", "should", "function", "please", "about",
    "give", "define", "into", "called", "mean"
}


TOPIC_TERMS = {
    "rainbow": {
        "rainbow", "spectrum", "sunlight", "water",
        "droplets", "dispersion", "prism", "prisms",
        "refract", "refracted", "reflection", "reflect",
        "raindrop", "colours", "colors", "internally"
    },
    "twinkle": {
        "star", "stars", "twinkle", "twinkling",
        "atmosphere", "atmospheric", "refraction",
        "rays", "light", "apparent", "position",
        "flickers", "brighter", "fainter", "starlight"
    },
    "eye_lens": {
        "eye", "lens", "retina", "image", "light",
        "focus", "focused", "focal", "distance",
        "crystalline", "cornea", "forms", "formation",
        "accommodation", "ciliary", "muscles",
        "near", "distant", "vision", "eyeball",
        "presbyopia", "myopia", "hypermetropia"
    },
    "photosynthesis": {
        "photosynthesis", "plants", "plant", "sunlight",
        "chlorophyll", "water", "carbon", "dioxide",
        "glucose", "food", "leaves"
    },
    "gravity": {
        "gravity", "gravitational", "force", "earth",
        "attraction", "mass", "objects"
    },
    "evaporation": {
        "evaporation", "evaporate", "liquid", "water",
        "vapour", "vapor", "heat", "temperature"
    },
    "refraction": {
        "refraction", "refract", "light", "medium",
        "bends", "bending", "speed"
    },
    "dispersion": {
        "dispersion", "splitting", "white", "light",
        "component", "colours", "colors", "spectrum",
        "prism"
    }
}


# ==================================================
# TEXT PROCESSING
# ==================================================

def tokenize(text):
    return re.findall(r"[a-zA-Z]+", text.lower())


def get_keywords(text):
    return {
        word for word in tokenize(text)
        if word not in STOP_WORDS and len(word) > 1
    }


def build_vector(text):
    return dict(Counter(tokenize(text)))


def cosine_similarity(vector_a, vector_b):
    if not vector_a or not vector_b:
        return 0.0

    common = set(vector_a) & set(vector_b)

    dot_product = sum(
        vector_a[word] * vector_b[word]
        for word in common
    )

    magnitude_a = math.sqrt(
        sum(value * value for value in vector_a.values())
    )

    magnitude_b = math.sqrt(
        sum(value * value for value in vector_b.values())
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def clean_text(text):
    text = re.sub(
        r"\bReprint\s+20\d{2}-\d{2}\b",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\b(?:Figure|Fig\.?)\s*\d+(?:\.\d+)?",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r"\(\s*\)", " ", text)

    text = re.sub(
        r"/square\d+",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\b(?:Rainbow in the sky|Rainbow formation|"
        r"Sunlight Raindrop|Dispersion of white light by the glass prism|"
        r"Recombination of the spectrum of white light)\b",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_sentences(text):
    text = clean_text(text)

    text = re.sub(r"\bFig\.", "Fig", text)
    text = re.sub(r"\bMr\.", "Mr", text)
    text = re.sub(r"\bDr\.", "Dr", text)

    parts = re.split(r"(?<=[.!?])\s+", text)

    sentences = []

    for part in parts:
        sentence = part.strip(" \t\r\n-–")

        sentence = re.sub(
            r"\(\s*(?:Fig\.?\s*)?\d*\.?\s*\)",
            "",
            sentence,
            flags=re.IGNORECASE
        ).strip()

        if sentence:
            sentences.append(sentence)

    return sentences


# ==================================================
# QUESTION CLASSIFICATION
# ==================================================

def detect_topic(question):
    q = question.lower()
    words = set(tokenize(q))

    if "rainbow" in words:
        return "rainbow"

    if "twinkle" in words or "twinkling" in words:
        return "twinkle"

    # Recognize eye-related questions even when "lens"
    # is not explicitly included in the question.
    eye_terms = {
        "eye", "lens", "retina", "cornea", "accommodation",
        "presbyopia", "myopia", "hypermetropia", "eyeball",
        "vision", "ciliary"
    }

    if words & eye_terms:
        return "eye_lens"

    if "photosynthesis" in words or "chlorophyll" in words:
        return "photosynthesis"

    if "gravity" in words or "gravitational" in words:
        return "gravity"

    if "evaporation" in words or "evaporate" in words:
        return "evaporation"

    if "dispersion" in words:
        return "dispersion"

    if "refraction" in words or "refract" in words:
        return "refraction"

    return None


def is_definition_question(question):
    q = question.lower().strip()

    patterns = (
        r"^what is ",
        r"^what are ",
        r"^define ",
        r"^give the meaning of ",
        r"^what do you mean by "
    )

    return any(re.search(pattern, q) for pattern in patterns)


def expand_keywords(question):
    words = get_keywords(question)
    topic = detect_topic(question)

    if topic:
        words.update(TOPIC_TERMS[topic])

    return words


# ==================================================
# PASSAGE RELEVANCE
# ==================================================

def score_passage(question, passage_text):
    question_words = expand_keywords(question)
    passage_words = get_keywords(passage_text)

    if not passage_words or not question_words:
        return 0.0

    overlap = (
        len(question_words & passage_words)
        / max(len(question_words), 1)
    )

    similarity = cosine_similarity(
        build_vector(" ".join(question_words)),
        build_vector(passage_text)
    )

    score = overlap * 0.75 + similarity * 0.25

    topic = detect_topic(question)
    lower_text = passage_text.lower()

    if topic:
        matches = sum(
            1 for word in TOPIC_TERMS[topic]
            if word in passage_words
        )

        score += min(matches * 0.008, 0.08)

    required_terms = {
        "rainbow": ("rainbow",),
        "twinkle": ("twinkle", "twinkling", "starlight"),
        "eye_lens": (
            "lens", "retina", "focal length", "accommodation",
            "cornea", "eyeball", "ciliary muscles", "presbyopia"
        ),
        "photosynthesis": (
            "photosynthesis", "chlorophyll", "carbon dioxide"
        ),
        "gravity": ("gravity", "gravitational"),
        "evaporation": ("evaporation", "evaporate"),
        "dispersion": ("dispersion", "splitting"),
        "refraction": ("refraction", "refract")
    }

    if topic in required_terms:
        if not any(
            term in lower_text
            for term in required_terms[topic]
        ):
            score *= 0.20

    if topic and topic.replace("_", " ") in lower_text:
        score += 0.10

    return score


# ==================================================
# SENTENCE FILTERING
# ==================================================

def is_bad_sentence(sentence):
    text = sentence.strip()
    lower = text.lower()

    if len(text.split()) < 6:
        return True

    if "?" in text:
        return True

    bad_starts = (
        "chapter ", "exercise ", "activity ", "example ",
        "questions ", "question ", "contents ", "index "
    )

    if lower.startswith(bad_starts):
        return True

    if lower.count("figure") >= 2 or "reprint" in lower:
        return True

    if sum(character.isalpha() for character in text) < 15:
        return True

    if re.match(
        r"^(?:fig(?:ure)?\.?\s*\d+|activity\s+\d+|"
        r"chapter\s+\d+)",
        lower
    ):
        return True

    return False


def sentence_matches_topic(topic, sentence):
    """Return True when a sentence is relevant to the requested topic."""

    lower = sentence.lower()

    if topic == "photosynthesis":
        return (
            "photosynthesis" in lower
            or "chlorophyll" in lower
            or "glucose" in lower
            or (
                "carbon dioxide" in lower
                and (
                    "plant" in lower
                    or "plants" in lower
                    or "sunlight" in lower
                    or "photosynthesis" in lower
                )
            )
        )

    if topic == "rainbow":
        return any(
            term in lower
            for term in (
                "rainbow", "dispersion of sunlight",
                "water droplets", "prism"
            )
        )

    if topic == "twinkle":
        return any(
            term in lower
            for term in (
                "twinkle", "twinkling", "starlight",
                "apparent position of the star"
            )
        )

    if topic == "eye_lens":
        return any(
            term in lower
            for term in (
                "lens", "retina", "focal length",
                "accommodation", "cornea", "ciliary muscles",
                "presbyopia", "myopia", "hypermetropia",
                "eyeball", "near point", "far point",
                "power of accommodation", "vision"
            )
        )

    if topic == "gravity":
        return "gravity" in lower or "gravitational" in lower

    if topic == "evaporation":
        return "evaporation" in lower or "evaporate" in lower

    if topic == "dispersion":
        return "dispersion" in lower or "splitting" in lower

    if topic == "refraction":
        return "refraction" in lower or "refract" in lower

    return True


# ==================================================
# SENTENCE SCORING
# ==================================================

def score_sentence(question, sentence, passage_score):
    if is_bad_sentence(sentence):
        return -1.0

    topic = detect_topic(question)

    if topic and not sentence_matches_topic(topic, sentence):
        return -1.0

    question_words = expand_keywords(question)
    sentence_words = get_keywords(sentence)

    overlap = (
        len(question_words & sentence_words)
        / max(len(question_words), 1)
    )

    score = overlap + passage_score * 0.20

    word_count = len(sentence.split())

    if 9 <= word_count <= 35:
        score += 0.06

    lower = sentence.lower()
    question_lower = question.lower()

    # Give direct definitions priority for definition questions.
    if is_definition_question(question):
        if topic == "eye_lens":
            definition_patterns = (
                "ability of the eye lens to adjust its focal length",
                "ability of the eye lens to adjust",
                "called accommodation",
            )

            if (
                "accommodation" in question_lower
                and any(pattern in lower for pattern in definition_patterns)
            ):
                score += 2.0

            if (
                "retina" in question_lower
                and "retina" in lower
                and any(
                    term in lower
                    for term in ("image", "light-sensitive", "light sensitive")
                )
            ):
                score += 0.60

            if (
                "cornea" in question_lower
                and "cornea" in lower
                and "refraction" in lower
            ):
                score += 0.60

        if topic == "rainbow" and "rainbow" in lower:
            score += 0.40

        if topic == "twinkle" and (
            "twinkling effect" in lower
            or "twinkle" in lower
        ):
            score += 0.40

        if topic == "photosynthesis" and (
            "photosynthesis" in lower
            and ("process" in lower or "plants" in lower)
        ):
            score += 0.60

    if topic == "rainbow":
        if "dispersion of sunlight" in lower:
            score += 0.60
        if "water droplets" in lower:
            score += 0.35
        if "refract" in lower:
            score += 0.20
        if "reflect" in lower:
            score += 0.20
        if "different colours" in lower or "different colors" in lower:
            score += 0.20

    elif topic == "twinkle":
        if "twinkling effect" in lower:
            score += 0.70
        if "apparent position of the star" in lower:
            score += 0.30
        if "starlight" in lower:
            score += 0.20
        if "atmosphere" in lower:
            score += 0.15

    elif topic == "eye_lens":
        if "ability of the eye lens to adjust its focal length" in lower:
            score += 1.50
        if "called accommodation" in lower:
            score += 0.50
        if "forms an image" in lower:
            score += 0.60
        if "retina" in lower:
            score += 0.20
        if "focal length" in lower:
            score += 0.30
        if "focus objects" in lower:
            score += 0.30
        if "inverted real image" in lower:
            score += 0.25

    elif topic == "dispersion":
        if (
            "splitting of white light into its component colours"
            in lower
            or "splitting of white light into its component colors"
            in lower
        ):
            score += 1.20
        elif (
            "splitting of light into its component colours"
            in lower
            or "splitting of light into its component colors"
            in lower
        ):
            score += 1.00
        elif "dispersion of white light" in lower:
            score += 0.45

    return score


# ==================================================
# ANSWER SELECTION
# ==================================================

def select_answer(question, passages):
    topic = detect_topic(question)
    definition_question = is_definition_question(question)

    ranked_passages = []

    for passage in passages:
        score = score_passage(question, passage["text"])

        ranked_passages.append({
            "id": passage["id"],
            "text": passage["text"],
            "score": score
        })

    ranked_passages.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    if not ranked_passages:
        return [], []

    if ranked_passages[0]["score"] < MIN_PASSAGE_SCORE:
        return [], []

    candidate_passages = [
        passage for passage in ranked_passages[:12]
        if passage["score"] >= MIN_PASSAGE_SCORE
    ]

    candidates = []

    for passage in candidate_passages:
        for sentence in split_sentences(passage["text"]):
            score = score_sentence(
                question,
                sentence,
                passage["score"]
            )

            if score <= 0:
                continue

            candidates.append({
                "sentence": sentence,
                "score": score,
                "passage_id": passage["id"],
                "passage_score": passage["score"]
            })

    if topic == "dispersion" and definition_question:
        for candidate in candidates:
            lower = candidate["sentence"].lower()

            if (
                "splitting of white light into its component colours"
                in lower
                or "splitting of white light into its component colors"
                in lower
                or "splitting of light into its component colours"
                in lower
                or "splitting of light into its component colors"
                in lower
            ):
                candidate["score"] += 2.0

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    selected = []
    seen = set()

    for candidate in candidates:
        sentence = candidate["sentence"]

        normalized = re.sub(
            r"\W+", " ", sentence.lower()
        ).strip()

        if normalized in seen:
            continue

        lower = sentence.lower()

        if topic == "rainbow" and any(
            term in lower
            for term in ("lens system", "human eye", "stars twinkle")
        ):
            continue

        if topic == "twinkle" and any(
            term in lower for term in ("planet", "planets")
        ):
            continue

        if topic == "eye_lens" and any(
            term in lower for term in ("rainbow", "water droplets")
        ):
            continue

        if topic and not sentence_matches_topic(topic, sentence):
            continue

        words = set(get_keywords(sentence))
        duplicate = False

        for previous in selected:
            previous_words = set(
                get_keywords(previous["sentence"])
            )

            union = words | previous_words

            if union:
                similarity = len(words & previous_words) / len(union)

                if similarity > 0.75:
                    duplicate = True
                    break

        if duplicate:
            continue

        selected.append(candidate)
        seen.add(normalized)

        limit = (
            1
            if definition_question
            else MAX_ANSWER_SENTENCES
        )

        if len(selected) >= limit:
            break

    answer = [
        item["sentence"] for item in selected
    ]

    sources_by_id = {
        passage["id"]: passage
        for passage in ranked_passages
    }

    relevant_sources = []
    source_ids = []

    # Prefer sources that actually contributed to the answer.
    for item in selected:
        passage_id = item["passage_id"]

        if passage_id not in source_ids:
            source_ids.append(passage_id)

    for source_id in source_ids:
        source = sources_by_id.get(source_id)

        if source and source["score"] >= MIN_PASSAGE_SCORE:
            relevant_sources.append(source)

    # Add other relevant passages only when needed.
    for passage in ranked_passages:
        if len(relevant_sources) >= 3:
            break

        if passage["score"] < MIN_PASSAGE_SCORE:
            continue

        if passage["id"] not in {
            source["id"] for source in relevant_sources
        }:
            relevant_sources.append(passage)

    return answer, relevant_sources[:3]


# ==================================================
# LOAD TEXTBOOK PASSAGES
# ==================================================

def read_passages(file_path):
    """Read and normalize passages from a JSON file."""

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not load {file_path.name}: {error}")
        return []

    if isinstance(data, list):
        items = data

    elif isinstance(data, dict):
        items = None

        for key in ("passages", "chunks", "documents", "data"):
            if isinstance(data.get(key), list):
                items = data[key]
                break

        if items is None:
            items = list(data.values())

    else:
        return []

    passages = []

    for index, item in enumerate(items, start=1):
        if isinstance(item, str):
            text = item
            passage_id = index

        elif isinstance(item, dict):
            text = None

            for key in ("text", "content", "passage", "chunk"):
                if isinstance(item.get(key), str):
                    text = item[key]
                    break

            if text is None:
                continue

            passage_id = item.get("id", index)

        else:
            continue

        text = clean_text(text)

        if text:
            passages.append({
                "id": passage_id,
                "text": text
            })

    return passages


def load_passages():
    """
    Load full textbook passages when available.
    Otherwise, fall back to sample science passages.

    Local computer:
        Uses embeddings.json when available.

    Streamlit Cloud:
        Uses sample_passages.json when embeddings.json is absent.
    """

    passages = read_passages(EMBEDDINGS_FILE)

    if passages:
        print("\nFull textbook passages loaded successfully!")
        print("Available passages:", len(passages))
        return passages

    print("\nFull textbook embeddings are unavailable.")
    print("Trying sample science passages...")

    passages = read_passages(SAMPLE_FILE)

    if passages:
        print("\nSample science passages loaded successfully!")
        print("Available passages:", len(passages))
        return passages

    print("\nERROR: No passages could be loaded.")
    print("Checked:", EMBEDDINGS_FILE)
    print("Checked:", SAMPLE_FILE)

    return []


# ==================================================
# MAIN APPLICATION
# ==================================================

def main():
    print("=" * 55)
    print("VIDYA-RAG: SCIENCE DOUBTS RESOLVER")
    print("=" * 55)

    passages = load_passages()

    if not passages:
        print("\nNo textbook passages were loaded.")
        return

    print("Type 'exit' to close the application.")

    while True:
        try:
            question = input("\nYour question: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nVIDYA-RAG closed.")
            break

        if question.lower() in ("exit", "quit"):
            print("VIDYA-RAG closed.")
            break

        if not question:
            print("Please enter a question.")
            continue

        answer, sources = select_answer(question, passages)

        print("\n" + "=" * 55)
        print("ANSWER")
        print("=" * 55)

        if answer:
            for sentence in answer:
                print(sentence)
        else:
            print(
                "Sorry, I couldn't find a sufficiently relevant "
                "answer in the loaded science textbook. "
                "Try rephrasing your question or check whether "
                "the topic is included in your textbook."
            )

        print("\n" + "-" * 55)
        print("SOURCE PASSAGES")
        print("-" * 55)

        if not sources:
            print("No sufficiently relevant source passages found.")

        for index, source in enumerate(sources, start=1):
            preview = clean_text(source["text"])

            if len(preview) > 600:
                preview = preview[:600].rsplit(" ", 1)[0] + "..."

            print(
                f"\nSource {index} "
                f"(Passage {source['id']}, "
                f"score: {source['score']:.3f})"
            )

            print(preview)
            print("-" * 40)


if __name__ == "__main__":
    main()
