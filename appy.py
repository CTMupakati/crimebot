from flask import Flask, request, jsonify
from langchain_community.llms import DeepInfra
from langchain_core.prompts import ChatPromptTemplate
import json
from flask_cors import CORS  # Fix CORS for WordPress

app = Flask(__name__)
CORS(app)  # Allow requests from WordPress

# Load crime data
def load_crime_data():
    with open("crime_data.json") as f:
        return json.load(f)

crime_data = load_crime_data()

# Format data for the LLM
def format_data(data):
    return "\n".join([
        f"{entry['CRIME CATEGORY']} ({entry['PERIOD TYPE']}): " + 
        ", ".join([f"{year}: {entry[year]}" for year in entry if year.startswith("20")])
        for entry in data
    ])

data_str = format_data(crime_data)

# Initialize DeepInfra (free Llama 3 API)
llm = DeepInfra(model_id="meta-llama/Meta-Llama-3-70B-Instruct")
llm.api_key = "YOUR_DEEPINFRA_API_KEY"  # Get from https://deepinfra.com

# Set up the prompt
prompt = ChatPromptTemplate.from_template("""
You are a crime data assistant. Use this data:
---
{data}
---
Answer concisely. If unsure, say "Data not found."

Question: {question}
Answer:""")

chain = prompt | llm

# API endpoint
@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question")
    response = chain.invoke({"data": data_str, "question": user_question})
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # Cloud Run uses 8080