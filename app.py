from flask import Flask, request, jsonify
import os
import json
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# load environment variables
load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
API_URL = os.environ["TEAMS_API_URL"]

response = requests.get(API_URL)
if response.status_code != 200:
    raise Exception("Failed to fetch team data from the API.")

team_data = response.json().get("data", [])

# load data from new_data.json
with open("new_data.json", "r") as file:
    new_data = json.load(file)

# prepare structured conversation data
conversation_data = []

# append data from API response
for i in range(len(team_data)):
    name = team_data[i].get('name')
    access = team_data[i].get('access')
    if team_data[i].get('extra') is not None:
        if access == 'ALUMNI':
            designation = 'Previous' + team_data[i].get('extra').get('designation', "No Designation")
        else:
            designation = team_data[i].get('extra').get('designation', "No Designation")
    else:
        continue
    conversation_data.append(f"input: {name}")
    conversation_data.append(f"output: {access}, {designation}")

# append data from new_data.json
for item in new_data:
    input_text = item.get("input", "Unknown Input")
    output_text = item.get("output", "Unknown Output")
    conversation_data.append(f"input: {input_text}")
    conversation_data.append(f"output: {output_text}")

# join all conversation data
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
    # reload conversation data from API and new_data.json dynamically
    response = requests.get(API_URL)
    if response.status_code == 200:
        team_data = response.json().get("data", [])
        global conversation_data
        conversation_data = []

        # append data from API response
        for i in range(len(team_data)):
            name = team_data[i].get('name')
            access = team_data[i].get('access')
            if team_data[i].get('extra') is not None:
                designation = team_data[i].get('extra').get('designation', "No Designation")
            else:
                continue
            conversation_data.append(f"input: {name}")
            conversation_data.append(f"output: {access}, {designation}")

        # append data from new_data.json
        with open("new_data.json", "r") as file:
            new_data = json.load(file)
        for item in new_data:
            input_text = item.get("input", "Unknown Input")
            output_text = item.get("output", "Unknown Output")
            conversation_data.append(f"input: {input_text}")
            conversation_data.append(f"output: {output_text}")

        conversation_text = "\n".join(conversation_data)
        return jsonify({"message": "Conversation reset successfully."})
    else:
        return jsonify({"error": "Failed to reset data from the API"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)