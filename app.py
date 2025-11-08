import streamlit as st
import google.generativeai as genai
import PyPDF2
from collections import Counter

# Configure Gemini
from config import GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro")

# PDF extraction
def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

# Frequency analysis
def word_frequency_analysis(text, top_n=10):
    # Simple approach: split on spaces, remove punctuation manually
    text = text.lower()
    for ch in ".,!?;:()\"'-":
        text = text.replace(ch, "")
    words = text.split()
    counter = Counter(words)
    return counter.most_common(top_n)

# Initial essay analysis
def analyze_essay(essay_text):
    top_words = word_frequency_analysis(essay_text)
    freq_table = "\n".join([f"{w}: {c}" for w, c in top_words])

    prompt = f"""
    Analyze the following essay:

    1. Concise summary (4-5 sentences)
    2. Sentence-final expressions — analyze how sentences end and what patterns exist
    3. Frequently used words — confirm the ones below
       Word Frequency (top 10):
       {freq_table}
    4. Writing quality — comment on organization, vocabulary, coherence, grammar
    5. Areas for improvement — constructive suggestions
    6. Overall evaluation — score 0-100

    Essay:
    {essay_text}
    """
    response = model.generate_content(prompt)
    return response.text

# Follow-up Q&A
def answer_question(essay_text, user_question):
    prompt = f"""
    Essay:
    {essay_text}

    Question: {user_question}

    Answer concisely and accurately based only on the essay.
    """
    response = model.generate_content(prompt)
    return response.text

# Streamlit UI
st.subheader("Choose essay input method:")
input_method = st.radio("Select one:", ["Upload PDF", "Copy & Paste Text"])

essay_text = ""

# Input section
if input_method == "Upload PDF":
    uploaded_file = st.file_uploader("Upload your essay (PDF)", type="pdf")
    if uploaded_file:
        from PyPDF2 import PdfReader
        reader = PdfReader(uploaded_file)
        essay_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                essay_text += page_text + "\n"
elif input_method == "Copy & Paste Text":
    essay_text = st.text_area("Paste your essay here", height=300)

# Preview essay text
if essay_text:
    st.subheader("Essay Text Preview")
    st.text(essay_text[:500] + ("..." if len(essay_text) > 500 else ""))

# Show the button **after** the essay text area or PDF upload
if essay_text and st.button("Analyze Essay"):
    with st.spinner("Analyzing essay..."):
        analysis_results = analyze_essay(essay_text)  # Your existing function
        st.subheader("Analysis Results")
        st.text(analysis_results)
        # Save to session for Q&A
        st.session_state['essay_text'] = essay_text
