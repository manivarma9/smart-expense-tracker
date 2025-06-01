import streamlit as st

def login_app():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if st.session_state.logged_in:
        st.markdown(f"### 👋 Welcome, **{st.session_state.username}**!")
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.experimental_rerun()
    else:
        st.markdown("<h1 style='color: #4CAF50;'>🔐 Login</h1>", unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login"):
            if username == "mani" and password == "mani123":
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("✅ Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("❌ Invalid username or password")
