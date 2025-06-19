import streamlit as st
import random
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import os
import json
import re
from auth import get_user_data, update_user_data
from scoreboard import update_user_progress

# Initialize Gemini client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# List of world languages
WORLD_LANGUAGES = [
    "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Azerbaijani",
    "Basque", "Belarusian", "Bengali", "Bosnian", "Bulgarian", "Burmese",
    "Catalan", "Cebuano", "Chinese (Mandarin)", "Chinese (Cantonese)", "Croatian", "Czech",
    "Danish", "Dutch", "English", "Esperanto", "Estonian",
    "Finnish", "French", "Galician", "Georgian", "German", "Greek", "Gujarati",
    "Haitian Creole", "Hausa", "Hawaiian", "Hebrew", "Hindi", "Hmong", "Hungarian",
    "Icelandic", "Igbo", "Indonesian", "Irish", "Italian",
    "Japanese", "Javanese", "Kannada", "Kazakh", "Khmer", "Korean", "Kurdish",
    "Kyrgyz", "Lao", "Latin", "Latvian", "Lithuanian", "Luxembourgish",
    "Macedonian", "Malagasy", "Malay", "Malayalam", "Maltese", "Maori", "Marathi", "Mongolian",
    "Nepali", "Norwegian",
    "Pashto", "Persian", "Polish", "Portuguese", "Punjabi",
    "Romanian", "Russian",
    "Samoan", "Scots Gaelic", "Serbian", "Sesotho", "Shona", "Sindhi", "Sinhala", "Slovak",
    "Slovenian", "Somali", "Spanish", "Sundanese", "Swahili", "Swedish",
    "Tajik", "Tamil", "Telugu", "Thai", "Turkish",
    "Ukrainian", "Urdu", "Uzbek",
    "Vietnamese",
    "Welsh",
    "Xhosa",
    "Yiddish", "Yoruba",
    "Zulu"
]

def parse_quiz_data(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    questions = []
    current_question = {}
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith("Question:"):
            if current_question:
                questions.append(current_question)
            current_question = {"question": line.split("Question:")[1].strip()}
        elif line.startswith("Correct answer:"):
            current_question["answer"] = line.split("Correct answer:")[1].strip()
        elif line.startswith("Explanation:"):
            current_question["explanation"] = line.split("Explanation:")[1].strip()
        elif line.startswith("Choices:"):
            choices_text = line.split("Choices:")[1].strip()
            choices = re.findall(r'\b[A-D]\)\s*([^\,]+)(?:,|$)', choices_text)
            current_question["choices"] = choices
        elif line.startswith("Clue:"):
            current_question["clue"] = line.split("Clue:")[1].strip()

    if current_question:
        questions.append(current_question)

    return questions

def create_quiz_prompt(native_language, target_language, topic, num_questions, difficulty):
    return f"""Generate a {difficulty} level quiz for learning {target_language} on the topic of {topic}. 
    The questions should be in {native_language}, except for the specific {target_language} words or phrases being asked about.
    Include {num_questions} questions with a mix of the following types:
    1. Multiple choice
    2. Fill in the blank
    3. Translation
    For each question, provide:
    - The question (in {native_language}, with {target_language} words as needed)
    - The correct answer (in {target_language})
    - A detailed explanation of the answer (in {native_language}), including:
      * Why the answer is correct
      * Common mistakes learners might make
      * Additional context or related language points
    - For multiple choice questions, include 4 choices labeled A, B, C, D (in {target_language})
    - For fill-in-the-blank questions:
      * For Easy difficulty: Present a short sentence with one blank word to fill in
      * For Medium difficulty: Present a longer sentence or two short sentences with one or two blanks to fill in
      * For Hard difficulty: Present a longer sentences with multiple blanks to fill in 
      * The blank(s) should be word(s) or phrase(s) in {target_language}
      * Represent blanks with '___' (triple underscore)
      * Provide a clue for the blank(s) in {native_language}
      * Do not include the answer(s) anywhere in the question text
    Format each question as follows:
    Question: [question text]
    Choices: A) [choice A], B) [choice B], C) [choice C], D) [choice D] (for multiple choice only)
    Clue: [clue in {native_language}] (for fill-in-the-blank only)
    Correct answer: [correct answer]
    Explanation: [detailed explanation]"""

def validate_question(question):
    if not isinstance(question, dict):
        return False
    if 'question' not in question or 'answer' not in question:
        return False
    if "_" in question['question']:  # This is a fill-in-the-blank question
        answer = question['answer'].lower()
        question_text = question['question'].lower()
        # Check if the answer appears in the question text
        if answer in question_text.replace('_', ''):
            return False
    return True

def generate_quiz(native_language, target_language, topic, num_questions, difficulty):
    prompt = create_quiz_prompt(native_language, target_language, topic, num_questions, difficulty)

    while True:
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=1.3,
                    max_output_tokens=4000,
                )
            )

            quiz_data = parse_quiz_data(response.text)

            # Validate each question
            valid_questions = [q for q in quiz_data if validate_question(q)]

            if len(valid_questions) >= num_questions:
                return valid_questions[:num_questions]
            else:
                print(f"Generated {len(valid_questions)} valid questions out of {num_questions} requested. Retrying...")
        except Exception as e:
            print(f"An error occurred: {str(e)}. Retrying...")

