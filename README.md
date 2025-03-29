# 🐾 Veterinary AI Assistant

An intelligent veterinary chatbot that supports multilingual conversations and image-based diagnosis. It leverages Groq LLM, LangChain memory, and EfficientNet-Lite for image analysis, designed to assist pet owners and veterinarians with medical guidance.

## 🚀 Features

- 🧠 **Conversational AI** using Groq LLM
- 🗣️ **Multilingual support** with automatic language detection
- 📸 **Image-based diagnosis** with EfficientNet-Lite0
- 🐶 **Species-specific responses**
- 📜 **LangChain memory** for context-aware responses
- 🌐 **Secure public access** via ngrok tunnel

## 🧩 Technologies Used

- **Flask** for backend API
- **LangChain** for conversational memory
- **Groq** for fast LLM response
- **EfficientNet-Lite0** for image classification
- **torchvision** for preprocessing
- **Ngrok** to expose local server
- **langdetect** for language auto-detection
- **CORS** for frontend/backend integration

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/arsath-02/veterinary-bot.git
cd vet-ai-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Make sure to set the following before running:

```bash
export GROQ_API_KEY="your_groq_api_key"
export NGROK_AUTH_TOKEN="your_ngrok_auth_token"
```

## 🏃 Running the App

```bash
python app.py
```

The API will be exposed to the internet using ngrok.

## 🧪 API Usage

### Endpoint: `/veterinary-assist`

**POST Request**

```json
{
  "message": "My dog is sneezing a lot.",
  "species": "dog"
}
```

**Optional:** Include image file for image-based diagnosis.

## 🖼️ Image Classification

Upload an image of the pet to get additional analysis integrated into the conversation.

## 🤖 Example Prompt

```
User: My cat is not eating and looks very tired.
Response (English): It could be a sign of digestive issues or fatigue. Is your pet vaccinated or on medication?
```

## 📄 License

MIT License

## 🙌 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## ✨ Author

Made with ❤️ by [Arsath Mohamed]
