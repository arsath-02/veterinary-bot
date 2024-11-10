import requests

url = "http://127.0.0.1:8000/get_response/"
data = {
    "query": "What should I do if my dog has a fever?",
    "species": "dog"
}

response = requests.post(url, json=data)
print("Chatbot Response:", response.json())

