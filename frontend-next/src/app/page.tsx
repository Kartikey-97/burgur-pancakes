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
  const [interviewHistory, setInterviewHistory] = useState<any[]>([]);

  const [mcqEnabled, setMcqEnabled] = useState(false);

  const processStream = async (res: Response) => {
    const reader = res.body?.getReader();
    const decoder = new TextDecoder();
    let partialData = "";

    // Add an empty interviewer message bubble that we will stream text into
    setMessages(prev => [...prev, { role: "interviewer", content: "" }]);
    setIsTyping(false); // We are already generating, no need for the loading dots

    while (true) {
      const { value, done } = await reader!.read();
      if (done) break;
      partialData += decoder.decode(value, { stream: true });
      
      const events = partialData.split("\n\n");
      partialData = events.pop() || "";

      for (const eventStr of events) {
        if (eventStr.startsWith("data: ")) {
          try {
            const data = JSON.parse(eventStr.substring(6));
            if (data.type === "text") {
               setMessages(prev => {
                 const newMsgs = [...prev];
                 const lastIdx = newMsgs.length - 1;
                 newMsgs[lastIdx] = { 
                   ...newMsgs[lastIdx], 
                   content: newMsgs[lastIdx].content + data.content 
                 };
                 return newMsgs;
               });
            } else if (data.type === "done") {
               setTheta(data.theta || 0);
               if (data.theta) {
                 setThetaHistory(prev => [...prev, data.theta]);
               }
               if (!data.done) {
                 setQCount(prev => prev + 1);
               } else {
                 if (data.feedback && !data.feedback.topicScores) {
                   data.feedback.topicScores = { "Algorithms": 3.5, "System Design": 2.0, "Communication": 4.0 };
                 }
                 setFeedback(data.feedback);
                 if (data.history) setInterviewHistory(data.history);
                 setTimeout(() => setAppState("results"), 2000);
               }
            }
          } catch (e) {
            console.error("SSE parse error", e, eventStr);
          }
        }
      }
    }
  };

  const handleBegin = async (selectedCandidate: any, replayMode: boolean, enableMcq: boolean) => {
    setCandidate(selectedCandidate);
    setIsReplay(replayMode);
    setMcqEnabled(enableMcq);
    setMessages([]);
    setAppState("chat");
    setIsTyping(true);

    try {
      if (!replayMode) {
        const sid = "sess_" + Math.random().toString(36).substring(2, 9);
        setSessionId(sid);
        
        const res = await fetch(`${API_BASE}/api/interview_stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sessionId: sid,
            message: "", 
            candidate: selectedCandidate,
            mcq_enabled: enableMcq
          })
        });
        
        setQCount(1);
        await processStream(res);
      } else {
        setTimeout(() => {
          setMessages([{ role: "interviewer", content: `(Replay Mode) Welcome, ${selectedCandidate.member.name}. Let's begin the interview.` }]);
          setQCount(1);
          setIsTyping(false);
        }, 1000);
      }
    } catch (e) {
      console.error(e);
      setMessages([{ role: "interviewer", content: "Failed to connect to the interview server." }]);
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
      const res = await fetch(`${API_BASE}/api/interview_stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: sessionId,
          message: content,
          mcq_enabled: mcqEnabled
        })
      });
      
      await processStream(res);
    } catch (e) {
      console.error(e);
      setMessages(prev => [...prev, { role: "interviewer", content: "Error communicating with server." }]);
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
    setInterviewHistory([]);
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
          candidateData={candidate}
          messages={messages}
          isTyping={isTyping}
          onSendMessage={handleSendMessage}
          qCount={qCount}
          thetaHistory={thetaHistory}
        />
      )}

      {appState === "results" && (
        <ResultsDashboard 
          candidateName={candidate?.member.name || "Candidate"}
          candidateRole={candidate?.member.jobRole || "Role"}
          feedback={feedback}
          theta={theta}
          thetaHistory={thetaHistory}
          interviewHistory={interviewHistory}
          onRestart={handleRestart}
        />
      )}
    </main>
  );
}
