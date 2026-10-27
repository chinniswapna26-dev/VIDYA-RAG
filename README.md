# VIDYA-RAG – Science Doubts Resolver

## About the Project
VIDYA-RAG is a science question-answering application designed to help students find information from a science textbook. It retrieves relevant textbook passages and displays answers along with supporting source passages.

## Features
- Ask science questions through a web interface.
- Retrieve relevant information from textbook passages.
- View supporting textbook sources.
- Search textbook passages by keyword.
- Practise science concepts using a revision quiz.
- View quiz scores and feedback.

## Technologies Used
- Python
- Streamlit
- PyMuPDF and PDF-processing tools
- Sentence Transformers and FAISS, if used by the project's retrieval pipeline
- JSON for storing processed textbook passages

## Project Structure
```text
VIDYA-RAG/
├── data/
│   └── textbooks/
│       ├── science.pdf
│       └── embeddings.json
├── app_test.py
├── web_app.py
├── read_pdf.py
├── chunk_text.py
├── create_embeddings.py
├── requirements.txt
└── README.md
```

## How to Run the Project

1. Install Python.
2. Open the project folder in VS Code.
3. Activate the project's virtual environment.
4. Install the required packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Start the website:

   ```bash
   python -m streamlit run web_app.py
   ```

6. Open the local address displayed in the terminal, usually `http://localhost:8501`.

## How to Use
1. Open the Home page.
2. Select **Ask a Question** to ask a science question.
3. Open **Textbook Sources** to search and read passages.
4. Open **Revision Practice** to answer quiz questions.
5. Review your quiz score and feedback.

## Current Limitations
- Answers depend on the textbook passages available to the application.
- The question-answering component may not answer every question correctly.
- Revision Practice currently uses sample questions.
- The retrieval and answer-generation methods depend on the implementation in `app_test.py`.

## Future Improvements
- Improve the relevance of retrieved passages.
- Add more textbooks and subjects.
- Expand the revision question bank.
- Improve answer accuracy and evaluation.

## Author
Student Project