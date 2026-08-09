"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";

interface HistoryEntry {
  day: number;
  question: string;
  answer: string;
  score: number;
  notable_quote?: string;
  cheat_flagged?: boolean;
}

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
  interviewHistory: HistoryEntry[];
  onRestart: () => void;
}

function scoreToPercent(score: number): number {
  return Math.max(0, Math.min(100, Math.round((score / 4) * 100)));
}

function getGrade(score: number): string {
  if (score >= 80) return "A";
  if (score >= 65) return "B";
  if (score >= 45) return "C";
  return "F";
}

function getScoreClass(score: number): string {
  if (score >= 70) return "high";
  if (score >= 40) return "mid";
  return "low";
}

function ScoreRing({ score, size = 140 }: { score: number; size?: number }) {
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const grade = getGrade(score);
  const gradeClass =
    grade === "A" ? "grade-A" : grade === "B" ? "grade-B" : grade === "C" ? "grade-C" : "grade-F";
  const color =
    score >= 70 ? "#10b981" : score >= 45 ? "#f59e0b" : "#ef4444";
  const dashOffset = circumference * (1 - score / 100);

  return (
    <div className="score-ring-card">
      <div className="score-ring-wrap" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke="var(--border)" strokeWidth={10}
          />
          <motion.circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke={color} strokeWidth={10}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: dashOffset }}
            transition={{ duration: 1.4, ease: "easeOut", delay: 0.3 }}
          />
        </svg>
        <div className="score-ring-val">
          <motion.div
            className="score-ring-num"
            style={{ color }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            {score}
          </motion.div>
          <div className="score-ring-denom">/ 100</div>
        </div>
      </div>
      <div className={`score-grade ${gradeClass}`}>{grade}</div>
      <div className="score-ring-label">Overall Score</div>
    </div>
  );
}

function AnimatedBar({ pct, color }: { pct: number; color: string }) {
  return (
    <div className="day-bar-track">
      <motion.div
        className="day-bar-fill"
        style={{ background: color }}
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 1.1, ease: "easeOut", delay: 0.2 }}
      />
    </div>
  );
}

