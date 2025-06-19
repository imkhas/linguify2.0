import streamlit as st
from openai import OpenAI
import os
import pandas as pd
import json
import re

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_lesson_data(content):
    """Parse the lesson data from the API response."""
    # Try to extract a JSON-like structure from the content
    match = re.search(r'\[.*\]', content, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            return data
        except json.JSONDecodeError:
            pass

    # If JSON parsing fails, fallback to manual parsing
    rows = []
    current_row = {}
    for line in content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            current_row[key] = value
        elif line.strip() == '' and current_row:
            rows.append(current_row)
            current_row = {}
    if current_row:
        rows.append(current_row)
    return rows

def generate_lesson(topic, target_language, native_language):
    """Generate a lesson on a given topic in a format suitable for table display."""
    prompt = f"""Create a short lesson about {topic} in {target_language} with translations to {native_language}. 
    Format the output as a list of dictionaries, where each dictionary represents a row with the following keys:
    - Vocabulary: the term in {target_language}
    - Vocabulary_Translation: the term in {native_language}
    - Grammar_Points: grammar explanation in {target_language}
    - Grammar_Translation: grammar explanation in {native_language}
    - Cultural_Insights: cultural information in {target_language}
    - Cultural_Translation: cultural information in {native_language}

    Provide at least 10 rows  and maximum of 20 of content."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a knowledgeable language teacher. Respond with a list of dictionaries containing the lesson information."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content
    lesson_data = parse_lesson_data(content)
    return lesson_data

def generate_exercise(topic, target_language, exercise_type):
    """Generate an exercise based on the topic and exercise type."""
    prompt = f"Create a {exercise_type} exercise about {topic} in {target_language}. Include instructions and the correct answer."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a creative language exercise creator."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def teaching_assistant_tab():
    # List of world languages
    languages = [
        "English", "Spanish", "French", "German", "Italian", "Portuguese",
        "Russian", "Japanese", "Korean", "Chinese", "Arabic", "Hindi",
        "Turkish", "Dutch", "Swedish", "Polish", "Greek", "Thai",
        "Vietnamese", "Indonesian", "Malay", "Filipino", "Ukrainian",
        "Czech", "Romanian", "Hungarian", "Finnish", "Danish", "Norwegian"
    ]

    # Reordered form
    native_language = st.selectbox("Select your native language:", languages)
    target_language = st.selectbox("Select the language you're learning:", languages)
    topic = st.text_input("Enter a topic you want to learn about:")

    if st.button("Generate Lesson"):
        with st.spinner("Generating lesson..."):
            lesson_data = generate_lesson(topic, target_language, native_language)

            if lesson_data:
                # Create a DataFrame from the lesson data
                df = pd.DataFrame(lesson_data)

                # Display the table
                st.subheader(f"Lesson on {topic} in {target_language}")
                st.table(df)
            else:
                st.error("Failed to generate lesson. Please try again.")

    exercise_type = st.selectbox("Choose an exercise type:", ["Vocabulary", "Grammar", "Reading Comprehension"])
    if st.button("Generate Exercise"):
        with st.spinner("Generating exercise..."):
            exercise = generate_exercise(topic, target_language, exercise_type)
            st.markdown(exercise)

    st.markdown("---")
    st.subheader("Chat with Teaching Assistant")
    user_question = st.text_input("Ask a question about language learning:")
    if st.button("Ask"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful language learning assistant."},
                    {"role": "user", "content": user_question}
                ]
            )
            st.markdown(response.choices[0].message.content)

# Main app
def main():
    st.set_page_config(page_title="Language Learning Assistant", layout="wide")
    teaching_assistant_tab()

if __name__ == "__main__":
    main()