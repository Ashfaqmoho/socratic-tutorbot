from flask import Flask, request, jsonify, render_template
import ollama

app = Flask(__name__)

conversation = []

def generate_socratic_response(user_input):
    global conversation
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
        conversation.append({"role": "user", "content": user_input})
        conversation.append({"role": "assistant", "content": bot_response})
        return bot_response
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    bot_response = generate_socratic_response(user_input)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
