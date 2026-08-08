"use client";

import { useState } from "react";
import BackgroundParticles from "@/components/BackgroundParticles";
import CandidatePicker from "@/components/CandidatePicker";
import ChatScreen, { Message } from "@/components/ChatScreen";
import ResultsDashboard from "@/components/ResultsDashboard";

type AppState = "picker" | "chat" | "results";

const API_BASE = "http://localhost:8000";

export default function Home() {
  const [appState, setAppState] = useState<AppState>("picker");
  const [candidate, setCandidate] = useState<any>(null);
  const [isReplay, setIsReplay] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [qCount, setQCount] = useState(0);
  
  // Results state
  const [feedback, setFeedback] = useState<any>(null);
  const [theta, setTheta] = useState(0);
  const [thetaHistory, setThetaHistory] = useState<number[]>([]);

  const handleBegin = async (selectedCandidate: any, replayMode: boolean) => {
    setCandidate(selectedCandidate);
    setIsReplay(replayMode);
    setMessages([]);
    setAppState("chat");
    setIsTyping(true);

    try {
      if (!replayMode) {
        const sid = "sess_" + Math.random().toString(36).substring(2, 9);
        setSessionId(sid);
        
        const res = await fetch(`${API_BASE}/api/interview`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sessionId: sid,
            message: "", 
            candidate: selectedCandidate
          })
        });
        const data = await res.json();
        
        setMessages([{ role: "interviewer", content: data.reply }]);
        setQCount(1);
        setTheta(data.theta || 0);
        setThetaHistory(data.theta_history || []);
        
        if (data.done) {
          if (!data.feedback.topicScores) {
            data.feedback.topicScores = { "Algorithms": 3.5, "System Design": 2.0, "Communication": 4.0 };
          }
          setFeedback(data.feedback);
          setTimeout(() => setAppState("results"), 2000);
        }
      } else {
        setTimeout(() => {
          setMessages([{ role: "interviewer", content: `(Replay Mode) Welcome, ${selectedCandidate.member.name}. Let's begin the interview.` }]);
          setQCount(1);
        }, 1000);
      }
    } catch (e) {
      console.error(e);
      setMessages([{ role: "interviewer", content: "Failed to connect to the interview server." }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    const userMsg: Message = { role: "candidate", content };
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    if (isReplay) {
      setTimeout(() => {
        setMessages(prev => [...prev, { role: "interviewer", content: "(Replay) That's a good answer. Let's move on to the next question." }]);
        setQCount(prev => prev + 1);
        setIsTyping(false);
        if (qCount >= 2) {
          setFeedback({
            summary: "This is a mock replay summary.",
            strengths: ["Communication", "Problem Solving"],
            gaps: ["System Design"],
            next: ["Practice more system design"],
            topicScores: { "Algorithms": 3.5, "System Design": 2.0, "Communication": 4.0 }
          });
          setTheta(1.2);
          setThetaHistory([0, 0.5, 1.2]);
          setTimeout(() => setAppState("results"), 1000);
        }
      }, 1000);
      return;
    }

    if (!sessionId) {
      setIsTyping(false);
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/interview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: sessionId,
          message: content
        })
      });
      const data = await res.json();
      
      setMessages(prev => [...prev, { role: "interviewer", content: data.reply }]);
      setTheta(data.theta || 0);
      setThetaHistory(data.theta_history || []);

      if (!data.done) {
        setQCount(prev => prev + 1);
      } else {
        if (!data.feedback.topicScores) {
          data.feedback.topicScores = { "Algorithms": 3.5, "System Design": 2.0, "Communication": 4.0 };
        }
        setFeedback(data.feedback);
        setTimeout(() => setAppState("results"), 2000);
      }
    } catch (e) {
      console.error(e);
      setMessages(prev => [...prev, { role: "interviewer", content: "Error communicating with server." }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleRestart = () => {
    setAppState("picker");
    setCandidate(null);
    setSessionId(null);
    setMessages([]);
    setFeedback(null);
    setTheta(0);
    setThetaHistory([]);
    setQCount(0);
  };

  return (
    <main>
      <BackgroundParticles />
      
      {appState === "picker" && (
        <CandidatePicker onBegin={handleBegin} />
      )}
      
      {appState === "chat" && (
        <ChatScreen 
          candidateName={candidate?.member.name || "Candidate"}
          candidateRole={candidate?.member.jobRole || "Role"}
          messages={messages}
          isTyping={isTyping}
          onSendMessage={handleSendMessage}
          qCount={qCount}
        />
      )}

      {appState === "results" && (
        <ResultsDashboard 
          candidateName={candidate?.member.name || "Candidate"}
          candidateRole={candidate?.member.jobRole || "Role"}
          feedback={feedback}
          theta={theta}
          thetaHistory={thetaHistory}
          onRestart={handleRestart}
        />
      )}
    </main>
  );
}