export default function ResultsDashboard({
  candidateName,
  candidateRole,
  feedback,
  theta,
  thetaHistory,
  interviewHistory,
  onRestart,
}: ResultsDashboardProps) {
  if (!feedback) return null;

  // Compute overall score from history
  const overallScore =
    interviewHistory.length > 0
      ? Math.round(
          interviewHistory.reduce((acc, h) => acc + scoreToPercent(h.score), 0) /
            interviewHistory.length
        )
      : Math.max(0, Math.min(100, Math.round((theta + 2) * 25)));

  // Per-day aggregation
  const dayMap: Record<number, number[]> = {};
  interviewHistory.forEach((h) => {
    if (!dayMap[h.day]) dayMap[h.day] = [];
    dayMap[h.day].push(scoreToPercent(h.score));
  });

  const dayScores = Object.entries(dayMap)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([day, scores]) => ({
      day: Number(day),
      score: Math.round(scores.reduce((a, b) => a + b, 0) / scores.length),
    }));

  const barColor = (s: number) =>
    s >= 70 ? "#10b981" : s >= 45 ? "#f59e0b" : "#ef4444";

  return (
    <div id="results-screen" className="screen active">
      <div className="results-wrapper">
        {/* ── HERO ROW ── */}
        <div className="results-hero">
          <ScoreRing score={overallScore} />
          <div className="results-summary-card">
            <div>
              <div className="results-complete-badge">✓ Interview Complete</div>
            </div>
            <div className="results-name">
              {candidateName.split(" ")[0]}'s{" "}
              <span>Performance Report</span>
            </div>
            <div className="results-role">
              {candidateName} · {candidateRole}
            </div>
            <div className="results-summary-text">{feedback.summary}</div>
          </div>
        </div>

        {/* ── PER-QUESTION TABLE ── */}
        <div className="r-section">
          <div className="r-section-title">
            <span className="r-badge accent" />
            Question-by-Question Breakdown
          </div>
          {interviewHistory.length > 0 ? (
            <table className="q-table">
              <thead>
                <tr>
                  <th style={{ width: 28 }}>#</th>
                  <th>Question & Answer</th>
                  <th style={{ textAlign: "right" }}>Score</th>
                </tr>
              </thead>
              <tbody>
                {interviewHistory.map((h, i) => {
                  const pct = scoreToPercent(h.score);
                  const cls = getScoreClass(pct);
                  return (
                    <motion.tr
                      key={i}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.06 }}
                    >
                      <td>
                        <div
                          className="q-num"
                          style={{
                            background:
                              cls === "high"
                                ? "var(--green-light)"
                                : cls === "mid"
                                ? "var(--amber-light)"
                                : "var(--red-light)",
                            color:
                              cls === "high"
                                ? "var(--green)"
                                : cls === "mid"
                                ? "var(--amber)"
                                : "var(--red)",
                          }}
                        >
                          {i + 1}
                        </div>
                      </td>
                      <td>
                        <div className="q-text-preview">{h.question}</div>
                        <div className="q-answer-preview">
                          "{h.answer.length > 120 ? h.answer.slice(0, 120) + "…" : h.answer}"
                        </div>
                        {h.cheat_flagged && (
                          <span className="q-cheat-badge">⚠ Unusual response speed flagged</span>
                        )}
                      </td>
                      <td style={{ textAlign: "right", verticalAlign: "top", paddingTop: 14 }}>
                        <span className={`q-score-badge ${cls}`}>{pct}/100</span>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div style={{ color: "var(--text-muted)", fontSize: 14 }}>
              No question data available.
            </div>
          )}
        </div>

        {/* ── TWO-COLUMN: PER-DAY SCORES + TOPIC SCORES ── */}
        <div className="results-two-col">
          {/* Per-day */}
          <div className="r-section">
            <div className="r-section-title">
              <span className="r-badge teal" />
              Score by Curriculum Day
            </div>
            <div className="day-bar-list">
              {dayScores.length > 0 ? (
                dayScores.map(({ day, score }) => (
                  <div key={day} className="day-bar-row">
                    <div className="day-bar-header">
                      <div className="day-bar-label">Day {day}</div>
                      <div className="day-bar-val" style={{ color: barColor(score) }}>
                        {score}/100
                      </div>
                    </div>
                    <AnimatedBar pct={score} color={barColor(score)} />
                  </div>
                ))
              ) : (
                <div style={{ color: "var(--text-muted)", fontSize: 14 }}>No data.</div>
              )}
            </div>
          </div>

          {/* AI-generated topic scores */}
          <div className="r-section">
            <div className="r-section-title">
              <span className="r-badge accent" />
              Topic Mastery
            </div>
            <div className="day-bar-list">
              {Object.entries(feedback.topicScores || {}).map(([topic, score]) => {
                const pct = Math.round((score / 4) * 100);
                return (
                  <div key={topic} className="day-bar-row">
                    <div className="day-bar-header">
                      <div className="day-bar-label">{topic}</div>
                      <div className="day-bar-val" style={{ color: barColor(pct) }}>
                        {pct}/100
                      </div>
                    </div>
                    <AnimatedBar pct={pct} color={barColor(pct)} />
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* ── STRENGTHS / GAPS / NEXT STEPS ── */}
        <div className="feedback-three-col">
          <div className="r-section">
            <div className="r-section-title">
              <span className="r-badge green" />
              Strengths
            </div>
            <div className="feedback-list">
              {feedback.strengths.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="feedback-item"
                >
                  <div className="feedback-icon strength">✓</div>
                  <div>{item}</div>
                </motion.div>
              ))}
            </div>
          </div>
          <div className="r-section">
            <div className="r-section-title">
              <span className="r-badge red" />
              Gaps to Address
            </div>
            <div className="feedback-list">
              {feedback.gaps.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="feedback-item"
                >
                  <div className="feedback-icon gap">↓</div>
                  <div>{item}</div>
                </motion.div>
              ))}
            </div>
          </div>
          <div className="r-section">
            <div className="r-section-title">
              <span className="r-badge amber" />
              Next Steps
            </div>
            <div className="feedback-list">
              {feedback.next.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="feedback-item"
                >
                  <div className="feedback-icon next">→</div>
                  <div>{item}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* ── ACTIONS ── */}
        <div className="results-actions">
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            className="btn-filled"
            id="again-btn"
            onClick={onRestart}
          >
            Interview Another →
          </motion.button>
        </div>
      </div>
    </div>
  );
}
