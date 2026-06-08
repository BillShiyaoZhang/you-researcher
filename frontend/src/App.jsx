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

const TRANSLATIONS = {
  cn: {
    title: "教授模拟器",
    subtitle: "大模型智能科研实验室",
    budget: "实验室经费 (USD)",
    reputation: "实验室声望",
    simDay: "模拟天数",
    activeProject: "当前进行中课题",
    noProject: "暂无进行中的项目。请在办公室启动一个新项目。",
    nextDay: "推进到下一天 ➔",
    simulating: "模拟中...",
    resetSim: "重置模拟 ↺",
    tabOffice: "👥 办公室 & 实验室",
    tabMeeting: "💬 学术组会",
    tabReview: "📄 论文评审与文档",
    launchTitle: "启动新科研项目",
    launchDesc: "输入您的学术研究课题，或选择以下一个热门方向，指派给您的 PhD 学生开展研究。",
    trendingTitle: "选择热门研究方向：",
    customTitle: "或者输入完全自定义课题：",
    launchBtn: "启动课题",
    placeholderCustom: "例如：在卷积骨干网络中应用低秩适配器(LoRA)...",
    studentsTitle: "科研团队 (PhD 学生)",
    workspaceTitle: "的工作区与思维流",
    monologueTitle: "内心独白 / 运行日志",
    emptyThoughts: "今天还没有记录任何想法。点击“推进到下一天”开始工作。",
    piGuidance: "导师直接指示",
    guidanceDesc: "直接向该学生发布具体指导意见，该反馈会合并入学生的下一步推理记忆中。",
    placeholderIntervene: "输入指示（例如：“专注于检索包含开源代码的 ArXiv 论文”）",
    sendInstruction: "发送指示",
    meetingTitle: "实验室每周组会",
    meetingDesc: "举行课题讨论和工作汇报。输入您的指导意见，PhD 学生们会根据自身专长进行发言，并开展跨角色角色讨论。",
    chatPlaceholder: "向团队提问：例如“我们如何解决沙箱中出现的数值发散问题？”",
    chatSend: "发送至组会",
    reviewRequired: "⚠️ 关键节点评审",
    reviewDesc: "学生已经完成了开题报告草拟（附带沙箱代码）。请审核，若满意可批准进入实验阶段。",
    approveBtn: "批准立项 ✓",
    rejectBtn: "驳回并要求修改 ✗",
    placeholderFeedback: "添加指导意见或修改要求...",
    submitTitle: "🚀 学术论文投稿与盲审",
    submitDesc: "论文手稿已最终定稿！支付会议注册费并投稿进行同行双盲评审。提交稿件需要支付 $800 会议注册费。",
    venueLabel: "选择投稿会议：",
    submitBtn: "提交学术手稿",
    reviewsTitle: "📬 同行评审报告 (Blind Review)",
    filesTitle: "工作区生成文件",
    filesDesc: "以下文件是学生在实验文件夹中真实撰写并编译生成的代码与学术手稿。",
    emptyFiles: "当前没有生成任何文件。请指导学生开始检索文献。",
    alertOutFunds: "🚨 经费已耗尽！实验室破产，运营冻结。请重置模拟。",
    responseIntervene: "的答复",
    resetConfirm: "确定要重置模拟吗？所有当前的实验室进度和成果都将丢失。"
  },
  en: {
    title: "PI Simulator",
    subtitle: "Agentic Research Lab",
    budget: "Budget (USD)",
    reputation: "Reputation",
    simDay: "Simulation Day",
    activeProject: "Active Project",
    noProject: "No active project. Launch one in the Office.",
    nextDay: "Next Day ➔",
    simulating: "Simulating...",
    resetSim: "Reset Simulation ↺",
    tabOffice: "👥 Office & Lab Room",
    tabMeeting: "💬 Group Meeting Room",
    tabReview: "📄 Drafts & Review",
    launchTitle: "Launch New Research Project",
    launchDesc: "Enter a research question or select one of the trending topics to assign to your students.",
    trendingTitle: "Select a Trending Topic:",
    customTitle: "Or enter a fully custom topic:",
    launchBtn: "Launch Project",
    placeholderCustom: "e.g., Implementing Low-rank adapters for Convolutional backbones...",
    studentsTitle: "Research Students",
    workspaceTitle: "'s Workspace & Thought Stream",
    monologueTitle: "Internal Monologue / Logs",
    emptyThoughts: "No thoughts recorded yet today. Click \"Next Day\" to begin work.",
    piGuidance: "PI Direct Instruction",
    guidanceDesc: "Instruct student directly. This adds feedback directly into their thought context.",
    placeholderIntervene: "Type guidance (e.g. \"Focus on finding papers with code\")",
    sendInstruction: "Send Instruction",
    meetingTitle: "Weekly Group Meeting",
    meetingDesc: "Conduct research reviews. Type a question or instruction to discuss details. Every active student will comment based on their specialty.",
    chatPlaceholder: "Ask the group: e.g. 'How should we handle variance in the sandbox?'",
    chatSend: "Send to Group",
    reviewRequired: "⚠️ Milestone Review Required",
    reviewDesc: "Alice has drafted a research proposal including experiment code. Review and approve to start execution.",
    approveBtn: "Approve Proposal ✓",
    rejectBtn: "Request Revisions ✗",
    placeholderFeedback: "Add guidance or revision requests if rejecting...",
    submitTitle: "🚀 Submit Research Paper",
    submitDesc: "Your paper draft is finalized. Submit the manuscript for peer review. Submitting costs $800 registration fees.",
    venueLabel: "Select Target Venue:",
    submitBtn: "Submit Manuscript",
    reviewsTitle: "📬 Peer Review Reports",
    filesTitle: "Lab Workspace Files",
    filesDesc: "These are files written and compiled inside your lab's directory as your students progress.",
    emptyFiles: "No files have been written yet. Instruct your students to start literature review.",
    alertOutFunds: "🚨 Out of funds! Lab operations frozen. Run a reset.",
    responseIntervene: "'s Response",
    resetConfirm: "Are you sure you want to reset the simulation? All progress will be lost."
  }
};

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

  const handleLanguageToggle = async () => {
    if (!state) return;
    const nextLang = state.language === 'cn' ? 'en' : 'cn';
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/set_language`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: nextLang })
      });
      if (!res.ok) throw new Error("Language toggle failed");
      const data = await res.json();
      setState(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
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
      alert(`${studentName}${t.responseIntervene}: "${data.reply}"`);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleReset = async () => {
    if (!window.confirm(t.resetConfirm)) return;
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

  // Active translation set
  const t = TRANSLATIONS[state.language || 'cn'];

  const project = state.current_project;
  const currentStudentObj = state.students.find(s => s.name === selectedStudent);

  return (
    <div className="app-container">
      {/* Sidebar Panel */}
      <aside className="sidebar">
        <div className="logo-area">
          <span className="logo-icon">🔬</span>
          <div>
            <h1>{t.title}</h1>
            <span className="subtitle">{t.subtitle}</span>
          </div>
        </div>

        {/* Lab Metrics */}
        <div className="stats-panel">
          <div className="stat-card">
            <div className="stat-header">
              <span>{t.budget}</span>
            </div>
            <div className="stat-val">${state.funding.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          </div>
          <div className="stat-card">
            <div className="stat-header">
              <span>🏆 {t.reputation}</span>
            </div>
            <div className="stat-val">{state.reputation.toFixed(1)}</div>
          </div>
          <div className="stat-card">
            <div className="stat-header">
              <span>📅 {t.simDay}</span>
            </div>
            <div className="stat-val">{state.language === 'cn' ? `第 ${state.day} 天` : `Day ${state.day}`}</div>
          </div>
        </div>

        {/* Project Card */}
        <div className="project-sidebar-card">
          <h3>{t.activeProject}</h3>
          {project ? (
            <div className="project-info">
              <p className="topic">"{project.topic}"</p>
              <div className="stage-badge">{project.stage}</div>
            </div>
          ) : (
            <p className="no-project-text">{t.noProject}</p>
          )}
        </div>

        <div className="sidebar-footer">
          <button onClick={handleTick} className="btn-tick" disabled={loading}>
            {loading ? t.simulating : t.nextDay}
          </button>
          <button onClick={handleReset} className="btn-reset">
            {t.resetSim}
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
              {t.tabOffice}
            </button>
            <button
              onClick={() => setActiveTab('meeting')}
              className={`tab-btn ${activeTab === 'meeting' ? 'active' : ''}`}
            >
              {t.tabMeeting}
            </button>
            <button
              onClick={() => setActiveTab('papers')}
              className={`tab-btn ${activeTab === 'papers' ? 'active' : ''}`}
            >
              {t.tabReview}
            </button>
          </div>

          <div className="header-right-actions">
            <button onClick={handleLanguageToggle} className="btn-language-toggle">
              🌐 {state.language === 'cn' ? 'English' : '简体中文'}
            </button>
            {!state.funding && (
              <div className="header-alert warning">
                {t.alertOutFunds}
              </div>
            )}
          </div>
        </header>

        {/* Tabs Area */}
        <div className="tab-pane">
          {/* Office Tab */}
          {activeTab === 'office' && (
            <div className="office-tab">
              {!project || project.status !== "Active" ? (
                <section className="init-project-section glass-card">
                  <h2>{t.launchTitle}</h2>
                  <p className="info-desc">
                    {t.launchDesc}
                  </p>
                  
                  <div className="trending-topics-list">
                    <h4>{t.trendingTitle}</h4>
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
                    <h4>{t.customTitle}</h4>
                    <div className="input-row">
                      <input
                        type="text"
                        placeholder={t.placeholderCustom}
                        value={customTopic}
                        onChange={(e) => setCustomTopic(e.target.value)}
                      />
                      <button
                        onClick={() => handleInitProject(customTopic)}
                        className="btn-primary"
                        disabled={!customTopic.trim() || loading}
                      >
                        {t.launchBtn}
                      </button>
                    </div>
                  </div>
                </section>
              ) : (
                <div className="active-lab-view">
                  {/* Students Grid */}
                  <section className="students-section">
                    <h2>{t.studentsTitle}</h2>
                    <div className="students-grid">
                      {state.students.map((student) => {
                        // Color pills
                        const statusColors = {
                          "Idle": "idle", "空闲": "idle",
                          "Resting": "resting", "休息中": "resting",
                          "Searching ArXiv": "searching", "文献检索": "searching",
                          "Writing Proposal": "proposal", "撰写开题报告": "proposal",
                          "Awaiting PI Approval": "approval", "等待教授审批": "approval",
                          "Experimenting": "experiment", "实验中": "experiment",
                          "Writing Draft": "writing", "撰写论文": "writing"
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
                              <span className="label">🔋 {state.language === 'cn' ? '精力' : 'Energy'}</span>
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
                                <span className="label">{state.language === 'cn' ? '研究' : 'Research'}</span>
                                <span className="val">{(student.skills.research * 10).toFixed(0)}</span>
                              </div>
                              <div className="skill-item">
                                <span className="label">{state.language === 'cn' ? '代码' : 'Coding'}</span>
                                <span className="val">{(student.skills.coding * 10).toFixed(0)}</span>
                              </div>
                              <div className="skill-item">
                                <span className="label">{state.language === 'cn' ? '写作' : 'Writing'}</span>
                                <span className="val">{(student.skills.writing * 10).toFixed(0)}</span>
                              </div>
                            </div>

                            <div className="activity">
                              <strong>{state.language === 'cn' ? '动态' : 'Current'}:</strong> {student.activity}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </section>

                  {/* Student Workspace (Logs/Thoughts/Intervention) */}
                  {currentStudentObj && (
                    <section className="student-workspace glass-card">
                      <h2>{currentStudentObj.name}{t.workspaceTitle}</h2>
                      <div className="workspace-layout">
                        <div className="thought-stream">
                          <h4>{t.monologueTitle}</h4>
                          <div className="logs-box">
                            {currentStudentObj.thoughts.length === 0 ? (
                              <p className="empty-text">{t.emptyThoughts}</p>
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
                          <h4>{t.piGuidance}</h4>
                          <p className="help-text">{t.guidanceDesc}</p>
                          <div className="input-row">
                            <input
                              type="text"
                              placeholder={t.placeholderIntervene}
                              value={interveneMsg}
                              onChange={(e) => setInterveneMsg(e.target.value)}
                            />
                            <button
                              onClick={() => handleIntervene(currentStudentObj.name)}
                              className="btn-primary"
                              disabled={!interveneMsg.trim()}
                            >
                              {t.sendInstruction}
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
              <h2>{t.meetingTitle}</h2>
              <p className="info-desc">{t.meetingDesc}</p>

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
                  placeholder={t.chatPlaceholder}
                  value={chatMsg}
                  onChange={(e) => setChatMsg(e.target.value)}
                />
                <button type="submit" className="btn-primary">{t.chatSend}</button>
              </form>
            </div>
          )}

          {/* Drafts Tab */}
          {activeTab === 'papers' && (
            <div className="papers-tab">
              {/* Approvals Gate */}
              {state.pending_approvals && state.pending_approvals.length > 0 && (
                <div className="review-alert-card glass-card">
                  <h3>{t.reviewRequired}</h3>
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
                      placeholder={t.placeholderFeedback}
                      value={feedbackMsg}
                      onChange={(e) => setFeedbackMsg(e.target.value)}
                    />
                    <div className="action-buttons">
                      <button
                        onClick={() => handleApproveProposal('approve')}
                        className="btn-success"
                        disabled={loading}
                      >
                        {t.approveBtn}
                      </button>
                      <button
                        onClick={() => handleApproveProposal('reject')}
                        className="btn-danger"
                        disabled={loading}
                      >
                        {t.rejectBtn}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Submission Gate */}
              {project && (project.stage === "Awaiting Submission" || project.stage === "等待提交投稿") && (
                <div className="submission-card glass-card">
                  <h3>{t.submitTitle}</h3>
                  <p className="info-desc">{t.submitDesc}</p>
                  
                  <div className="submission-row">
                    <div className="conf-select">
                      <label>{t.venueLabel}</label>
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
                      {t.submitBtn}
                    </button>
                  </div>
                </div>
              )}

              {/* Peer Review Output */}
              {project && project.reviews && (
                <div className="reviews-card glass-card">
                  <h3>{t.reviewsTitle}</h3>
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
                  <h2>{t.filesTitle}</h2>
                  <p className="info-desc">{t.filesDesc}</p>

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
                        <h4>📝 paper.md</h4>
                        <div className="file-viewer">
                          <pre>{project.paper_draft}</pre>
                        </div>
                      </div>
                    )}

                    {!project.proposal_draft && !project.experiment_results && !project.paper_draft && (
                      <p className="empty-text">{t.emptyFiles}</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="glass-card">
                  <p className="empty-text">{t.noProject}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Global Logs Panel */}
      <section className="global-logs-panel glass-card">
        <h3>📢 {state.language === 'cn' ? '实验室事件日志' : 'Lab Event Logs'}</h3>
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
