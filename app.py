import streamlit as st
import sqlite3
import base64
import datetime

# Initialize session state variables
if "user" not in st.session_state:
    st.session_state.user = None

# Database initialization
def init_db():
    conn = sqlite3.connect("dynabot_messenger.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    user TEXT,
                    message TEXT,
                    timestamp TEXT)''')
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("dynabot_messenger.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def register_user(username, password):
    conn = sqlite3.connect("dynabot_messenger.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def add_message(user, message):
    conn = sqlite3.connect("dynabot_messenger.db")
    c = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO messages (user, message, timestamp) VALUES (?, ?, ?)", (user, message, timestamp))
    conn.commit()
    conn.close()

def get_messages():
    conn = sqlite3.connect("dynabot_messenger.db")
    c = conn.cursor()
    c.execute("SELECT * FROM messages ORDER BY id")
    messages = c.fetchall()
    conn.close()
    return messages

def delete_message(message_id):
    conn = sqlite3.connect("dynabot_messenger.db")
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# UI Styling
st.set_page_config(page_title="Dynabot Industries Messenger", layout="centered")
st.markdown(
    """
    <style>
    .stApp {
        background-color: #121212;
        color: #f1c40f;
    }
    .stButton button {
        background-color: #f1c40f;
        color: #121212;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App Logic
if st.session_state.user is None:
    st.title("Dynabot Industries Messenger")
    st.subheader("Login or Sign Up")

    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_user(username, password)
            if user:
                st.session_state.user = username
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")

    with signup_tab:
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if register_user(new_username, new_password):
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Username already exists.")
else:
    st.title("Welcome to Dynabot Industries Messenger")
    st.subheader(f"Logged in as: {st.session_state.user}")
    if st.button("Log Out"):
        st.session_state.user = None
        st.experimental_rerun()

    st.write("---")
    st.subheader("Chat Room")

    # Display messages
    messages = get_messages()
    for message in messages:
        user, text, timestamp, message_id = message[1], message[2], message[3], message[0]
        st.markdown(f"**{user}**: {text} *({timestamp})*")
        if user == st.session_state.user:
            if st.button(f"Remove", key=f"remove_{message_id}"):
                delete_message(message_id)
                st.experimental_rerun()

    st.write("---")
    # Send a message
    message_text = st.text_area("Type a message", key="new_message")
    if st.button("Send Message"):
        if message_text:
            add_message(st.session_state.user, message_text)
            st.experimental_rerun()
        else:
            st.warning("Message cannot be empty!")

    # Add Emojis
    st.write("😀 😁 😂 🤔 ❤️")

    st.write("---")
    st.subheader("Image Sharing (Paste Image)")
    uploaded_file = st.file_uploader("Upload an image")
    if uploaded_file is not None:
        st.image(uploaded_file)
        add_message(st.session_state.user, f"Shared an image: {uploaded_file.name}")


