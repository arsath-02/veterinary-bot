from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx
import time
import torch
from efficientnet_lite_pytorch import EfficientNet

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
    """
)

# Load EfficientNet-Lite0 model
efficientnet_model = EfficientNet.from_name('efficientnet-lite0')  # Updated this line
efficientnet_model.eval()

# Define image preprocessing pipeline for EfficientNet-Lite0
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Veterinary bot function to handle Groq response with memory and image analysis
def veterinary_bot(message, species="general", image_analysis=None):
    # Detect the language of the message
    language = detect(message)
    
    # Load conversation memory
    memory_context = memory.load_memory_variables(inputs={"user_query": message})
    
    # Build prompt with image analysis if provided
    prompt = prompt_template.format(
        species=species,
        history=memory_context['history'],
        user_query=message,
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
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": message}],
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                stream=True,
                stop=None,
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    result += chunk.choices[0].delta.content
            break
        except (httpx.RemoteProtocolError, httpx.RequestError) as err:
            # Retry with exponential backoff on error
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return "Unable to process the request at this time. Please try again later."

    # Ensure the response is saved to memory only if it is complete
    if result.strip():
        memory.save_context({"user_query": message}, {"response": result.strip()})
    
    return result.strip()

# Combined endpoint to handle veterinary chat with optional image analysis
@app.route('/veterinary-assist', methods=['POST'])
def veterinary_assist():
    # Check if the request contains files or JSON data
    data = request.form if 'image' in request.files else request.json
    user_message = data.get("message", "Please provide more information on the analysis result.")
    species = data.get("species", "general")

    image_analysis = None
    if 'image' in request.files:
        # Process the image and perform recognition if an image is provided
        image_file = request.files['image']
        image = Image.open(image_file).convert("RGB")
        prediction = classify_image(image)
        image_analysis = f"Predicted class index by EfficientNet-Lite0 model: {prediction}"

    # Generate response using both message and image analysis (if provided)
    response = veterinary_bot(user_message, species=species, image_analysis=image_analysis)
    return jsonify({"analysis": image_analysis, "response": response})

def classify_image(image):
    # Preprocess the image
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)  # Create a mini-batch as expected by the model

    # Move tensor to appropriate device if using GPU
    with torch.no_grad():
        output = efficientnet_model(input_batch)
    
    # Get the predicted class (index of max value)
    _, predicted_idx = torch.max(output, 1)
    return predicted_idx.item()

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

# Run the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
