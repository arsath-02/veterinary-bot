import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { FiSend } from 'react-icons/fi';
import { AiOutlineCamera } from 'react-icons/ai';
import { MdPets } from 'react-icons/md';

function ChatInterface() {
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Hello! How can I assist you with your pet today?' },
  ]);
  const [message, setMessage] = useState('');
  const [species, setSpecies] = useState('general');
  const [image, setImage] = useState(null);
  const [isTyping, setIsTyping] = useState(false); // Track if bot is typing
  const chatEndRef = useRef(null);

  // Typing effect: gradually reveal the bot's message
  const addTypingEffect = (text, callback) => {
    let i = 0;
    setIsTyping(true);
    const interval = setInterval(() => {
      setMessages((prevMessages) => {
        const newText = prevMessages[prevMessages.length - 1].text + text[i];
        return [
          ...prevMessages.slice(0, -1),
          { type: 'bot', text: newText },
        ];
      });
      i++;
      if (i >= text.length) {
        clearInterval(interval);
        setIsTyping(false);
        callback();
      }
    }, 40); // Faster typing speed (40ms per character)
  };

  const handleSendMessage = async () => {
    if (!message.trim() && !image) return;

    // Add user message to the chat
    setMessages((prevMessages) => [
      ...prevMessages,
      { type: 'user', text: message || 'Image uploaded', image: image ? URL.createObjectURL(image) : null },
    ]);
    setMessage('');

    const formData = new FormData();
    formData.append('message', message);
    formData.append('species', species);
    if (image) formData.append('image', image);

    try {
      const res = await axios.post('https://apparent-wolf-obviously.ngrok-free.app/veterinary-assist', formData);

      // Ensure the response from the server is defined before showing it
      if (res.data.response) {
        // After sending the message, add the typing effect for the bot's response
        addTypingEffect(res.data.response, () => {
          // You can add any additional action once the typing effect finishes
        });
      } else {
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: 'bot', text: 'Sorry, I could not understand the response.' },
        ]);
      }
    } catch (error) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { type: 'bot', text: 'Error connecting to the server.' },
      ]);
    }
  };

  // Scroll to bottom whenever a new message is added
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="h-screen bg-gray-100 flex flex-col justify-between p-4 lg:p-6 items-center">
      <div className="w-full max-w-screen-sm bg-white rounded-lg shadow-lg p-4 flex flex-col flex-grow">
        <h2 className="text-2xl font-bold text-blue-600 text-center mb-4 flex items-center justify-center">
          <MdPets className="mr-2" />
          Veterinary AI Assistant
        </h2>

        {/* Messages container - scrollable */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-3 pr-3">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg max-w-full ${
                msg.type === 'bot' ? 'bg-blue-100 text-blue-900' : 'bg-green-100 text-green-900 text-right'
              }`}
            >
              {msg.text}
              {msg.image && (
                <div className="mt-2 max-w-xs mx-auto">
                  <img src={msg.image} alt="Uploaded" className="w-full h-auto rounded-lg" />
                </div>
              )}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Input area - fixed at the bottom */}
        <div className="mb-4">
          <label className="block text-gray-700">Species:</label>
          <select
            value={species}
            onChange={(e) => setSpecies(e.target.value)}
            className="w-full p-2 border rounded-md"
          >
            <option value="general">General</option>
            <option value="dog">Dog</option>
            <option value="cat">Cat</option>
            <option value="cow">Cow</option>
            <option value="goat">Goat</option>
          </select>
        </div>

        <div className="flex items-center space-x-2 mb-4">
          <label className="block text-gray-700 mr-2">Upload Image:</label>
          <input
            type="file"
            onChange={(e) => setImage(e.target.files[0])}
            className="hidden"
            id="image-upload"
          />
          <label htmlFor="image-upload" className="cursor-pointer">
            <AiOutlineCamera className="text-2xl text-blue-500" />
          </label>

          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask about your pet's health..."
            className="flex-1 p-2 border border-gray-300 rounded-lg outline-none"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault(); // Prevents the default behavior (such as new line)
                handleSendMessage(); // Calls the function to send the message
              }
            }}
          />

          <button
            onClick={handleSendMessage}
            className="p-2 bg-blue-500 rounded-full text-white hover:bg-blue-600"
          >
            <FiSend />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
