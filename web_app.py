import html
import streamlit as st
import app_test

st.set_page_config(
    page_title="VIDYA-RAG | Science Doubts Resolver",
    page_icon="📚",
    layout="wide",
)

# --------------------------------------------------
# PAGE DESIGN AND TEXT VISIBILITY
# --------------------------------------------------

st.markdown(
    """
    <style>
    /* Main background and default text */
    .stApp {
        background-color: #F8FAFC !important;
        color: #111827 !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #1E40AF !important;
    }

    /* Regular text */
    .stApp p,
    .stApp li,
    .stApp label,
    .stApp [data-testid="stMarkdownContainer"] p {
        color: #111827 !important;
    }

    /* Welcome banner */
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

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #E2E8F0 !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #111827 !important;
    }

    /* Navigation radio buttons */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background-color: transparent !important;
        padding: 5px;
    }

    /* Text input */
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

    /* Buttons */
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

    /* Expandable source passages */
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

    /* Radio options in revision practice */
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] p {
        color: #111827 !important;
    }

    /* Answer card */
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

    /* Alert boxes */
    [data-testid="stAlert"] p {
        color: #111827 !important;
    }

    /* Footer */
    .footer {
        color: #475569 !important;
        text-align: center;
        padding: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# LOAD TEXTBOOK PASSAGES
# --------------------------------------------------

@st.cache_resource
def get_passages():
    return app_test.load_passages()


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
        "📝 Revision Practice",
    ],
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
        unsafe_allow_html=True,
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
        "Enter a question about a topic covered in your science textbook."
    )

    with st.form("question_form"):

        question = st.text_input(
            "Your science question",
            placeholder="Example: What is dispersion of light?",
        )

        submitted = st.form_submit_button(
            "🔍 Ask VIDYA-RAG",
            use_container_width=True,
        )

    if submitted:

        if not question.strip():

            st.warning("Please enter a question first.")

        else:

            try:

                with st.spinner("Searching your science textbook..."):

                    answer, sources = app_test.select_answer(
                        question.strip(),
                        passages,
                    )

                st.divider()
                st.subheader("📝 Your Answer")

                if answer:

                    answer_text = " ".join(answer)

                    st.markdown(
                        (
                            '<div class="answer-box">'
                            '<strong>💡 Answer</strong><br><br>'
                            f'{html.escape(answer_text)}'
                            '</div>'
                        ),
                        unsafe_allow_html=True,
                    )

                else:

                    st.warning(
                        "I couldn't find a sufficiently relevant answer "
                        "in the loaded textbook. Try rephrasing your question."
                    )

                st.subheader("📚 Supporting Textbook Passages")

                if sources:

                    for index, source in enumerate(sources, start=1):

                        source_id = source.get("id", "Unknown")
                        score = source.get("score", 0)

                        source_text = app_test.clean_text(
                            source.get("text", "")
                        )

                        with st.expander(
                            f"Source {index} | Passage {source_id} "
                            f"| Relevance score: {score:.3f}"
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
        key="source_search",
    )

    matching_passages = []

    for index, passage in enumerate(passages, start=1):

        text = app_test.clean_text(
            passage.get("text", "")
        )

        if (
            not search_text.strip()
            or search_text.lower() in text.lower()
        ):

            matching_passages.append(
                (index, passage, text)
            )

    st.write(
        f"Found {len(matching_passages)} matching passage(s)."
    )

    if matching_passages:

        for index, passage, text in matching_passages:

            passage_id = passage.get("id", index)

            with st.expander(
                f"📄 Textbook Passage {passage_id}"
            ):

                if text.strip():
                    st.write(text)
                else:
                    st.caption("This passage contains no readable text.")

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
                "Shadows from trees",
            ],
            "answer": "Dispersion of sunlight by water droplets",
        },
        {
            "question": "Which part of the eye helps focus light on the retina?",
            "options": [
                "Eyelid",
                "Eye lens",
                "Eyebrow",
                "Optic nerve",
            ],
            "answer": "Eye lens",
        },
        {
            "question": "Why do stars appear to twinkle?",
            "options": [
                "They switch on and off",
                "Atmospheric refraction",
                "They change colour every second",
                "The Moon covers them",
            ],
            "answer": "Atmospheric refraction",
        },
        {
            "question": "What is dispersion of light?",
            "options": [
                "Splitting white light into its component colours",
                "Blocking all light",
                "Producing sound from light",
                "Turning light into water",
            ],
            "answer": "Splitting white light into its component colours",
        },
    ]

    with st.form("revision_form"):

        chosen_answers = {}

        for index, item in enumerate(questions):

            st.markdown(f"### Question {index + 1}")

            st.write(item["question"])

            chosen_answers[index] = st.radio(
                "Choose one answer:",
                item["options"],
                index=None,
                key=f"revision_answer_{index}",
            )

        check_answers = st.form_submit_button(
            "✅ Check My Answers",
            use_container_width=True,
        )

    if check_answers:

        score = 0
        unanswered = 0

        st.divider()
        st.subheader("📊 Your Results")

        for index, item in enumerate(questions):

            selected = chosen_answers[index]

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
            st.success("Excellent! You answered every question correctly.")

        elif unanswered > 0:

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
    unsafe_allow_html=True,
)
