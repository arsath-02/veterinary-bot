import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx
import time
from groq import Groq
from PIL import Image
import io
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Set the API key for Groq client
api_key = "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"
if not api_key:
    raise ValueError("API Key for Groq is not set in the environment variables.")

# Initialize Groq client
client = Groq(api_key=api_key)

# Initialize LangChain Memory
memory = ConversationBufferMemory()

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["species", "history", "user_query"],
    template="""
    You are a veterinary AI assistant designed to provide species-specific advice based on previous conversations.
    Species: {species}
    History: {history}
    User Query: {user_query}
    """
)

# Veterinary bot function to handle Groq response with memory
def veterinary_bot(message, species="general"):
    # Retrieve context from memory
    memory_context = memory.load_memory_variables(inputs={"user_query": message})
    prompt = prompt_template.format(
        species=species,
        history=memory_context['history'],
        user_query=message
    )
    
    # Generate response with Groq client
    result = ''
    max_retries = 3
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                stream=True,
                stop=None,
            )
            for chunk in completion:
                result += chunk.choices[0].delta.content or ""
            break
        except httpx.RemoteProtocolError as err:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return "Unable to process the request at this time. Please try again later."
        except httpx.RequestError as err:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return "There was an error reaching the server. Please check your connection and try again."

    # Update memory with user query and response
    memory.save_context({"user_query": message}, {"response": result.strip()})
    
    return result.strip()

# Endpoint for veterinary chat with species support
@app.route('/veterinary-chat', methods=['POST'])
def veterinary_chat():
    data = request.json
    user_message = data.get("message")
    species = data.get("species", "general")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    response = veterinary_bot(user_message, species=species)
    return jsonify({"response": response})

# Endpoint to handle image uploads and basic analysis
@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image = Image.open(image_file)

    # Placeholder for image analysis (future: integrate an image recognition model)
    analysis_result = "Image received. No visible analysis currently implemented."

    return jsonify({"analysis": analysis_result})

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

# Run the Flask app
if __name__ == "__main__":
    app.run(port=8000, debug=True)