def check_answer(user_answer, correct_answer):
    if isinstance(user_answer, list):
        return all(ua.lower().strip() == ca.lower().strip() for ua, ca in zip(user_answer, correct_answer.split(',')))
    return user_answer.lower().strip() == correct_answer.lower().strip()

def generate_hint(question, target_language):
    prompt = f"""Provide a helpful hint for the following {target_language} language learning question:
    "{question}"
    The hint should guide the learner towards the answer without giving it away completely."""

    response = model.generate_content(prompt)
    return response.text.strip()

def load_css():
    with open("styles.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def adjust_difficulty(current_difficulty, accuracy):
    if accuracy > 0.8:
        return "Hard" if current_difficulty == "Medium" else "Medium"
    elif accuracy < 0.5:
        return "Easy" if current_difficulty == "Medium" else "Medium"
    return current_difficulty

def initialize_session_state():
    if 'quiz' not in st.session_state:
        st.session_state.quiz = None
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'current_hint' not in st.session_state:
        st.session_state.current_hint = None

def main():
    load_css()
    initialize_session_state()

    st.header("Language Learning Quiz")

    # Quiz generation form
    native_language = st.selectbox("Choose your native language", WORLD_LANGUAGES, key="native_lang")
    target_language = st.selectbox("Choose the language you want to learn", WORLD_LANGUAGES, key="target_lang")
    topic = st.text_input("Enter a topic", key="quiz_topic")
    num_questions = st.slider("Number of questions", 5, 20, 10, key="num_questions")
    difficulty = st.selectbox("Choose difficulty", ["Easy", "Medium", "Hard"], key="difficulty")

    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz... This may take a moment."):
            try:
                quiz_data = generate_quiz(native_language, target_language, topic, num_questions, difficulty)
                if quiz_data:
                    st.session_state.quiz = quiz_data
                    st.session_state.user_answers = {}
                    st.session_state.quiz_submitted = False

                    # Update user progress for successfully generating a quiz
                    user_data = get_user_data(st.session_state.user)
                    user_data["experience"] += 5  # Award 5 XP for generating a quiz
                    user_data["completed_quizzes"] += 1
                    update_user_data(st.session_state.user, user_data)
                    st.success("Quiz generated successfully!")
            except Exception as e:
                st.error(f"An unexpected error occurred while generating the quiz: {str(e)}")

                # Update user progress even if an error occurs
                user_data = get_user_data(st.session_state.user)
                user_data["experience"] += 1  # Award 1 XP for the attempt
                update_user_data(st.session_state.user, user_data)

    # Quiz display and interaction
    if st.session_state.quiz is not None:
        st.subheader("Quiz")
        for i, question in enumerate(st.session_state.quiz):
            st.write(f"Question {i + 1}")
            st.write(question['question'])

            if "choices" in question:
                user_answer = st.radio(f"Choose the correct answer for Question {i + 1}:",
                                       question['choices'],
                                       key=f"q{i}")
            elif "clue" in question:  # This is a fill-in-the-blank question
                st.write(f"Clue: {question['clue']}")
                blanks = question['question'].count('___')
                if blanks == 1:
                    user_answer = st.text_input(f"Fill in the blank for Question {i + 1}:", key=f"q{i}")
                else:
                    user_answer = [st.text_input(f"Blank {j+1} for Question {i + 1}:", key=f"q{i}_{j}") for j in range(blanks)]
            else:
                user_answer = st.text_input(f"Your answer for Question {i + 1}:", key=f"q{i}")

            st.session_state.user_answers[i] = user_answer

        if st.button("Submit Quiz"):
            st.session_state.quiz_submitted = True

    # Add the hint chatbox
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        st.subheader("Hint Assistant")
        if st.session_state.quiz is not None:
            hint_question = st.selectbox("Select a question for a hint:",
                                         [f"Question {i+1}" for i in range(len(st.session_state.quiz))])
            if st.button("Get Hint"):
                question_index = int(hint_question.split()[-1]) - 1
                question = st.session_state.quiz[question_index]['question']
                st.session_state.current_hint = generate_hint(question, target_language)

            if st.session_state.current_hint:
                st.write(st.session_state.current_hint)
        st.markdown('</div></div>', unsafe_allow_html=True)

    # Quiz results
    if st.session_state.quiz_submitted:
        st.subheader("Quiz Results")
        correct_answers = 0
        for i, question in enumerate(st.session_state.quiz):
            st.write(f"Question {i + 1}")
            st.write(question['question'])
            user_answer = st.session_state.user_answers.get(i, "")
            correct_answer = question['answer']

            if check_answer(user_answer, correct_answer):
                st.success("Correct!")
                correct_answers += 1
            else:
                st.error("Incorrect")

            st.write(f"Your answer: {user_answer}")
            st.write(f"Correct answer: {correct_answer}")
            st.write("Explanation:")
            st.write(question['explanation'])
            st.write("---")

        score = correct_answers / len(st.session_state.quiz)
        st.write(f"Your score: {correct_answers}/{len(st.session_state.quiz)}")

        # Update user progress
        update_user_progress(st.session_state.user, correct_answers, len(st.session_state.quiz))

        new_difficulty = adjust_difficulty(difficulty, score)

        if st.button("Return"):
            st.session_state.quiz = None
            st.session_state.user_answers = {}
            st.session_state.quiz_submitted = False

if __name__ == "__main__":
    main()