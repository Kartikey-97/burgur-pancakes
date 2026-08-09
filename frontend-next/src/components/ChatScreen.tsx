"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";

export type Message = {
  role: "interviewer" | "candidate";
  content: string;
};

interface ChatScreenProps {
  candidateName: string;
  candidateRole: string;
  candidateData: any;
  messages: Message[];
  isTyping: boolean;
  onSendMessage: (msg: string) => void;
  qCount: number;
  thetaHistory: number[];
}

export default function ChatScreen({
  candidateName,
  candidateRole,
  candidateData,
  messages,
  isTyping,
  onSendMessage,
  qCount,
  thetaHistory,
}: ChatScreenProps) {
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => { scrollToBottom(); }, [messages, isTyping]);
  useEffect(() => { if (!isTyping && inputRef.current) inputRef.current.focus(); }, [isTyping]);

  const handleSend = () => {
    const val = inputValue.trim();
    if (!val || isTyping) return;
    setInputValue("");
    onSendMessage(val);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const parseMessage = (content: string, role: string) => {
    if (role === "candidate") return { text: content, options: [] as any[] };
    const lines = content.split("\n");
    const textLines: string[] = [];
    const options: { key: string; text: string; full: string }[] = [];
    for (const line of lines) {
      const match = line.match(/^([A-D])\)\s*(.*)/i);
      if (match) options.push({ key: match[1], text: match[2], full: line });
      else textLines.push(line);
    }
    return { text: textLines.join("\n").trim(), options };
  };

  // Compute live average score from thetaHistory
  const avgTheta = thetaHistory.length > 0 ? thetaHistory[thetaHistory.length - 1] : 0;
  // Convert theta (-2 to +2 range typically) to 0–100 score
  const liveScore = Math.max(0, Math.min(100, Math.round((avgTheta + 2) * 25)));
  const scoreColor = liveScore >= 70 ? "var(--green)" : liveScore >= 45 ? "var(--amber)" : "var(--red)";

  // Number of questions asked (interviewer messages that aren't the opening "typing" placeholder)
  const questionMessages = messages.filter(m => m.role === "interviewer" && m.content.trim().length > 0);

  return (
    <div id="chat-screen" className="screen active">
      {/* ── LEFT SIDEBAR ── */}
      <div className="chat-sidebar">
        {/* Interviewer block */}
        <div>
          <div className="sidebar-section-label">Interviewer</div>
          <div className="sidebar-interviewer">
            <div className="sidebar-avatar">
              P
              <span className="sidebar-online" />
            </div>
            <div className="sidebar-info">
              <div className="sidebar-name">Priya Nair</div>
              <div className="sidebar-role">Senior Technical Interviewer</div>
            </div>
          </div>
        </div>

        {/* Candidate block */}
        <div>
          <div className="sidebar-section-label">Candidate</div>
          <div className="sidebar-candidate">
            <div className="sidebar-candidate-avatar">{candidateName.charAt(0)}</div>
            <div className="sidebar-candidate-name">{candidateName}</div>
            <div className="sidebar-candidate-meta">{candidateRole}</div>
          </div>
        </div>

        {/* Live score */}
        <div>
          <div className="sidebar-section-label">Live Performance</div>
          <div className="live-score-block">
            <motion.div
              key={liveScore}
              initial={{ scale: 0.8, opacity: 0.5 }}
              animate={{ scale: 1, opacity: 1 }}
              className="live-score-num"
              style={{ color: scoreColor }}
            >
              {thetaHistory.length > 0 ? liveScore : "—"}
            </motion.div>
            <div className="live-score-label">Score / 100</div>
            <div className="live-score-bar-track">
              <motion.div
                className="live-score-bar-fill"
                style={{ background: scoreColor }}
                initial={{ width: 0 }}
                animate={{ width: thetaHistory.length > 0 ? `${liveScore}%` : "0%" }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              />
            </div>
          </div>
        </div>

        {/* Progress tracker (adaptive) */}
        <div style={{ flex: 1, minHeight: 0 }}>
          <div className="sidebar-section-label">Questions</div>
          <div className="progress-track">
            <AnimatePresence>
              {questionMessages.map((_, i) => {
                const isActive = i === questionMessages.length - 1 && isTyping === false;
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.04 }}
                    className="progress-q"
                  >
                    <div className={`q-bubble done`}>
                      {i + 1}
                    </div>
                    <div className="q-label">Q{i + 1}</div>
                  </motion.div>
                );
              })}
              {/* Current question being answered (active) */}
              {isTyping && (
                <motion.div
                  key="active"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="progress-q"
                >
                  <div className="q-bubble active">
                    {questionMessages.length + 1}
                  </div>
                  <div className="q-label">Thinking…</div>
                </motion.div>
              )}
              {questionMessages.length === 0 && !isTyping && (
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  Interview starting…
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* ── RIGHT CHAT PANEL ── */}
      <div className="chat-main">
        {/* Top bar */}
        <div className="chat-topbar">
          <div className="chat-topbar-info">
            <div className="chat-topbar-title">Technical Interview</div>
            <div className="chat-topbar-sub">AI Cohort Assessment · {candidateRole}</div>
          </div>
          <motion.div key={qCount} initial={{ scale: 0.8 }} animate={{ scale: 1 }} className="stat-pill active">
            Q {qCount}
          </motion.div>
          <div className="stat-pill">{candidateName}</div>
        </div>

        {/* Messages */}
        <div id="messages">
          <AnimatePresence initial={false}>
            {messages.map((m, i) => {
              const { text, options } = parseMessage(m.content, m.role);
              if (!text && !options.length && m.role === "interviewer") return null;
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 14, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.28, ease: "easeOut" }}
                  className={`msg-row ${m.role}`}
                >
                  <div className={`msg-avatar ${m.role}`}>
                    {m.role === "interviewer" ? "P" : candidateName.charAt(0)}
                  </div>
                  <div className="msg-body">
                    <div className="msg-meta">
                      {m.role === "interviewer" ? "Priya" : candidateName.split(" ")[0]}
                    </div>
                    <div className="msg-bubble">{text}</div>
                    {options.length > 0 && (
                      <motion.div
                        className="mcq-options"
                        initial="hidden"
                        animate="visible"
                        variants={{
                          hidden: { opacity: 0 },
                          visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
                        }}
                      >
                        {options.map((opt, idx) => (
                          <motion.button
                            key={idx}
                            variants={{ hidden: { opacity: 0, y: 8 }, visible: { opacity: 1, y: 0 } }}
                            whileHover={{ scale: 1.01, x: 3 }}
                            whileTap={{ scale: 0.98 }}
                            className="mcq-btn"
                            disabled={isTyping || i !== messages.length - 1}
                            onClick={() => onSendMessage(opt.full)}
                          >
                            <span className="mcq-key">{opt.key})</span> {opt.text}
                          </motion.button>
                        ))}
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>

          {isTyping && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="typing-row"
            >
              <div className="msg-avatar interviewer">P</div>
              <div className="typing-bubble">
                {[0, 0.2, 0.4].map((delay, i) => (
                  <motion.div
                    key={i}
                    animate={{ y: [0, -5, 0] }}
                    transition={{ repeat: Infinity, duration: 0.7, delay }}
                    className="dot"
                  />
                ))}
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="chat-input-area">
          <div className="input-row">
            <textarea
              id="msg-input"
              ref={inputRef}
              placeholder="Type your answer…"
              rows={1}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isTyping}
              autoFocus
            />
            <motion.button
              whileHover={{ scale: 1.06 }}
              whileTap={{ scale: 0.94 }}
              id="send-btn"
              disabled={!inputValue.trim() || isTyping}
              onClick={handleSend}
              aria-label="Send"
            >
              ▶
            </motion.button>
          </div>
          <div className="input-hint">Enter to send · Shift+Enter for newline</div>
        </div>
      </div>
    </div>
  );
}
