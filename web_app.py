import html
import re

import streamlit as st
from pypdf import PdfReader
import app_test


st.set_page_config(
    page_title="VIDYA-RAG | Science Doubts Resolver",
    page_icon="📚",
    layout="wide",
)


# --------------------------------------------------
# PAGE STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F8FAFC !important;
        color: #111827 !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #1E40AF !important;
    }

    .stApp p,
    .stApp li,
    .stApp label,
    .stApp [data-testid="stMarkdownContainer"] p {
        color: #111827 !important;
    }

    .hero {
        background-color: #DBEAFE !important;
        padding: 28px;
        border-radius: 16px;
        border: 1px solid #BFDBFE;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: #1E3A8A !important;
        font-size: 2.3rem;
    }

    .hero p {
        color: #111827 !important;
        font-size: 1.05rem;
        line-height: 1.7;
    }

    [data-testid="stSidebar"] {
        background-color: #E2E8F0 !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #111827 !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background-color: transparent !important;
        padding: 5px;
    }

    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #64748B !important;
        border-radius: 8px !important;
    }

    .stTextInput input::placeholder {
        color: #64748B !important;
        opacity: 1 !important;
    }

    .stButton button,
    .stFormSubmitButton button {
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    .stButton button p,
    .stFormSubmitButton button p {
        color: #FFFFFF !important;
    }

    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: #1E3A8A !important;
    }

    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
        color: #111827 !important;
    }

    [data-testid="stRadio"] label,
    [data-testid="stRadio"] p {
        color: #111827 !important;
    }

    .answer-box {
        background-color: #DBEAFE !important;
        color: #111827 !important;
        padding: 20px;
        border-left: 5px solid #2563EB;
        border-radius: 10px;
        line-height: 1.8;
        overflow-wrap: anywhere;
    }

    .answer-box p,
    .answer-box span {
        color: #111827 !important;
    }

    [data-testid="stAlert"] p {
        color: #111827 !important;
    }

    .footer {
        color: #475569 !important;
        text-align: center;
        padding: 15px;
    }

    /* LIGHT BLUE PDF UPLOAD AREA */

    [data-testid="stFileUploader"] section {
        background-color: #EAF4FF !important;
        border: 2px dashed #3B82F6 !important;
        border-radius: 12px !important;
    }

    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section * {
        color: #1E3A8A !important;
    }

    /* PDF BROWSE BUTTON */

    [data-testid="stFileUploader"] button {
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    [data-testid="stFileUploader"] button * {
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# LOAD ORIGINAL TEXTBOOK
# --------------------------------------------------

@st.cache_resource
def get_passages():
    return app_test.load_passages()


# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------

def extract_pdf_passages(uploaded_file):
    """Extract readable text from each page of an uploaded PDF."""

    reader = PdfReader(uploaded_file)
    result = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            result.append({
                "id": page_number,
                "text": text.strip()
            })

    return result


# --------------------------------------------------
# SEARCH UPLOADED PDF
# --------------------------------------------------

def search_pdf(question, pdf_passages):
    """Find PDF pages that best match the question keywords."""

    stop_words = {
        "the", "is", "are", "a", "an", "of", "in", "on",
        "to", "and", "what", "why", "how", "does", "do",
        "explain", "describe", "for", "with", "it", "which",
        "this", "that", "from", "by", "can", "be", "was",
        "were", "about"
    }

    terms = {
        word
        for word in re.findall(r"[a-z0-9]+", question.lower())
        if len(word) > 1 and word not in stop_words
    }

    if not terms:
        return []

    results = []

    for passage in pdf_passages:
        words = set(
            re.findall(r"[a-z0-9]+", passage["text"].lower())
        )

        matches = terms.intersection(words)

        if matches:
            results.append({
                "id": passage["id"],
                "text": passage["text"],
                "score": len(matches) / len(terms),
                "matched": len(matches)
            })

    results.sort(
        key=lambda item: (item["score"], item["matched"]),
        reverse=True
    )

    return results[:3]


# --------------------------------------------------
# LOAD TEXTBOOK DATA
# --------------------------------------------------

try:
    passages = get_passages()

    if not passages:
        st.error(
            "No textbook passages were found. "
            "Please check data/textbooks/embeddings.json."
        )
        st.stop()

except Exception as error:
    st.error("The textbook passages could not be loaded.")
    st.exception(error)
    st.stop()


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("📚 VIDYA-RAG")
st.sidebar.caption("Your Science Doubts Resolver")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate to a page:",
    [
        "🏠 Home",
        "🔎 Ask a Question",
        "📖 Textbook Sources",
        "📝 Revision Practice"
    ]
)

st.sidebar.divider()

st.sidebar.success(
    f"{len(passages)} textbook passages loaded"
)

st.sidebar.caption(
    "Explore your science textbook and practise concepts."
)


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if page == "🏠 Home":

    st.markdown(
        """
        <div class="hero">
            <h1>📚 Welcome to VIDYA-RAG</h1>
            <p><strong>Your Science Doubts Resolver</strong></p>
            <p>
                Have a science question? Search your textbook,
                explore supporting passages, and practise
                important science concepts.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Explore VIDYA-RAG")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            "**🔎 Ask a Question**\n\n"
            "Ask science questions and find relevant textbook information."
        )

    with col2:
        st.info(
            "**📖 Textbook Sources**\n\n"
            "Browse and search the loaded textbook passages."
        )

    with col3:
        st.info(
            "**📝 Revision Practice**\n\n"
            "Answer practice questions and check your score."
        )

    st.divider()

    st.subheader("How to use the website")

    st.write("1. Select **Ask a Question** in the sidebar.")
    st.write("2. Enter a science question.")
    st.write("3. Read the answer and supporting passages.")
    st.write("4. Visit Textbook Sources to explore the material.")
    st.write("5. Use Revision Practice to test your understanding.")


# --------------------------------------------------
# ASK A QUESTION PAGE
# --------------------------------------------------

elif page == "🔎 Ask a Question":

    st.title("🔎 Ask a Science Question")

    st.write(
        "Ask about your loaded textbook or upload a PDF "
        "to search its readable text."
    )

    # PDF UPLOAD WIDGET
    uploaded_pdf = st.file_uploader(
        "📄 Upload a science textbook PDF (optional)",
        type=["pdf"],
        help=(
            "PDFs must contain selectable text. "
            "Scanned image-only PDFs may need OCR."
        ),
        key="science_pdf_upload"
    )

    pdf_passages = None

    if uploaded_pdf is not None:

        try:
            with st.spinner("Reading your PDF..."):
                pdf_passages = extract_pdf_passages(uploaded_pdf)

            if pdf_passages:
                st.success(
                    f"PDF loaded! Readable text found on "
                    f"{len(pdf_passages)} page(s)."
                )
            else:
                st.warning(
                    "No selectable text was found. This may be "
                    "a scanned PDF; OCR is not included yet."
                )

        except Exception as error:
            st.error(
                "I couldn't read this PDF. Please try another PDF file."
            )
            st.caption(str(error))

    # SELECT SEARCH SOURCE
    source_choice = st.radio(
        "Where should VIDYA-RAG search?",
        [
            "Original science textbook",
            "Uploaded PDF"
        ],
        horizontal=True,
        key="question_source_choice"
    )

    # QUESTION FORM
    with st.form("question_form"):

        question = st.text_input(
            "Your science question",
            placeholder="Example: What is dispersion of light?"
        )

        submitted = st.form_submit_button(
            "🔍 Ask VIDYA-RAG",
            use_container_width=True
        )

    # PROCESS QUESTION
    if submitted:

        if not question.strip():

            st.warning("Please enter a question first.")

        elif source_choice == "Uploaded PDF" and uploaded_pdf is None:

            st.warning(
                "Please upload a PDF first, or choose the original textbook."
            )

        elif source_choice == "Uploaded PDF" and not pdf_passages:

            st.warning(
                "There is no readable text to search in this PDF."
            )

        else:

            try:
                with st.spinner("Searching your selected source..."):

                    if source_choice == "Uploaded PDF":

                        sources = search_pdf(
                            question.strip(),
                            pdf_passages
                        )

                        answer = []

                        if sources:

                            sentences = re.split(
                                r"(?<=[.!?])\s+",
                                sources[0]["text"]
                            )

                            terms = {
                                word
                                for word in re.findall(
                                    r"[a-z0-9]+",
                                    question.lower()
                                )
                                if len(word) > 2
                            }

                            ranked = sorted(
                                enumerate(sentences),
                                key=lambda item: (
                                    len(
                                        terms.intersection(
                                            set(
                                                re.findall(
                                                    r"[a-z0-9]+",
                                                    item[1].lower()
                                                )
                                            )
                                        )
                                    ),
                                    -item[0]
                                ),
                                reverse=True
                            )

                            answer = [
                                sentence.strip()
                                for _, sentence in ranked[:3]
                                if sentence.strip()
                            ]

                    else:

                        answer, sources = app_test.select_answer(
                            question.strip(),
                            passages
                        )

                st.divider()
                st.subheader("📝 Your Answer")

                if answer:

                    if source_choice == "Uploaded PDF":
                        label = "Relevant text from your PDF"
                    else:
                        label = "Answer"

                    answer_html = (
                        '<div class="answer-box">'
                        '<strong>💡 '
                        + label
                        + '</strong><br><br>'
                        + html.escape(" ".join(answer))
                        + '</div>'
                    )

                    st.markdown(
                        answer_html,
                        unsafe_allow_html=True
                    )

                    if source_choice == "Uploaded PDF":
                        st.caption(
                            "These are excerpts found in your PDF, "
                            "not a newly generated explanation."
                        )

                else:

                    st.warning(
                        "I couldn't find a sufficiently relevant answer "
                        "in the selected source. Try rephrasing your question."
                    )

                st.subheader("📚 Supporting Source Passages")

                if sources:

                    for index, source in enumerate(sources, start=1):

                        source_id = source.get("id", "Unknown")
                        score = source.get("score", 0)

                        if source_choice == "Uploaded PDF":
                            source_text = source.get("text", "")
                            title = f"PDF page {source_id}"
                        else:
                            source_text = app_test.clean_text(
                                source.get("text", "")
                            )
                            title = f"Textbook passage {source_id}"

                        with st.expander(
                            f"Source {index} | {title} | "
                            f"Relevance: {score:.3f}"
                        ):
                            st.write(source_text)

                else:

                    st.info(
                        "No supporting source passages were returned."
                    )

            except Exception as error:

                st.error(
                    "Something went wrong while answering your question."
                )
                st.exception(error)


# --------------------------------------------------
# TEXTBOOK SOURCES PAGE
# --------------------------------------------------

elif page == "📖 Textbook Sources":

    st.title("📖 Textbook Sources")

    st.write(
        "Browse the science textbook passages loaded into VIDYA-RAG."
    )

    search_text = st.text_input(
        "Search textbook passages",
        placeholder="Enter a keyword, such as light or eye...",
        key="source_search"
    )

    matching = []

    for index, passage in enumerate(passages, start=1):

        text = app_test.clean_text(
            passage.get("text", "")
        )

        if (
            not search_text.strip()
            or search_text.lower() in text.lower()
        ):
            matching.append((index, passage, text))

    st.write(
        f"Found {len(matching)} matching passage(s)."
    )

    if matching:

        for index, passage, text in matching:

            passage_id = passage.get("id", index)

            with st.expander(
                f"📄 Textbook Passage {passage_id}"
            ):

                if text.strip():
                    st.write(text)
                else:
                    st.caption(
                        "This passage contains no readable text."
                    )

    else:

        st.warning(
            "No matching passages found. Try a different keyword."
        )


# --------------------------------------------------
# REVISION PRACTICE PAGE
# --------------------------------------------------

elif page == "📝 Revision Practice":

    st.title("📝 Science Revision Practice")

    st.write(
        "Answer the questions below and check your results."
    )

    questions = [
        {
            "question": "What causes a rainbow to form?",
            "options": [
                "Dispersion of sunlight by water droplets",
                "Sound waves in the air",
                "Movement of the Moon",
                "Shadows from trees"
            ],
            "answer": "Dispersion of sunlight by water droplets"
        },
        {
            "question": (
                "Which part of the eye helps focus light on the retina?"
            ),
            "options": [
                "Eyelid",
                "Eye lens",
                "Eyebrow",
                "Optic nerve"
            ],
            "answer": "Eye lens"
        },
        {
            "question": "Why do stars appear to twinkle?",
            "options": [
                "They switch on and off",
                "Atmospheric refraction",
                "They change colour every second",
                "The Moon covers them"
            ],
            "answer": "Atmospheric refraction"
        },
        {
            "question": "What is dispersion of light?",
            "options": [
                "Splitting white light into its component colours",
                "Blocking all light",
                "Producing sound from light",
                "Turning light into water"
            ],
            "answer": (
                "Splitting white light into its component colours"
            )
        }
    ]

    with st.form("revision_form"):

        chosen = {}

        for index, item in enumerate(questions):

            st.markdown(
                f"### Question {index + 1}"
            )

            st.write(item["question"])

            chosen[index] = st.radio(
                "Choose one answer:",
                item["options"],
                index=None,
                key=f"revision_answer_{index}"
            )

        check = st.form_submit_button(
            "✅ Check My Answers",
            use_container_width=True
        )

    if check:

        score = 0
        unanswered = 0

        st.divider()
        st.subheader("📊 Your Results")

        for index, item in enumerate(questions):

            selected = chosen[index]

            if selected is None:

                unanswered += 1
                st.warning(
                    f"Question {index + 1}: Not answered."
                )

            elif selected == item["answer"]:

                score += 1
                st.success(
                    f"Question {index + 1}: Correct!"
                )

            else:

                st.error(
                    f"Question {index + 1}: Incorrect. "
                    f"Correct answer: {item['answer']}"
                )

        st.markdown(
            f"## Your score: {score}/{len(questions)}"
        )

        if score == len(questions):

            st.balloons()

            st.success(
                "Excellent! You answered every question correctly."
            )

        elif unanswered:

            st.info(
                "Try answering the remaining questions and practise again."
            )

        else:

            st.info(
                "Review the textbook passages and try again."
            )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <div class="footer">
        <strong>VIDYA-RAG</strong> · Science Doubts Resolver<br>
        Helping students explore science, one question at a time.
    </div>
    """,
    unsafe_allow_html=True
)