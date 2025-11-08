import streamlit as st
import google.generativeai as genai
import PyPDF2
from collections import Counter
import re

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
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    counter = Counter(words)
    return counter.most_common(top_n)

# Initial essay analysis
def analyze_essay(essay_text):
    top_words = word_frequency_analysis(essay_text)
    freq_table = "\n".join([f"{w}: {c}" for w, c in top_words])

    prompt = f"""
    You are a writing analysis assistant. Analyze the following essay:

    1. Concise summary (2–3 sentences)
    2. Sentence-final expressions — analyze how sentences end and what patterns exist
    3. Frequently used words — confirm the ones below
       Word Frequency (top 10):
       {freq_table}
    4. Writing quality — comment on organization, vocabulary, coherence, grammar
    5. Areas for improvement — constructive suggestions
    6. Overall evaluation — score 1–10

    Essay:
    {essay_text}
    """
    response = model.generate_content(prompt)
    return response.text

# Follow-up Q&A
def answer_question(essay_text, user_question):
    prompt = f"""
    You are an assistant who only uses the information in the essay below.
    Essay:
    {essay_text}

    Question: {user_question}

    Answer concisely and accurately based only on the essay.
    """
    response = model.generate_content(prompt)
    return response.text

# Streamlit UI
st.title("Essay Analysis Chatbot")
uploaded_file = st.file_uploader("Upload your essay (PDF)", type="pdf")

if uploaded_file:
    essay_text = extract_text_from_pdf(uploaded_file)
    st.subheader("Essay Text (Preview)")
    st.text(essay_text[:500] + "...\n")

    # Initial analysis
    if st.button("Analyze Essay"):
        with st.spinner("Analyzing essay..."):
            analysis_results = analyze_essay(essay_text)
            st.subheader("Analysis Results")
            st.text(analysis_results)

        # Store essay text for follow-up questions
        st.session_state['essay_text'] = essay_text

# Follow-up Q&A
if 'essay_text' in st.session_state:
    st.subheader("Ask Questions About the Essay")
    user_question = st.text_input("Enter your question:")
    if user_question:
        with st.spinner("Getting answer..."):
            answer = answer_question(st.session_state['essay_text'], user_question)
            st.text(answer)
