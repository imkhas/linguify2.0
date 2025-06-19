import streamlit as st
from auth import sign_up, sign_in, sign_out, get_user_data, update_user_data
from scoreboard import display_scoreboard
from teaching_assistant import teaching_assistant_tab
from quiz import main as quiz_main

# Set page configuration at the very beginning
st.set_page_config(page_title="Linguify", page_icon="🌍", layout="wide")

# Custom CSS for background and subtle buttons
page_bg_color = '''
    <style>
    body {
        background-color: #11558c;
    }
    .stApp {
        background-color: #11558c;
    }
    .stTextInput input {
        background-color: white;
        color: black;
    }
    </style>
'''

def main():
    # Apply the custom CSS
    st.markdown(page_bg_color, unsafe_allow_html=True)

    # Create two columns for the logo
    col1, col2 = st.columns([1, 3])

    # Place the image in the first column
    with col1:
        st.image("Linguify-Blue-logo latest.png", use_column_width="auto") 

    # Check if user is in session state
    if "user" not in st.session_state:
        st.session_state.user = None

    if not st.session_state.user:
        # Sign In and Sign Up tabs
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        with tab1:
            username = sign_in()
            if username:
                st.session_state.user = username
                st.success("Signed in successfully!")
                st.rerun()
        with tab2:
            if sign_up():
                st.success("Account created successfully! Please sign in.")
    else:
        # Move the navigation to the sidebar
        st.sidebar.title("Navigation")

        # Create selectable pages in the sidebar
        app_mode = st.sidebar.selectbox("Select page:", ["Quiz", "Teaching Assistant", "Scoreboard"])

        # Display user info and sign out button in the sidebar
        st.sidebar.write(f"Welcome, {st.session_state.user}!")
        if st.sidebar.button("Sign Out"):
            sign_out()
            st.rerun()

        # Main content area
        if app_mode == "Quiz":
            st.title("Quiz")
            quiz_main()
        elif app_mode == "Teaching Assistant":
            st.title("Teaching Assistant")
            teaching_assistant_tab()
        elif app_mode == "Scoreboard":
            st.title("Scoreboard")
            display_scoreboard()

if __name__ == "__main__":
    main()