"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";

export type Message = {
  role: "interviewer" | "candidate";
  content: string;
};

interface ChatScreenProps {
  candidateName: string;
  candidateRole: string;
  messages: Message[];
  isTyping: boolean;
  onSendMessage: (msg: string) => void;
  qCount: number;
}

export default function ChatScreen({ candidateName, candidateRole, messages, isTyping, onSendMessage, qCount }: ChatScreenProps) {
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    if (!isTyping && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isTyping]);

  const handleSend = () => {
    const val = inputValue.trim();
    if (!val || isTyping) return;
    setInputValue("");
    onSendMessage(val);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div id="chat-screen" className="screen active">
      <div className="chat-header">
        <div className="chat-header-avatar">P<span className="online-dot"></span></div>
        <div className="chat-header-info">
          <div className="chat-header-name">Priya Nair</div>
          <div className="chat-header-role">Senior Technical Interviewer</div>
        </div>
        <div className="chat-header-stats">
          <div className="stat-pill active" id="q-counter">Q {qCount}</div>
          <div className="stat-pill" id="candidate-pill">{candidateName}</div>
        </div>
      </div>
      <div id="messages">
        {messages.map((m, i) => (
          <div key={i} className={`msg-row ${m.role}`}>
            <div className={`msg-avatar ${m.role}`}>
              {m.role === 'interviewer' ? 'P' : candidateName.charAt(0)}
            </div>
            <div className="msg-body">
              <div className="msg-meta">
                {m.role === 'interviewer' ? 'Priya' : candidateName.split(' ')[0]}
              </div>
              <div className="msg-bubble">{m.content}</div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="typing-row" id="typing-indicator">
            <div className="msg-avatar interviewer">P</div>
            <div className="typing-bubble">
              <div className="dot"></div><div className="dot"></div><div className="dot"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-area">
        <div className="input-row">
          <textarea 
            id="msg-input" 
            ref={inputRef}
            placeholder="Type your answer&hellip;" 
            rows={1}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isTyping}
            autoFocus
          ></textarea>
          <button id="send-btn" disabled={!inputValue.trim() || isTyping} onClick={handleSend} aria-label="Send">&#9658;</button>
        </div>
        <div className="input-hint">Enter to send &nbsp;&middot;&nbsp; Shift+Enter for newline</div>
      </div>
    </div>
  );
}
