import React, { useState, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [recording, setRecording] = useState(false);
  const [messages, setMessages] = useState([]);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    chunksRef.current = [];

    mediaRecorder.ondataavailable = (e) => {
      chunksRef.current.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
      const form = new FormData();
      form.append('audio', blob, 'recording.wav');

      try {
        const res = await axios.post('http://localhost:5000/api/voice-chat', form);
        const userText = res.data.transcript;
        const genieText = res.data.response;
        const audioUrl = 'http://localhost:5000' + res.data.audio_url;

        setMessages(prev => [
          ...prev,
          { role: 'user', text: userText },
          { role: 'genie', text: genieText }
        ]);

        new Audio(audioUrl).play();
      } catch (error) {
        setMessages(prev => [...prev, { role: 'genie', text: "Oops! Something went wrong." }]);
      }
    };

    mediaRecorder.start();
    setRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>SpeakGenie</h1>
      </header>

      <div className="chat-box">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <span>{msg.role === 'user' ? '🧒' : '🤖'}</span>
            <p>{msg.text}</p>
          </div>
        ))}
      </div>

      <div className="controls">
        <button onClick={startRecording} disabled={recording}>Speak</button>
        <button onClick={stopRecording} disabled={!recording}>Stop</button>
      </div>
    </div>
  );
}

export default App;


