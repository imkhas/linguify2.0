import streamlit as st

# User data storage
users = {}

def sign_up():
    st.subheader("Sign Up")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Create Account"):
        if username and password:
            if username not in users:
                users[username] = {
                    "password": password,
                    "level": 1,
                    "experience": 0,
                    "streak": 0,
                    "completed_quizzes": 0,
                    "weak_areas": []
                }
                return True
            else:
                st.error("Username already exists.")
        else:
            st.error("Please enter both username and password.")
    return False

def sign_in():
    st.subheader("Sign In")
    username = st.text_input("Username", key="signin_username")
    password = st.text_input("Password", type="password", key="signin_password")
    if st.button("Sign In"):
        if username in users and users[username]["password"] == password:
            return username
        else:
            st.error("Invalid username or password.")
    return None

def sign_out():
    st.session_state.user = None

def get_user_data(username):
    return users.get(username, None)

def update_user_data(username, data):
    if username in users:
        users[username].update(data)