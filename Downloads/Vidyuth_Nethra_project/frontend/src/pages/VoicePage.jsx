import React, { useState, useEffect, useRef } from 'react';
import { voiceApi } from '../services/api';

const sampleCommands = [
  '"Turn off AC"',
  '"Show energy usage"',
  '"What is my bill?"',
  '"Show highest consuming device"',
  '"Predict next month\'s bill"',
];

export default function VoicePage({ t, selectedHome }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [commandResult, setCommandResult] = useState(null);
  const [commandLog, setCommandLog] = useState([]);
  const [error, setError] = useState('');
  const recognitionRef = useRef(null);

  const supported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;

  const executeCommand = async (text) => {
    if (!selectedHome) return;
    setError('');
    try {
      const res = await voiceApi.sendCommand(selectedHome.id, text);
      const action = res.response;
      const resultObj = { action, type: res.intent };
      setCommandResult(resultObj);
      setCommandLog(prev => [{
        id: Date.now(),
        command: text,
        result: action,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }, ...prev.slice(0, 4)]);
    } catch (err) {
      console.error("Failed to execute voice command:", err);
      setError("Error executing command: " + (err.message || err));
    }
  };

  const startListening = () => {
    setError('');
    setTranscript('');
    setCommandResult(null);

    if (!supported) {
      // Fallback simulation calling backend
      setIsListening(true);
      const demos = ['Turn off AC', 'Show my energy usage', 'What is my bill', 'Show highest consuming device'];
      const demo = demos[Math.floor(Math.random() * demos.length)];
      let i = 0;
      const interval = setInterval(() => {
        setTranscript(demo.slice(0, i + 1));
        i++;
        if (i >= demo.length) {
          clearInterval(interval);
          setTimeout(() => {
            setIsListening(false);
            executeCommand(demo);
          }, 400);
        }
      }, 60);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.lang = 'en-IN';
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (e) => {
      const tVal = Array.from(e.results).map(r => r[0].transcript).join('');
      setTranscript(tVal);
      if (e.results[0].isFinal) {
        setIsListening(false);
        executeCommand(tVal);
      }
    };
    recognition.onerror = (e) => { setError(`Mic error: ${e.error}`); setIsListening(false); };
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
  };

  const handleMicClick = () => {
    if (isListening) stopListening();
    else startListening();
  };

  const tryCommand = (cmd) => {
    const clean = cmd.replace(/"/g, '');
    setTranscript(clean);
    executeCommand(clean);
  };

  return (
    <div>
      <div className="page-header">
        <h1>🎙️ Voice Assistant</h1>
        <p>Speak to control your smart home devices</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20 }}>
        {/* Main Voice Panel */}
        <div className="card">
          <div className="voice-container">
            {/* Animated Rings */}
            <div style={{ position: 'relative', marginBottom: 28 }}>
              {isListening && (
                <>
                  <div style={{
                    position: 'absolute', inset: -20, borderRadius: '50%',
                    border: '1px solid rgba(20,184,166,0.2)',
                    animation: 'pulse 1.5s ease infinite'
                  }} />
                  <div style={{
                    position: 'absolute', inset: -40, borderRadius: '50%',
                    border: '1px solid rgba(20,184,166,0.1)',
                    animation: 'pulse 1.5s ease infinite 0.3s'
                  }} />
                </>
              )}
              <div
                className={`voice-ring ${isListening ? 'listening' : ''}`}
                onClick={handleMicClick}
              >
                <div className="voice-btn">{isListening ? '⏹️' : '🎙️'}</div>
              </div>
            </div>

            {/* Status */}
            <div style={{ textAlign: 'center', marginBottom: 20 }}>
              {isListening ? (
                <>
                  <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--teal)', marginBottom: 6 }}>
                    🔴 Listening…
                  </div>
                  <div className="voice-waves">
                    {[1, 2, 3, 4, 5].map(i => (
                      <div key={i} className="voice-wave" style={{ height: `${20 + Math.random() * 20}px` }} />
                    ))}
                  </div>
                </>
              ) : (
                <div style={{ fontSize: 14, color: 'var(--text-muted)' }}>
                  Tap the mic and speak a command
                </div>
              )}
            </div>

            {/* Transcript */}
            {transcript && (
              <div className="voice-transcript" style={{ marginBottom: 16 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 1 }}>
                  {isListening ? 'Hearing…' : 'You said:'}
                </div>
                <div className="transcript-text">"{transcript}"</div>
              </div>
            )}

            {/* Result */}
            {commandResult && !isListening && (
              <div className="command-result">
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>✅ Action Taken</div>
                <div style={{ fontWeight: 600 }}>{commandResult.action}</div>
              </div>
            )}

            {error && (
              <div style={{ color: 'var(--red)', fontSize: 13, textAlign: 'center', marginTop: 12 }}>
                {error}
              </div>
            )}

            {!supported && (
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8, textAlign: 'center' }}>
                Note: Using demo mode (Web Speech API not available in this browser)
              </div>
            )}

            {/* Sample Commands */}
            <div className="voice-commands">
              <div className="commands-title">Try these commands →</div>
              <div className="commands-grid">
                {sampleCommands.map(cmd => (
                  <button key={cmd} className="command-chip" onClick={() => tryCommand(cmd)}>
                    {cmd}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Command Log */}
        <div>
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-header">
              <div className="card-title">📋 Command Log</div>
            </div>
            {commandLog.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', padding: '24px 0' }}>
                No commands yet. Try speaking!
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {commandLog.map(log => (
                  <div key={log.id} style={{
                    padding: '10px 12px', background: 'var(--bg-secondary)',
                    borderRadius: 8, border: '1px solid var(--border)',
                    animation: 'fadeIn 0.3s ease'
                  }}>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 3 }}>{log.time}</div>
                    <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 2 }}>"{log.command}"</div>
                    <div style={{ fontSize: 12, color: 'var(--teal)' }}>{log.result}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-title" style={{ marginBottom: 12 }}>💬 Supported Commands</div>
            {[
              { cat: 'Devices', examples: ['Turn off AC', 'Turn on lights', 'Fan off'] },
              { cat: 'Navigation', examples: ['Switch to Home 2', 'Go to Dashboard'] },
              { cat: 'Information', examples: ['Show usage', 'What is my bill'] },
              { cat: 'Management', examples: ['Add fan to bedroom', 'Remove light'] },
            ].map(c => (
              <div key={c.cat} style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: 'var(--teal)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 4 }}>
                  {c.cat}
                </div>
                {c.examples.map(ex => (
                  <div key={ex} style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 2 }}>• "{ex}"</div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
