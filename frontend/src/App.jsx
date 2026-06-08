import React, { useState, useEffect } from 'react';
import './index.css';

const API_BASE = window.location.hostname === 'localhost' && window.location.port === '5173'
  ? 'http://localhost:8000'
  : '';

const TRENDING_TOPICS = [
  "Adaptive Optimization schedules for Transformer networks",
  "Reinforcement Learning from AI Feedback (RLAIF) for reasoning tasks",
  "Parameter-efficient fine-tuning via Sparse Weight Masking",
  "Direct Preference Optimization (DPO) stabilization on small datasets"
];

const CONFERENCES = [
  { name: "NeurIPS (Very High Prestige)", difficulty: "Hard" },
  { name: "ICML (High Prestige)", difficulty: "Medium-Hard" },
  { name: "CVPR (High Prestige)", difficulty: "Medium-Hard" },
  { name: "EMNLP (Specialized)", difficulty: "Medium" }
];

export default function App() {
  const [state, setState] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('office'); // office, meeting, papers
  const [customTopic, setCustomTopic] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [chatMsg, setChatMsg] = useState('');
  const [interveneMsg, setInterveneMsg] = useState('');
  const [feedbackMsg, setFeedbackMsg] = useState('');
  const [selectedConf, setSelectedConf] = useState(CONFERENCES[0].name);

  // Poll state every 3 seconds for active ticks
  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchState = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/game/state`);
      if (!res.ok) throw new Error("Failed to fetch game state");
      const data = await res.json();
      setState(data);
      if (data.students && data.students.length > 0 && !selectedStudent) {
        setSelectedStudent(data.students[0].name);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleInitProject = async (topic) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/init_project`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      });
      if (!res.ok) throw new Error("Could not start project");
      const data = await res.json();
      setState(data);
      setActiveTab('office');
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTick = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/tick`, { method: 'POST' });
      if (!res.ok) throw new Error("Game tick failed");
      const data = await res.json();
      setState(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveProposal = async (decision) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/approve_proposal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, feedback: feedbackMsg })
      });
      if (!res.ok) throw new Error("Approval submission failed");
      const data = await res.json();
      setState(data);
      setFeedbackMsg('');
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitPaper = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/submit_paper`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conference: selectedConf })
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Paper submission failed");
      }
      const data = await res.json();
      setState(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGroupChat = async (e) => {
    e.preventDefault();
    if (!chatMsg.trim()) return;
    const msg = chatMsg;
    setChatMsg('');
    try {
      const res = await fetch(`${API_BASE}/api/game/group_chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      if (!res.ok) throw new Error("Chat send failed");
      const data = await res.json();
      setState(data);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleIntervene = async (studentName) => {
    if (!interveneMsg.trim()) return;
    const msg = interveneMsg;
    setInterveneMsg('');
    try {
      const res = await fetch(`${API_BASE}/api/game/intervene`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_name: studentName, message: msg })
      });
      if (!res.ok) throw new Error("Intervention failed");
      const data = await res.json();
      setState(data.state);
      alert(`${studentName}'s Response: "${data.reply}"`);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleReset = async () => {
    if (!window.confirm("Are you sure you want to reset the simulation? All progress will be lost.")) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/reset`, { method: 'POST' });
      if (!res.ok) throw new Error("Reset failed");
      const data = await res.json();
      setState(data);
      setSelectedStudent(data.students[0].name);
      setActiveTab('office');
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <div className="error-screen">
        <h2>⚠️ Connection Error</h2>
        <p>Could not connect to the backend server. Is the FastAPI application running?</p>
        <button onClick={fetchState} className="btn-primary">Retry Connection</button>
      </div>
    );
  }

  if (!state) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Opening Laboratory Doors...</p>
      </div>
    );
  }

  const project = state.current_project;
  const currentStudentObj = state.students.find(s => s.name === selectedStudent);

  return (
    <div className="app-container">
      {/* Sidebar Panel */}
      <aside className="sidebar">
        <div className="logo-area">
          <span className="logo-icon">🔬</span>
          <div>
            <h1>PI Simulator</h1>
            <span className="subtitle">Agentic Research Lab</span>
          </div>
        </div>

        {/* Lab Metrics */}
        <div className="stats-panel">
          <div className="stat-card">
            <div className="stat-header">
              <span>💰 Budget (USD)</span>
            </div>
            <div className="stat-val">${state.funding.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          </div>
          <div className="stat-card">
            <div className="stat-header">
              <span>🏆 Reputation</span>
            </div>
            <div className="stat-val">{state.reputation.toFixed(1)}</div>
          </div>
          <div className="stat-card">
            <div className="stat-header">
              <span>📅 Simulation Day</span>
            </div>
            <div className="stat-val">Day {state.day}</div>
          </div>
        </div>

        {/* Project Card */}
        <div className="project-sidebar-card">
          <h3>Active Project</h3>
          {project ? (
            <div className="project-info">
              <p className="topic">"{project.topic}"</p>
              <div className="stage-badge">{project.stage}</div>
            </div>
          ) : (
            <p className="no-project-text">No active project. Launch one in the Office.</p>
          )}
        </div>

        <div className="sidebar-footer">
          <button onClick={handleTick} className="btn-tick" disabled={loading}>
            {loading ? "Simulating..." : "Next Day ➔"}
          </button>
          <button onClick={handleReset} className="btn-reset">
            Reset Simulation ↺
          </button>
        </div>
      </aside>

      {/* Main Panel */}
      <main className="main-content">
        <header className="main-header">
          <div className="tabs">
            <button
              onClick={() => setActiveTab('office')}
              className={`tab-btn ${activeTab === 'office' ? 'active' : ''}`}
            >
              👥 Office & Lab Room
            </button>
            <button
              onClick={() => setActiveTab('meeting')}
              className={`tab-btn ${activeTab === 'meeting' ? 'active' : ''}`}
            >
              💬 Group Meeting Room
            </button>
            <button
              onClick={() => setActiveTab('papers')}
              className={`tab-btn ${activeTab === 'papers' ? 'active' : ''}`}
            >
              📄 Drafts & Review
            </button>
          </div>
          
          {!state.funding && (
            <div className="header-alert warning">
              🚨 Out of funds! Lab operations frozen. Run a reset.
            </div>
          )}
        </header>

        {/* Tabs Area */}
        <div className="tab-pane">
          {/* Office Tab */}
          {activeTab === 'office' && (
            <div className="office-tab">
              {!project || project.status !== "Active" ? (
                <section className="init-project-section glass-card">
                  <h2>Launch New Research Project</h2>
                  <p className="info-desc">
                    Enter a research question or select one of the trending topics to assign to your students.
                  </p>
                  
                  <div className="trending-topics-list">
                    <h4>Select a Trending Topic:</h4>
                    {TRENDING_TOPICS.map((topic, i) => (
                      <button
                        key={i}
                        className="topic-choice-btn"
                        onClick={() => handleInitProject(topic)}
                        disabled={loading}
                      >
                        ⚡ {topic}
                      </button>
                    ))}
                  </div>

                  <div className="custom-topic-input">
                    <h4>Or enter a fully custom topic:</h4>
                    <div className="input-row">
                      <input
                        type="text"
                        placeholder="e.g., Implementing Low-rank adapters for Convolutional backbones..."
                        value={customTopic}
                        onChange={(e) => setCustomTopic(e.target.value)}
                      />
                      <button
                        onClick={() => handleInitProject(customTopic)}
                        className="btn-primary"
                        disabled={!customTopic.trim() || loading}
                      >
                        Launch Project
                      </button>
                    </div>
                  </div>
                </section>
              ) : (
                <div className="active-lab-view">
                  {/* Students Grid */}
                  <section className="students-section">
                    <h2>Research Students</h2>
                    <div className="students-grid">
                      {state.students.map((student) => {
                        const statusColors = {
                          "Idle": "idle",
                          "Resting": "resting",
                          "Searching ArXiv": "searching",
                          "Writing Proposal": "proposal",
                          "Awaiting PI Approval": "approval",
                          "Experimenting": "experiment",
                          "Writing Draft": "writing"
                        };
                        const statusClass = statusColors[student.status] || "idle";
                        return (
                          <div
                            key={student.name}
                            className={`student-card glass-card ${selectedStudent === student.name ? 'selected' : ''}`}
                            onClick={() => setSelectedStudent(student.name)}
                          >
                            <div className="student-card-header">
                              <h3>{student.name}</h3>
                              <span className={`status-pill ${statusClass}`}>
                                {student.status}
                              </span>
                            </div>
                            <p className="role">{student.role}</p>

                            <div className="student-metric">
                              <span className="label">🔋 Energy</span>
                              <div className="progress-bar-container">
                                <div
                                  className="progress-bar-fill"
                                  style={{
                                    width: `${student.energy}%`,
                                    backgroundColor: student.energy < 25 ? '#ff5252' : student.energy < 60 ? '#ffa726' : '#66bb6a'
                                  }}
                                ></div>
                              </div>
                              <span className="val">{student.energy}/100</span>
                            </div>

                            <div className="skills-grid">
                              <div className="skill-item">
                                <span className="label">Research</span>
                                <span className="val">{(student.skills.research * 10).toFixed(0)}</span>
                              </div>
                              <div className="skill-item">
                                <span className="label">Coding</span>
                                <span className="val">{(student.skills.coding * 10).toFixed(0)}</span>
                              </div>
                              <div className="skill-item">
                                <span className="label">Writing</span>
                                <span className="val">{(student.skills.writing * 10).toFixed(0)}</span>
                              </div>
                            </div>

                            <div className="activity">
                              <strong>Current:</strong> {student.activity}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </section>

                  {/* Student Workspace (Logs/Thoughts/Intervention) */}
                  {currentStudentObj && (
                    <section className="student-workspace glass-card">
                      <h2>{currentStudentObj.name}'s Workspace & Thought Stream</h2>
                      <div className="workspace-layout">
                        <div className="thought-stream">
                          <h4>Internal Monologue / Logs</h4>
                          <div className="logs-box">
                            {currentStudentObj.thoughts.length === 0 ? (
                              <p className="empty-text">No thoughts recorded yet today. Click "Next Day" to begin work.</p>
                            ) : (
                              currentStudentObj.thoughts.map((thought, idx) => (
                                <div key={idx} className="log-entry">
                                  <span className="log-bullet">💭</span>
                                  <p>{thought}</p>
                                </div>
                              ))
                            )}
                          </div>
                        </div>

                        <div className="direct-intervention">
                          <h4>PI Direct Instruction</h4>
                          <p className="help-text">
                            Instruct {currentStudentObj.name} directly. This adds feedback directly into their thought context.
                          </p>
                          <div className="input-row">
                            <input
                              type="text"
                              placeholder={`Type guidance to ${currentStudentObj.name} (e.g. "Focus on finding papers with code")`}
                              value={interveneMsg}
                              onChange={(e) => setInterveneMsg(e.target.value)}
                            />
                            <button
                              onClick={() => handleIntervene(currentStudentObj.name)}
                              className="btn-primary"
                              disabled={!interveneMsg.trim()}
                            >
                              Send Instruction
                            </button>
                          </div>
                        </div>
                      </div>
                    </section>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Meeting Room Tab */}
          {activeTab === 'meeting' && (
            <div className="meeting-tab glass-card">
              <h2>Weekly Group Meeting</h2>
              <p className="info-desc">
                Conduct research reviews. Type a question or instruction to discuss details, model parameters, or findings. Every active student will comment based on their specialty.
              </p>

              <div className="chat-messages-box">
                {state.meeting_chat.map((msg, i) => {
                  let roleClass = "chat-student";
                  if (msg.sender === "Professor") roleClass = "chat-pi";
                  else if (msg.sender === "System") roleClass = "chat-system";
                  
                  return (
                    <div key={i} className={`chat-message ${roleClass}`}>
                      <div className="message-header">
                        <strong>{msg.sender}</strong>
                        {msg.role && <span className="role-tag">({msg.role})</span>}
                      </div>
                      <p className="message-content">{msg.message}</p>
                    </div>
                  );
                })}
              </div>

              <form onSubmit={handleGroupChat} className="chat-form">
                <input
                  type="text"
                  placeholder="Ask the group: e.g. 'How should we handle variance in the sandbox?'"
                  value={chatMsg}
                  onChange={(e) => setChatMsg(e.target.value)}
                />
                <button type="submit" className="btn-primary">Send to Group</button>
              </form>
            </div>
          )}

          {/* Drafts Tab */}
          {activeTab === 'papers' && (
            <div className="papers-tab">
              {/* Approvals Gate */}
              {state.pending_approvals && state.pending_approvals.length > 0 && (
                <div className="review-alert-card glass-card">
                  <h3>⚠️ Milestone Review Required</h3>
                  <div className="approval-content">
                    <h4>{state.pending_approvals[0].title}</h4>
                    <p>{state.pending_approvals[0].description}</p>
                    <pre className="code-view-box">
                      {state.pending_approvals[0].content}
                    </pre>
                  </div>
                  
                  <div className="feedback-section">
                    <input
                      type="text"
                      placeholder="Add guidance or revision requests if rejecting..."
                      value={feedbackMsg}
                      onChange={(e) => setFeedbackMsg(e.target.value)}
                    />
                    <div className="action-buttons">
                      <button
                        onClick={() => handleApproveProposal('approve')}
                        className="btn-success"
                        disabled={loading}
                      >
                        Approve Proposal ✓
                      </button>
                      <button
                        onClick={() => handleApproveProposal('reject')}
                        className="btn-danger"
                        disabled={loading}
                      >
                        Request Revisions ✗
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Submission Gate */}
              {project && project.stage === "Awaiting Submission" && (
                <div className="submission-card glass-card">
                  <h3>🚀 Submit Research Paper</h3>
                  <p className="info-desc">
                    Your paper draft is finalized. Submit the manuscript for peer review. Submitting costs <strong>$800</strong> registration fees.
                  </p>
                  
                  <div className="submission-row">
                    <div className="conf-select">
                      <label>Select Target Venue:</label>
                      <select
                        value={selectedConf}
                        onChange={(e) => setSelectedConf(e.target.value)}
                      >
                        {CONFERENCES.map((c, i) => (
                          <option key={i} value={c.name}>{c.name} ({c.difficulty})</option>
                        ))}
                      </select>
                    </div>
                    <button onClick={handleSubmitPaper} className="btn-primary-large" disabled={loading}>
                      Submit Manuscript
                    </button>
                  </div>
                </div>
              )}

              {/* Peer Review Output */}
              {project && project.reviews && (
                <div className="reviews-card glass-card">
                  <h3>📬 Peer Review Reports</h3>
                  <div className="reviews-list">
                    {project.reviews.map((rev, i) => (
                      <div key={i} className="review-report">
                        {rev}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Files Viewer */}
              {project ? (
                <div className="workspace-files glass-card">
                  <h2>Lab Workspace Files</h2>
                  <p className="info-desc">
                    These are files written and compiled inside your lab's directory as your students progress.
                  </p>

                  <div className="files-layout">
                    {project.proposal_draft && (
                      <div className="file-section">
                        <h4>📄 literature_review.md / proposal.md</h4>
                        <div className="file-viewer">
                          <pre>{project.proposal_draft}</pre>
                        </div>
                      </div>
                    )}

                    {project.experiment_results && (
                      <div className="file-section">
                        <h4>🛠️ experiment.py & results.log</h4>
                        <div className="file-viewer">
                          <pre>{project.experiment_results}</pre>
                        </div>
                      </div>
                    )}

                    {project.paper_draft && (
                      <div className="file-section">
                        <h4>📝 paper.md (Manuscript Draft)</h4>
                        <div className="file-viewer">
                          <pre>{project.paper_draft}</pre>
                        </div>
                      </div>
                    )}

                    {!project.proposal_draft && !project.experiment_results && !project.paper_draft && (
                      <p className="empty-text">No files have been written yet. Instruct your students to start literature review.</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="glass-card">
                  <p className="empty-text">Launch a project to see research documents here.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Global Logs Panel */}
      <section className="global-logs-panel glass-card">
        <h3>📢 Lab Event Logs</h3>
        <div className="logs-stream">
          {state.system_logs.map((log, index) => (
            <div key={index} className="log-line">
              {log}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
