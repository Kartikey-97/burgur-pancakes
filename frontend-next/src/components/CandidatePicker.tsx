"use client";

import { useMemo, useState } from "react";
import candidateData from "@/data/candidates.json";

export default function CandidatePicker({ onBegin }: { onBegin: (candidate: any, isReplay: boolean, enableMcq: boolean) => void }) {
  const [selectedId, setSelectedId] = useState("");
  const [enableMcq, setEnableMcq] = useState(false);
  const isReplayMode = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('replay') === '1' : false;
  const candidates = candidateData.candidates || candidateData;

  const selectedCandidate = useMemo(() => {
    return candidates.find((c: any) => c.member.id === selectedId);
  }, [selectedId, candidates]);

  const handleBegin = () => {
    if (selectedCandidate) {
      onBegin(selectedCandidate, isReplayMode, enableMcq);
    }
  };

  return (
    <div id="picker-screen" className="screen active">
      <div className="picker-card">
        <div className="logo-row">
          <div className="logo-icon">&#127908;</div>
          <div>
            <div className="logo-text">Priya</div>
            <div className="logo-sub">AI Technical Interviewer</div>
          </div>
        </div>
        <div className="picker-headline">
          Your personalized<br /><span>technical interview</span><br />starts here.
        </div>
        <p className="picker-sub">
          Select your cohort profile. Priya has studied your mission history and will adapt every question to who you are &mdash; your role, your wins, and where you struggled.
        </p>
        <div className="field-label">Select Candidate</div>
        <div className="select-wrapper">
          <select 
            id="candidate-select" 
            value={selectedId} 
            onChange={(e) => setSelectedId(e.target.value)}
          >
            <option value="" disabled>Choose a candidate&hellip;</option>
            {candidates.map((c: any) => {
              const passedCount = c.missions.filter((m: any) => m.passed).length;
              return (
                <option key={c.member.id} value={c.member.id}>
                  {c.member.name} &mdash; {c.member.jobRole} ({c.member.yearsExperience}yr, {passedCount} passed)
                </option>
              );
            })}
          </select>
        </div>

        <div className={`candidate-preview ${selectedCandidate ? "visible" : ""}`} id="candidate-preview" style={{ display: selectedCandidate ? "flex" : "none" }}>
          <div className="candidate-avatar" id="preview-avatar">
            {selectedCandidate?.member.name.charAt(0)}
          </div>
          <div className="candidate-info">
            <div className="candidate-name" id="preview-name">{selectedCandidate?.member.name}</div>
            <div className="candidate-meta" id="preview-meta">{selectedCandidate?.member.jobRole} &middot; {selectedCandidate?.member.yearsExperience}yr</div>
            <div className="candidate-tags" id="preview-tags">
              <span className="tag accent">{selectedCandidate?.signals.missionsCompleted} Missions</span>
              <span className="tag teal">{selectedCandidate?.signals.commitDays} Days</span>
            </div>
          </div>
        </div>

        <div style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input 
            type="checkbox" 
            id="mcq-toggle" 
            checked={enableMcq} 
            onChange={(e) => setEnableMcq(e.target.checked)}
            style={{ width: '18px', height: '18px', cursor: 'pointer' }}
          />
          <label htmlFor="mcq-toggle" style={{ fontSize: '14px', color: 'var(--text-light)', cursor: 'pointer' }}>
            Enable Multiple Choice Questions (Adaptive)
          </label>
        </div>

        <button 
          id="begin-btn" 
          className="btn-primary" 
          disabled={!selectedCandidate} 
          onClick={handleBegin}
          style={{ marginTop: '24px' }}
        >
          Begin Interview &rarr;
        </button>
      </div>
    </div>
  );
}
