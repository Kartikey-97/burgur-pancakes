"use client";

import RadarChart from "./charts/RadarChart";
import ThetaTrajectory from "./charts/ThetaTrajectory";

interface Feedback {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
  topicScores: Record<string, number>;
}

interface ResultsDashboardProps {
  candidateName: string;
  candidateRole: string;
  feedback: Feedback | null;
  theta: number;
  thetaHistory: number[];
  onRestart: () => void;
}

export default function ResultsDashboard({ candidateName, candidateRole, feedback, theta, thetaHistory, onRestart }: ResultsDashboardProps) {
  if (!feedback) return null;

  return (
    <div id="results-screen" className="screen active">
      <div className="results-header">
        <div className="results-complete-badge">&#10003; Interview Complete</div>
        <div className="results-title">Your Performance<br /><span>Report Card</span></div>
        <div className="results-subtitle" id="results-subtitle">
          Assessment for {candidateName} &middot; {candidateRole}
        </div>
      </div>
      <div className="results-body">
        <div className="r-card full" style={{ marginBottom: 18 }}>
          <div className="r-card-title"><span className="dot-icon accent"></span>Overall Summary</div>
          <div className="summary-text" id="summary-text">{feedback.summary}</div>
        </div>
        <div className="results-grid">
          <div className="r-card" id="radar-card">
            <div className="r-card-title"><span className="dot-icon accent"></span>Topic Mastery</div>
            <div className="radar-wrap">
              <RadarChart scores={feedback.topicScores} />
            </div>
          </div>
          <div className="r-card" id="bars-card">
            <div className="r-card-title"><span className="dot-icon teal"></span>Score per Topic</div>
            <div className="score-bar-list" id="score-bars">
              {Object.entries(feedback.topicScores || {}).map(([topic, score]) => (
                <div key={topic}>
                  <div className="score-bar-label">
                    <span>{topic}</span>
                    <span>{score.toFixed(1)} / 4.0</span>
                  </div>
                  <div className="score-bar-track">
                    <div 
                      className="score-bar-fill" 
                      style={{ width: `${(score / 4) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 22, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
              <div className="r-card-title" style={{ marginBottom: 10 }}><span className="dot-icon accent"></span>Ability Estimate (&theta;)</div>
              <div className="theta-display">
                <div className={`theta-number ${theta >= 0 ? "positive" : "negative"}`} id="theta-val">
                  {theta > 0 ? "+" : ""}{theta.toFixed(2)}
                </div>
                <div className="theta-desc" id="theta-desc">
                  {theta > 0.5 ? 'Above expected — strong performance across topics.' :
                   theta > 0   ? 'At or slightly above baseline — solid foundations.' :
                   theta > -0.5 ? 'Slightly below expected — some gaps to address.' :
                               'Below baseline — key concepts need reinforcement.'}
                </div>
              </div>
              <div style={{ marginTop: 16 }}>
                <ThetaTrajectory history={thetaHistory} />
              </div>
            </div>
          </div>
          <div className="r-card">
            <div className="r-card-title"><span className="dot-icon teal"></span>Strengths</div>
            <div className="feedback-list" id="strengths-list">
              {feedback.strengths.map((item, i) => (
                <div key={i} className="feedback-item">
                  <div className="feedback-icon strength">✓</div>
                  <div>{item}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="r-card">
            <div className="r-card-title"><span className="dot-icon danger"></span>Gaps</div>
            <div className="feedback-list" id="gaps-list">
              {feedback.gaps.map((item, i) => (
                <div key={i} className="feedback-item">
                  <div className="feedback-icon gap">↓</div>
                  <div>{item}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="r-card full">
            <div className="r-card-title"><span className="dot-icon warn"></span>Next Steps</div>
            <div className="feedback-list" id="next-list">
              {feedback.next.map((item, i) => (
                <div key={i} className="feedback-item">
                  <div className="feedback-icon next">→</div>
                  <div>{item}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="results-actions">
          <button className="btn-filled" id="again-btn" onClick={onRestart}>Interview Another &rarr;</button>
        </div>
      </div>
    </div>
  );
}
