"use client";

import { useMemo, useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import baseData from "@/data/candidates.json";

const CURRICULUM_DAYS: { day: number; title: string }[] = [
  { day: 1, title: "VS Code & Python Environment Setup" },
  { day: 2, title: "Local LLM & AI Coding Assistant Setup" },
  { day: 3, title: "First AI Project, React Frontend & GitHub" },
  { day: 4, title: "Reading & Processing Structured Data" },
  { day: 5, title: "Reading & Processing Unstructured Data" },
  { day: 6, title: "Building the Knowledge Base" },
  { day: 7, title: "Embeddings Explained" },
  { day: 8, title: "Vector Databases Overview" },
  { day: 9, title: "Building & Populating the Vector Database" },
  { day: 10, title: "The Retrieval & Matching Engine" },
  { day: 11, title: "RAG End-to-End & LLM API Basics" },
  { day: 12, title: "Prompt Engineering Fundamentals" },
  { day: 13, title: "Advanced Prompting: Function Calling & Structured Outputs" },
  { day: 14, title: "Fine-Tuning: Concepts & When to Use It" },
  { day: 15, title: "Fine-Tuning: Hands-On with LoRA & QLoRA" },
  { day: 16, title: "Chatbot Backend & API Integration" },
  { day: 17, title: "Chatbot Frontend Development" },
  { day: 18, title: "Full-Stack Integration & Streaming Responses" },
  { day: 19, title: "Response Formatting & Rich Outputs" },
  { day: 20, title: "Conversation Memory & Context Management" },
  { day: 21, title: "Agentic Frameworks: LangChain Agents & Tool Use" },
  { day: 22, title: "Multi-Agent Orchestration" },
  { day: 23, title: "Model Context Protocol (MCP)" },
  { day: 24, title: "Agentic Chatbot Integration" },
  { day: 25, title: "Chatbot Evaluation & Testing" },
  { day: 26, title: "Performance Optimization & Cost Management" },
  { day: 27, title: "Security, Privacy & Guardrails" },
  { day: 28, title: "Docker & Kubernetes Deployment" },
  { day: 29, title: "Monitoring, Logging & Observability" },
  { day: 30, title: "Production Readiness & Final Testing" },
  { day: 31, title: "Capstone Project & Final Demo" },
];

const FEATURES = [
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
      </svg>
    ),
    title: "Adaptive Questioning",
    desc: "Difficulty adjusts in real-time based on your performance.",
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
      </svg>
    ),
    title: "Context Retention",
    desc: "Priya remembers everything and asks smart follow-ups.",
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
    title: "Scored in Real-Time",
    desc: "Watch your live score update with each answer.",
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
      </svg>
    ),
    title: "Detailed Report Card",
    desc: "Per-question scores and per-day breakdown at the end.",
  },
];

function buildCustomCandidate(form: {
  name: string; role: string; experience: string; education: string; selectedDays: number[];
}): any {
  const id = "CAND-CUSTOM-" + Date.now();
  const missions = CURRICULUM_DAYS
    .filter((d) => form.selectedDays.includes(d.day))
    .map((d) => ({ day: d.day, title: d.title, passed: true, attempts: 1 }));
  const passedCount = missions.length;
  return {
    member: {
      id, name: form.name,
      jobRole: form.role || "Engineer",
      yearsExperience: parseInt(form.experience) || 0,
      education: form.education || "Not specified",
      status: "COMPLETED",
    },
    missions,
    signals: { commitDays: passedCount, missionsCompleted: passedCount, missionsFirstTry: passedCount },
    isCustom: true,
  };
}

