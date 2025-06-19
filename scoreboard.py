import streamlit as st
import pandas as pd
from auth import users, get_user_data, update_user_data

def display_scoreboard():
    st.subheader("Scoreboard")

    # Prepare data for the table
    data = []
    for username, user_data in users.items():
        data.append({
            "Username": username,
            "Experience": user_data['experience'],
            "Quizzes Completed": user_data['completed_quizzes']
        })

    # Create DataFrame and sort by Experience
    df = pd.DataFrame(data)
    df = df.sort_values(by="Experience", ascending=False).reset_index(drop=True)

    # Add ranking
    df.insert(0, "Rank", df.index + 1)

    # Display the table without the index and with full width
    st.dataframe(df.head(10), hide_index=True, use_container_width=True)

# The update_user_progress function remains unchanged
def update_user_progress(username, correct_answers, total_questions):
    user_data = get_user_data(username)
    if user_data:
        accuracy = correct_answers / total_questions
        user_data["experience"] += correct_answers * 10
        user_data["streak"] += 1 if accuracy >= 0.7 else 0
        user_data["completed_quizzes"] += 1
        if user_data["experience"] >= 100:
            user_data["level"] += 1
            user_data["experience"] -= 100
        update_user_data(username, user_data)