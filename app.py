import streamlit as st
import sqlite3
import time

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

def login(username, password):
    conn = sqlite3.connect("dynabot_messenger.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def signup(username, password):
    conn = sqlite3.connect("dynabot_messenger.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def check_login():
    if st.session_state.user is None:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            user = login(username, password)
            if user:
                st.session_state.user = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials, please try again.")
        
        if st.button("Sign Up"):
            signup(username, password)
            st.success("Account created successfully! Please log in.")

def show_chat():
    # Function to retrieve and show messages from database
    conn = sqlite3.connect("dynabot_messenger.db")
    c = conn.cursor()
    c.execute("SELECT * FROM messages ORDER BY timestamp DESC")
    messages = c.fetchall()
    conn.close()

    for message in messages:
        user, text, image, timestamp = message
        st.write(f"{user}: {text} - {timestamp}")
        if image:
            st.image(image)

def add_message(user, text, image=None):
    conn = sqlite3.connect("dynabot_messenger.db")
    c = conn.cursor()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO messages (user, message, image, timestamp) VALUES (?, ?, ?, ?)", 
              (user, text, image, timestamp))
    conn.commit()
    conn.close()

# Main app flow
if st.session_state.user is None:
    check_login()
else:
    st.write(f"Welcome, {st.session_state.user}")
    
    # Message input
    message_text = st.text_area("Type a message", key="new_message")
    image_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"], key="image_upload")
    
    if st.button("Send Message"):
        if message_text or image_file:
            if image_file:
                # Convert image to binary (BLOB)
                image_data = image_file.read()
                add_message(st.session_state.user, message_text, image=image_data)
            else:
                add_message(st.session_state.user, message_text)
            st.experimental_rerun()
        else:
            st.warning("Message cannot be empty!")

    show_chat()

    # Real-time message update (Simple example using rerun)
    st.text("Messages will update automatically every 10 seconds.")
    time.sleep(10)
    st.experimental_rerun()