export default function CandidatePicker({
  onBegin,
}: {
  onBegin: (candidate: any, isReplay: boolean, enableMcq: boolean) => void;
}) {
  const baseCandidates: any[] = (baseData as any).candidates || [];
  const [customCandidates, setCustomCandidates] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [enableMcq, setEnableMcq] = useState(false);
  const [search, setSearch] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);

  // New candidate form state
  const [form, setForm] = useState({ name: "", role: "", experience: "", education: "" });
  const [selectedDays, setSelectedDays] = useState<number[]>([]);
  const [formError, setFormError] = useState("");

  const isReplayMode =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search).get("replay") === "1"
      : false;

  // Load custom candidates from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem("priya-custom-candidates");
      if (stored) setCustomCandidates(JSON.parse(stored));
    } catch {}
  }, []);

  const allCandidates = useMemo(
    () => [...baseCandidates, ...customCandidates],
    [customCandidates]
  );

  const filtered = useMemo(() => {
    if (!search.trim()) return allCandidates;
    const q = search.toLowerCase();
    return allCandidates.filter(
      (c) =>
        c.member.name.toLowerCase().includes(q) ||
        c.member.jobRole.toLowerCase().includes(q)
    );
  }, [allCandidates, search]);

  const selectedCandidate = useMemo(
    () => allCandidates.find((c) => c.member.id === selectedId),
    [selectedId, allCandidates]
  );

  const passedCount = selectedCandidate
    ? selectedCandidate.missions.filter((m: any) => m.passed).length
    : 0;

  const handleBegin = () => {
    if (selectedCandidate) onBegin(selectedCandidate, isReplayMode, enableMcq);
  };

  const handleAddCandidate = () => {
    if (!form.name.trim()) { setFormError("Name is required."); return; }
    if (selectedDays.length < 2) { setFormError("Select at least 2 completed days."); return; }
    const newCand = buildCustomCandidate({ ...form, selectedDays });
    const updated = [...customCandidates, newCand];
    setCustomCandidates(updated);
    localStorage.setItem("priya-custom-candidates", JSON.stringify(updated));
    setSelectedId(newCand.member.id);
    setShowAddModal(false);
    setForm({ name: "", role: "", experience: "", education: "" });
    setSelectedDays([]);
    setFormError("");
  };

  const handleDeleteCustom = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = customCandidates.filter((c) => c.member.id !== id);
    setCustomCandidates(updated);
    localStorage.setItem("priya-custom-candidates", JSON.stringify(updated));
    if (selectedId === id) setSelectedId("");
  };

  const toggleDay = (day: number) => {
    setSelectedDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
    );
  };

  return (
    <div id="picker-screen" className="screen active">
      {/* ── LEFT PANEL ── */}
      <motion.div className="picker-left" initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, ease: "easeOut" }}>
        <div className="priya-hero">
          <div className="priya-avatar-ring">
            <div className="priya-avatar-inner">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
              </svg>
            </div>
            <span className="priya-online-dot" />
          </div>
          <div className="priya-hero-info">
            <div className="priya-hero-name">Priya Nair</div>
            <div className="priya-hero-sub">Senior Technical Interviewer · AI</div>
          </div>
        </div>
        <div className="picker-left-headline">Ace your next<br /><span>technical interview.</span></div>
        <p className="picker-left-sub">Priya conducts a personalized, multi-turn AI engineering interview tailored to your cohort history — your strengths, struggles, and gaps.</p>
        <div className="picker-features">
          {FEATURES.map((f, i) => (
            <motion.div key={i} className="picker-feature" initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 + i * 0.1 }}>
              <div className="picker-feature-icon">{f.icon}</div>
              <div>
                <div className="picker-feature-title">{f.title}</div>
                <div className="picker-feature-desc">{f.desc}</div>
              </div>
            </motion.div>
          ))}
        </div>
        <div className="picker-trust-bar">
          <span className="trust-badge">AI Cohort</span>
          <span className="trust-badge">Gemini Powered</span>
          <span className="trust-badge">IRT Scoring</span>
        </div>
      </motion.div>

      {/* ── RIGHT FORM PANEL ── */}
      <motion.div className="picker-right" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, ease: "easeOut", delay: 0.1 }}>
        <div className="picker-form-card">
          <div className="picker-form-header">
            <div className="picker-form-title">Start your interview</div>
            <div className="picker-form-sub">Select a candidate profile or add your own to begin.</div>
          </div>

          {/* Search + Add row */}
          <div className="candidate-picker-section">
            <div className="cp-section-header">
              <span className="picker-field-label" style={{ margin: 0 }}>Candidate Profile</span>
              <button className="cp-add-btn" onClick={() => setShowAddModal(true)}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Add new
              </button>
            </div>

            {/* Search bar */}
            <div className="cp-search-row">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" style={{ color: "var(--text-muted)", flexShrink: 0 }}>
                <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                className="cp-search-input"
                placeholder="Search by name or role…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              {search && (
                <button className="cp-search-clear" onClick={() => setSearch("")}>×</button>
              )}
            </div>

            {/* Candidate card list */}
            <div className="cp-card-list">
              <AnimatePresence mode="popLayout">
                {filtered.length === 0 ? (
                  <div className="cp-empty">No candidates found.</div>
                ) : (
                  filtered.map((c) => {
                    const pc = c.missions.filter((m: any) => m.passed).length;
                    const isSelected = c.member.id === selectedId;
                    return (
                      <motion.div
                        key={c.member.id}
                        layout
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className={`cp-card ${isSelected ? "selected" : ""}`}
                        onClick={() => setSelectedId(c.member.id)}
                      >
                        <div className="cp-card-avatar">{c.member.name.charAt(0)}</div>
                        <div className="cp-card-info">
                          <div className="cp-card-name">{c.member.name}</div>
                          <div className="cp-card-meta">{c.member.jobRole} · {c.member.yearsExperience}yr</div>
                          <div className="cp-card-tags">
                            <span className="cp-card-tag">{pc} passed</span>
                            {c.isCustom && <span className="cp-card-tag custom">Custom</span>}
                          </div>
                        </div>
                        <div className="cp-card-right">
                          {isSelected && (
                            <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="cp-check">
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="20 6 9 17 4 12" />
                              </svg>
                            </motion.div>
                          )}
                          {c.isCustom && (
                            <button className="cp-delete-btn" onClick={(e) => handleDeleteCustom(c.member.id, e)} title="Remove">×</button>
                          )}
                        </div>
                      </motion.div>
                    );
                  })
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* MCQ toggle */}
          <div className="mcq-toggle-row" onClick={() => setEnableMcq(!enableMcq)}>
            <div className="mcq-toggle-text">
              <div className="mcq-toggle-label">Enable Multiple Choice</div>
              <div className="mcq-toggle-sub">AI will occasionally offer multiple-choice options</div>
            </div>
            <div className={`toggle-switch ${enableMcq ? "on" : ""}`}>
              <motion.div className="toggle-thumb" animate={{ x: enableMcq ? 22 : 2 }} transition={{ type: "spring", stiffness: 500, damping: 35 }} />
            </div>
          </div>

          {/* CTA */}
          <motion.button
            id="begin-btn" className="btn-begin"
            disabled={!selectedCandidate}
            onClick={handleBegin}
            whileHover={{ scale: selectedCandidate ? 1.02 : 1 }}
            whileTap={{ scale: selectedCandidate ? 0.98 : 1 }}
          >
            {selectedCandidate
              ? `Begin Interview with ${selectedCandidate.member.name.split(" ")[0]} →`
              : "Select a candidate to begin"}
          </motion.button>
          <div className="picker-form-footer">Adaptive · Context-aware · Scored in real-time</div>
        </div>
      </motion.div>

      {/* ── ADD CANDIDATE MODAL ── */}
      <AnimatePresence>
        {showAddModal && (
          <>
            <motion.div
              className="modal-overlay"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setShowAddModal(false)}
            />
            <motion.div
              className="modal-panel"
              initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 40 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
            >
              <div className="modal-header">
                <div>
                  <div className="modal-title">Add New Candidate</div>
                  <div className="modal-sub">Create a custom profile for your interview session.</div>
                </div>
                <button className="modal-close" onClick={() => setShowAddModal(false)}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>

              <div className="modal-body">
                <div className="modal-field-row">
                  <div className="modal-field">
                    <label className="modal-label">Full Name *</label>
                    <input className="modal-input" placeholder="e.g. Alex Kumar" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                  </div>
                  <div className="modal-field">
                    <label className="modal-label">Job Role</label>
                    <input className="modal-input" placeholder="e.g. ML Engineer" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
                  </div>
                </div>
                <div className="modal-field-row">
                  <div className="modal-field">
                    <label className="modal-label">Years Experience</label>
                    <input className="modal-input" type="number" min="0" max="30" placeholder="0" value={form.experience} onChange={(e) => setForm({ ...form, experience: e.target.value })} />
                  </div>
                  <div className="modal-field">
                    <label className="modal-label">Education</label>
                    <input className="modal-input" placeholder="e.g. B.Tech CS" value={form.education} onChange={(e) => setForm({ ...form, education: e.target.value })} />
                  </div>
                </div>

                <div className="modal-days-section">
                  <label className="modal-label">Completed Curriculum Days * <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>({selectedDays.length} selected)</span></label>
                  <div className="modal-days-grid">
                    {CURRICULUM_DAYS.map((d) => {
                      const isOn = selectedDays.includes(d.day);
                      return (
                        <motion.button
                          key={d.day}
                          whileTap={{ scale: 0.95 }}
                          className={`day-chip ${isOn ? "on" : ""}`}
                          onClick={() => toggleDay(d.day)}
                          type="button"
                        >
                          <span className="day-chip-num">D{d.day}</span>
                          <span className="day-chip-title">{d.title}</span>
                        </motion.button>
                      );
                    })}
                  </div>
                </div>

                {formError && <div className="modal-error">{formError}</div>}
              </div>

              <div className="modal-footer">
                <button className="modal-cancel" onClick={() => setShowAddModal(false)}>Cancel</button>
                <motion.button
                  whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                  className="modal-submit"
                  onClick={handleAddCandidate}
                >
                  Add Candidate →
                </motion.button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
