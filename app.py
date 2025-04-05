from flask import Flask, request, jsonify, render_template, session
from flask_session import Session  # For server-side session storage
import ollama

app = Flask(__name__)

# Secret key for session management (generate a random one for production)
app.secret_key = "84649c28b633da5ebd0cc9e56d541692"

# Configure server-side session storage (filesystem-based for simplicity)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def generate_socratic_response(user_input, user_session):
    # Get or initialize conversation for this user from session
    conversation = user_session.get("conversation", [])
    
    messages = [
        {
            "role": "system",
            "content": "You are a Socratic tutor. Ask ONE concise question per turn. "
                       "Do NOT explain, answer, or monologue. Reference prior answers."
        },
        *conversation,
        {"role": "user", "content": user_input}
    ]

    try:
        response = ollama.chat(
            model="qwen2.5:7b",
            messages=messages,
            options={"temperature": 0.2}
        )
        bot_response = response["message"]["content"].strip()
        # Update conversation history
        conversation.append({"role": "user", "content": user_input})
        conversation.append({"role": "assistant", "content": bot_response})
        # Save back to session
        user_session["conversation"] = conversation
        return bot_response
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/")
def home():
    # Optionally clear session on page load for a fresh start
    # session.clear()  # Uncomment if you want each visit to reset the chat
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    bot_response = generate_socratic_response(user_input, session)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)