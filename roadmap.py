import streamlit as st
from openai import OpenAI
import os

my_secret = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=my_secret)

def generate_roadmap(career):
    system_prompt = """
    You are an expert career counselor and education planner. Generate a comprehensive study roadmap for the given career path.
    The roadmap should include:
    1. Key subjects or areas of study
    2. Important skills to develop
    3. Recommended courses or certifications
    4. Suggested projects or practical experience
    5. Estimated time frame for each major step

    Format the response as a numbered list with main categories and sub-points.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a study roadmap for becoming a {career}"}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

st.title("Career Study Roadmap Generator")
st.divider()

career = st.text_input("Enter the career you want to pursue:")

if 'roadmap_generated' not in st.session_state:
    st.session_state.roadmap_generated = False

if st.button("Generate Roadmap"):
    with st.spinner("Generating your career study roadmap..."):
        roadmap = generate_roadmap(career)
        st.session_state.roadmap = roadmap
        st.session_state.roadmap_generated = True

if st.session_state.roadmap_generated:
    st.subheader(f"Study Roadmap for {career}")
    st.markdown(st.session_state.roadmap)

    if st.button("Save Roadmap"):
        roadmap_filename = f"{career.replace(' ', '_').lower()}_roadmap.txt"
        with open(roadmap_filename, "w") as f:
            f.write(st.session_state.roadmap)
        st.success(f"Roadmap saved as {roadmap_filename}")

st.divider()
st.write(" ")