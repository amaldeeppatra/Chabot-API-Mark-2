from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Load data from new_data.json
with open("new_data.json", "r") as file:
    new_data = json.load(file)

# Prepare structured conversation data
conversation_data = []
for item in new_data:
    input_text = item.get("input", "Unknown Input")
    output_text = item.get("output", "Unknown Output")
    conversation_data.append(f"input: {input_text}")
    conversation_data.append(f"output: {output_text}")

# Join all conversation data
conversation_text = "\n".join(conversation_data)

app = Flask(__name__)
CORS(app)

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
    
    # Reload data from new_data.json
    with open("new_data.json", "r") as file:
        new_data = json.load(file)
    
    conversation_data = []
    for item in new_data:
        input_text = item.get("input", "Unknown Input")
        output_text = item.get("output", "Unknown Output")
        conversation_data.append(f"input: {input_text}")
        conversation_data.append(f"output: {output_text}")
    
    conversation_text = "\n".join(conversation_data)
    return jsonify({"message": "Conversation reset successfully."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
