import streamlit as st
from groq import Groq
import PyPDF2
import json
import os
import bcrypt
from dotenv import load_dotenv   # ✅ added

# 🔑 LOAD ENV FILE
load_dotenv()   # ✅ loads .env file

groq_api_key = os.getenv("GROQ_API_KEY")   # ✅ get API key

# Optional check (for debugging)
print(groq_api_key)

# 🔑 API CLIENT
client = Groq(api_key=groq_api_key)

# 📁 Files
USER_FILE = "users.json"
HISTORY_FILE = "history.json"

# 🌈 UI Styling
st.markdown("""
<style>
body {
    background-color: #E6F7FF;
    color: black;
}
.stApp {
    background-color: #E6F7FF;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🔐 FUNCTIONS
# =========================

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# =========================
# 🔐 LOGIN SYSTEM
# =========================

users = load_users()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# 👉 SHOW LOGIN ONLY IF NOT LOGGED IN
if not st.session_state["logged_in"]:

    st.title("🔐 Login / Sign Up")

    menu = st.radio("Select Option", ["Login", "Sign Up"])

    if menu == "Sign Up":
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            if new_user in users:
                st.error("User already exists ❌")
            else:
                users[new_user] = hash_password(new_pass)
                save_users(users)
                st.success("Account created ✅")

    elif menu == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users and check_password(password, users[username]):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Invalid credentials ❌")

# =========================
# 🧠 MAIN APP (ONLY AFTER LOGIN)
# =========================

else:
    st.sidebar.success(f"👋 Welcome {st.session_state['username']}")

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.title("📄 AI Resume Analyzer Pro 🚀")

    job_role = st.text_input("Enter Job Role")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if uploaded_file and job_role:
        resume_text = extract_text(uploaded_file)

        st.subheader("📃 Resume Preview")
        st.write(resume_text[:1000])

        if st.button("Analyze Resume 🚀"):

            prompt = f"""
            Analyze this resume for {job_role}

            Give output:

            **Score (out of 100):**
            **Strengths**
            **Weaknesses**
            **Suggestions**

            Resume:
            {resume_text}
            """

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.choices[0].message.content

            st.subheader("📊 Report")
            st.markdown(result)

            st.download_button("Download Report", result)