import React, { useState } from 'react';
import './styles/main.scss';
import axios from 'axios'; 

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;
  
    // Add user's message
    setMessages(prev => [...prev, { sender: 'You', text: input }]);
    const userInput = input;
    setInput('');
  
      // Send POST request to REST API
    axios.post('http://localhost:1234/v1/chat/completions', {
    model: 'gemma-3-4b-it',
    messages: [
        { role: 'user', content: userInput }
    ],
    temperature: 0.7
    })
    .then(response => {
        console.log('Response:');
        console.log('Chat Response:', response.data.choices[0].message.content);
        setMessages(prev => [
            ...prev,
            { sender: 'Bot', text: response.data.choices[0].message.content },
            ]);
    })
    .catch(error => {
        console.log('Error:');  
        console.error('Error:', error.response?.data || error.message);
        setMessages(prev => [
            ...prev,
            { sender: 'Bot', text: 'Error: Unable to fetch response.' },
            ]);
    });

  };

  const handleKeyDown = (e) => {
    console.log('Key pressed:', e.key);
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="chat-container">
      <div className="chat-output">
        {messages.map((msg, i) => (
          <div className="message" key={i}>
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatBox;
