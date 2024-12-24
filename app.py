from flask import Flask, request, jsonify
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

with open("new_data.json", "r") as file:
    dataset = json.load(file)

conversation_data = []
for item in dataset:
    conversation_data.append(f"input: {item['input']}")
    conversation_data.append(f"output: {item['output']}")

conversation_text = "\n".join(conversation_data)

app = Flask(__name__)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 256,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_text
    user_input = request.json.get('input')

    if not user_input:
        return jsonify({"error": "Input is required"}), 400

    conversation_text += f"\ninput: {user_input}\noutput: "
    response = model.generate_content([conversation_text])
    conversation_text += response.text.strip()

    return jsonify({"response": response.text.strip()})

@app.route('/reset', methods=['POST'])
def reset_conversation():
    global conversation_text
    conversation_text = "\n".join(conversation_data)
    return jsonify({"message": "Conversation reset successfully."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)