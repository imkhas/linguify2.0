import streamlit as st

st.title('This is a title')

st.write('This is a **text**')

st.button('Reset', type ="primary")
if st.button('Say Hello'):
  st.write("Why hello there")
else:
  st.write("Goodbye")