from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx
import time
import torch
from efficientnet_lite_pytorch import EfficientNet
import ngrok
from torchvision import transforms
from groq import Groq
from PIL import Image
import os
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langdetect import detect

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Set the API key for Groq client
api_key = "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"
if not api_key:
    raise ValueError("API Key for Groq is not set in the environment variables.")

# Initialize Groq client
client = Groq(api_key=api_key)

# Initialize Ngrok
ngrok.set_auth_token("2a1iGE4Q5SDAF4mhdAVXeNptwJd_2GBcW2ACMaj2JoAJy8Gtt")
listener = ngrok.forward(
    "127.0.0.1:5000", authtoken_from_env=True, domain="apparent-wolf-obviously.ngrok-free.app"
)

# Initialize LangChain Memory
memory = ConversationBufferMemory()

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["species", "history", "user_query", "language"],
    template="""
    You are a veterinary AI assistant designed to provide species-specific advice based on previous conversations.
    Species: {species}
    History: {history}
    User Query: {user_query}
    Language: {language}
    
    Provide the response in the same language as the user query.
    Additionally, address the following queries if they are relevant:
    - Is the pet vaccinated?
    - Does the pet have any known allergies?
    - Has the pet had any recent medical issues or treatments?
    - Are there any behavioral changes in the pet?
    - Is the pet on any medication or special diet?
    """
)

# Load EfficientNet-Lite0 model
efficientnet_model = EfficientNet.from_name('efficientnet-lite0')
efficientnet_model.eval()

# Define image preprocessing pipeline for EfficientNet-Lite0
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def veterinary_bot(message, species="general", image_analysis=None):
    """Process user message and image analysis using Groq client."""
    language = detect(message) if message else "en"  # Detect language only if there's text input

    # Load conversation memory
    memory_context = memory.load_memory_variables(inputs={"user_query": message or "Image analysis only"})

    # Build prompt with image analysis if provided
    prompt = prompt_template.format(
        species=species,
        history=memory_context.get('history', ''),
        user_query=message or "Image analysis only",
        language=language
    )
    if image_analysis:
        prompt += f"\nImage Analysis: {image_analysis}"

    result = ''
    max_retries = 3
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False,
            )
            result = completion.choices[0].message.content
            break
        except (httpx.RemoteProtocolError, httpx.RequestError) as err:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return "Unable to process the request at this time. Please try again later."

    if result.strip():
        memory.save_context({"user_query": message or "Image analysis only"}, {"response": result.strip()})
    return result.strip()

@app.route('/veterinary-assist', methods=['POST'])
def veterinary_assist():
    """API endpoint to assist with veterinary queries."""
    data = request.form if 'image' in request.files else request.json
    user_message = data.get("message", "")
    species = data.get("species", "general")
    image_analysis = None

    if 'image' in request.files:
        image_file = request.files['image']
        image = Image.open(image_file).convert("RGB")
        prediction = classify_image(image)
        image_analysis = f"Predicted class index by EfficientNet-Lite0 model: {prediction}"

    if user_message or image_analysis:
        response = veterinary_bot(user_message, species=species, image_analysis=image_analysis)
        return jsonify({"analysis": image_analysis, "response": response})
    else:
        return jsonify({"error": "Please provide a message or an image for analysis."}), 400

def classify_image(image):
    """Classify image using EfficientNet-Lite0."""
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)  # Create a mini-batch as expected by the model
    with torch.no_grad():
        output = efficientnet_model(input_batch)
        _, predicted_idx = torch.max(output, 1)
    return predicted_idx.item()

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

# Run the Flask app
if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print(f"Public URL: {public_url}")
    app.run(host="0.0.0.0", port=5000)
