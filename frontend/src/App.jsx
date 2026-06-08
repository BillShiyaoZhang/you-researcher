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
    budget: "实验室经费 (元)",
    reputation: "实验室声望",
    simDay: "模拟天数",
    activeProject: "进行中课题",
    noProject: "暂无课题。请在办公室启动一个新项目。",
    tabOffice: "👥 办公室 & 实验室",
    tabMeeting: "💬 学术通讯录",
    tabReview: "📄 论文评审与文档",
    launchTitle: "启动新科研项目",
    launchDesc: "输入您的学术研究课题，或选择以下一个热门方向，指派给您的 PhD 学生开展研究。",
    trendingTitle: "选择热门研究方向：",
    customTitle: "或者输入完全自定义课题：",
    launchBtn: "启动课题",
    placeholderCustom: "例如：在卷积骨干网络中应用低秩适配器(LoRA)...",
    studentsTitle: "科研团队 (PhD 学生)",
    workspaceTitle: "的专属工作区",
    monologueTitle: "内心独白 / 运行日志",
    emptyThoughts: "目前还没有记录想法。给该学生发私信或群聊讨论来唤醒它吧。",
    piGuidance: "私聊对话通道",
    guidanceDesc: "向该学生发送私聊指令。对话将自动记录在通讯录『私聊』频道中。",
    placeholderIntervene: "输入私信内容...",
    sendInstruction: "发送私信",
    meetingTitle: "实验室群聊学术讨论",
    chatPlaceholder: "向频道发送消息：例如“关于数值发散问题，Alice 你怎么看？”",
    chatSend: "发送消息",
    reviewRequired: "⚠️ 科研审批与共享中心",
    approveBtn: "同意申请 ✓",
    rejectBtn: "驳回申请 ✗",
    placeholderFeedback: "添加驳回原因或修改意见...",
    submitTitle: "🚀 学术手稿投稿与同行评审",
    submitDesc: "论文手稿已撰写完毕，双盲评审投稿需要从经费中扣除注册费。",
    venueLabel: "选择投稿会议：",
    submitBtn: "提交手稿投稿",
    reviewsTitle: "📬 盲审评审报告 (Blind Review)",
    filesTitle: "工作区生成文件",
    emptyFiles: "工作区尚未生成任何文件。",
    settingsBtn: "⚙️ 实验室设置",
    settingsTitle: "实验室运行参数设置",
    llmProvider: "大模型服务商",
    apiKey: "API Key 密钥",
    apiBase: "API Base 地址 (可选)",
    modelName: "具体模型名称",
    fundingMode: "经费扣款模式",
    fundingSim: "模拟经费 (虚拟 ¥50w 精确计费)",
    fundingReal: "绑定真实 API 账户余额 (即时同步)",
    autoMode: "自主协同协作模式",
    autoModeDesc: "开启后，Agent 之间的文件共享与沙箱运行将完全自动化，直到任务结束或经费超支。",
    maxCost: "单次会话最大经费额度限制 (元)",
    saveSettings: "保存设置",
    resetConfirm: "确定要重置实验室吗？所有当前的实验室进度和成果都将丢失。",
    sessionCostLabel: "当前会话消耗 (元)"
  },
  en: {
    title: "PI Simulator",
    subtitle: "Agentic Research Lab",
    budget: "Budget (RMB)",
    reputation: "Reputation",
    simDay: "Simulation Day",
    activeProject: "Active Project",
    noProject: "No active project. Launch one in the Office.",
    tabOffice: "👥 Office & Lab Room",
    tabMeeting: "💬 Contact Channels",
    tabReview: "📄 Reviews & Documents",
    launchTitle: "Launch New Research Project",
    launchDesc: "Enter a research question or select one of the trending topics to assign to your students.",
    trendingTitle: "Select a Trending Topic:",
    customTitle: "Or enter a fully custom topic:",
    launchBtn: "Launch Project",
    placeholderCustom: "e.g., Implementing Low-rank adapters for Convolutional backbones...",
    studentsTitle: "Research Students",
    workspaceTitle: "'s Isolated Workspace",
    monologueTitle: "Internal Monologue / Logs",
    emptyThoughts: "No thoughts recorded yet. Send them a message to wake them up.",
    piGuidance: "Private Chat Channel",
    guidanceDesc: "Send a private message to this student. The chat history is kept under their Private Channel.",
    placeholderIntervene: "Type private message...",
    sendInstruction: "Send Private",
    meetingTitle: "Lab Group Chat",
    chatPlaceholder: "Type message: e.g. 'Alice, how should we handle training instability?'",
    chatSend: "Send Message",
    reviewRequired: "⚠️ Approval & Sharing Hub",
    approveBtn: "Approve ✓",
    rejectBtn: "Reject & Request Revisions ✗",
    placeholderFeedback: "Add reasons or feedback for rejection...",
    submitTitle: "🚀 Conference Submission",
    submitDesc: "Manuscript is finalized! Submit the draft for double-blind peer review.",
    venueLabel: "Select Venue:",
    submitBtn: "Submit Manuscript",
    reviewsTitle: "📬 Peer Review Reports",
    filesTitle: "Workspace Files",
    emptyFiles: "No files generated yet.",
    settingsBtn: "⚙️ Lab Settings",
    settingsTitle: "Configure LLM & Autonomous Parameters",
    llmProvider: "LLM Provider",
    apiKey: "API Key",
    apiBase: "API Base URL (Optional)",
    modelName: "Model Name",
    fundingMode: "Funding Accounting Mode",
    fundingSim: "Simulated Funding (¥500k precise token billing)",
    fundingReal: "Real API Balance Binding (Synchronized)",
    autoMode: "Fully Autonomous Mode",
    autoModeDesc: "When enabled, file transfers & sandbox runs execute automatically up to the cost budget limit.",
    maxCost: "Session Cost Limit (RMB)",
    saveSettings: "Save Configuration",
    resetConfirm: "Are you sure you want to reset the lab? All progress will be lost.",
    sessionCostLabel: "Current Session Cost (RMB)"
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
  const [activeChannelId, setActiveChannelId] = useState('group');

  // Settings Modal States
  const [showSettings, setShowSettings] = useState(false);
  const [provider, setProvider] = useState('openai');
  const [apiKey, setApiKey] = useState('');
  const [apiBase, setApiBase] = useState('');
  const [model, setModel] = useState('gpt-3.5-turbo');
  const [autoMode, setAutoMode] = useState(false);
  const [maxCost, setMaxCost] = useState(10.0);
  const [fundingMode, setFundingMode] = useState('simulated');
  const [connectionStatus, setConnectionStatus] = useState(null); // null, 'testing', 'success', 'warning', 'error'
  const [connectionMsg, setConnectionMsg] = useState('');
  const [connectionOk, setConnectionOk] = useState(false);
  const [balanceAvailable, setBalanceAvailable] = useState(false);

  // Workspace File Explorer & Commenting States
  const [workspaceFiles, setWorkspaceFiles] = useState([]);
  const [activeFile, setActiveFile] = useState(null);
  const [commentText, setCommentText] = useState('');
  
  // Rejection feedback state
  const [feedbackMsg, setFeedbackMsg] = useState('');
  const [selectedConf, setSelectedConf] = useState(CONFERENCES[0].name);

  // Poll state every 3 seconds
  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchFiles = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/game/files`);
      if (res.ok) {
        const data = await res.json();
        setWorkspaceFiles(data);
        if (activeFile) {
          const updated = data.find(f => f.name === activeFile.name && f.student === activeFile.student);
          if (updated) setActiveFile(updated);
        }
      }
    } catch (err) {
      console.error("Failed to fetch workspace files", err);
    }
  };
  const fetchState = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/game/state`);
      if (!res.ok) throw new Error("Failed to fetch game state");
      const data = await res.json();
      setState(data);
      setSelectedStudent(prev => prev || (data.students && data.students.length > 0 ? data.students[0].name : null));
      fetchFiles();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleOpenSettings = () => {
    if (state) {
      setProvider(state.llm_config.provider);
      setApiKey(state.llm_config.api_key);
      setApiBase(state.llm_config.base_url || '');
      setModel(state.llm_config.model);
      setAutoMode(state.autonomous_mode);
      setMaxCost(state.max_cost_limit);
      setFundingMode(state.funding_mode);

      if (state.llm_config.api_key) {
        setConnectionOk(true);
        setBalanceAvailable(state.funding_mode === 'real' || !!state.llm_config.api_key);
        setConnectionStatus(null);
      } else {
        setConnectionOk(false);
        setBalanceAvailable(false);
        setConnectionStatus(null);
      }
    }
    setShowSettings(true);
  };

  const handleTestConnection = async () => {
    setConnectionStatus('testing');
    setConnectionMsg(state.language === 'cn' ? '正在测试大模型连通性...' : 'Testing LLM connectivity...');
    try {
      const res = await fetch(`${API_BASE}/api/game/check_connection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          api_key: apiKey,
          base_url: apiBase,
          model
        })
      });
      if (!res.ok) throw new Error("Connection check request failed");
      const data = await res.json();
      
      if (data.status === 'ok') {
        setConnectionOk(true);
        setBalanceAvailable(data.has_balance);
        setConnectionStatus(data.has_balance ? 'success' : 'warning');
        setConnectionMsg(data.message);
        if (!data.has_balance) {
          setFundingMode('simulated');
        }
      } else {
        setConnectionOk(false);
        setConnectionStatus('error');
        setConnectionMsg(data.message);
      }
    } catch (err) {
      setConnectionOk(false);
      setConnectionStatus('error');
      setConnectionMsg(err.message);
    }
  };

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          api_key: apiKey,
          base_url: apiBase,
          model,
          autonomous_mode: autoMode,
          max_cost_limit: Number(maxCost),
          funding_mode: fundingMode
        })
      });
      if (!res.ok) throw new Error("Failed to save settings");
      const data = await res.json();
      setState(data);
      setShowSettings(false);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!commentText.trim() || !activeFile) return;
    try {
      const res = await fetch(`${API_BASE}/api/game/comment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: activeFile.name, student: activeFile.student, comment: commentText })
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Comment submission failed");
      }
      setCommentText('');
      fetchFiles();
    } catch (err) {
      alert(err.message);
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

  const handleSendChannelMsg = async (e) => {
    e.preventDefault();
    if (!chatMsg.trim()) return;
    const msg = chatMsg;
    setChatMsg('');
    try {
      const res = await fetch(`${API_BASE}/api/game/channels/${activeChannelId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      if (!res.ok) throw new Error("Failed to send message");
      const data = await res.json();
      setState(data);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleIntervenePrivate = async (studentName) => {
    if (!chatMsg.trim()) return;
    const msg = chatMsg;
    setChatMsg('');
    const channelId = studentName.toLowerCase();
    try {
      const res = await fetch(`${API_BASE}/api/game/channels/${channelId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      if (!res.ok) throw new Error("Private intervention failed");
      const data = await res.json();
      setState(data);
      setActiveChannelId(channelId);
      setActiveTab('meeting');
    } catch (err) {
      alert(err.message);
    }
  };

  const handleApprovalSubmit = async (approvalId, decision) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approval_id: approvalId,
          decision,
          feedback: decision === 'reject' ? feedbackMsg : selectedConf
        })
      });
      if (!res.ok) throw new Error("Approval processing failed");
      const data = await res.json();
      setState(data);
      setFeedbackMsg('');
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
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
      setActiveChannelId('group');
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

  const t = TRANSLATIONS[state.language || 'cn'];
  const project = state.current_project;
  const currentStudentObj = state.students.find(s => s.name === selectedStudent);
  const activeChannelObj = state.channels.find(c => c.id === activeChannelId);

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
              <span className={`billing-badge ${state.funding_mode}`}>
                {state.funding_mode === 'real' ? 'Real API' : 'Simulated'}
              </span>
            </div>
            <div className="stat-val">¥{state.funding.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          </div>
          <div className="stat-card">
            <div className="stat-header">
              <span>🏆 {t.reputation}</span>
            </div>
            <div className="stat-val">{state.reputation.toFixed(1)}</div>
          </div>
          <div className="stat-card">
            <div className="stat-header">
              <span>{t.sessionCostLabel}</span>
            </div>
            <div className="stat-val text-orange">¥{state.session_cost.toFixed(4)}</div>
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
          <button onClick={handleOpenSettings} className="btn-settings">
            {t.settingsBtn}
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
              onClick={() => {
                setActiveTab('meeting');
                // clear unread status when switching
                if (activeChannelId) {
                  fetch(`${API_BASE}/api/game/channels/${activeChannelId}/read`, { method: 'POST' });
                }
              }}
              className={`tab-btn ${activeTab === 'meeting' ? 'active' : ''}`}
            >
              {t.tabMeeting}
              {state.channels.some(c => c.unread) && <span className="unread-dot-badge">●</span>}
            </button>
            <button
              onClick={() => setActiveTab('papers')}
              className={`tab-btn ${activeTab === 'papers' ? 'active' : ''}`}
            >
              {t.tabReview}
              {state.pending_approvals.length > 0 && (
                <span className="count-badge">{state.pending_approvals.length}</span>
              )}
            </button>
          </div>

          <div className="header-right-actions">
            <button onClick={handleLanguageToggle} className="btn-language-toggle">
              🌐 {state.language === 'cn' ? 'English' : '简体中文'}
            </button>
          </div>
        </header>

        {/* Main Body Layout */}
        <div className="main-body-layout">
          <div className="tab-pane-container">
            <div className="tab-pane">
              
              {/* Office Tab */}
              {activeTab === 'office' && (
                <div className="office-tab">
                  {!project || project.status !== "Active" ? (
                    <section className="init-project-section glass-card">
                      <h2>{t.launchTitle}</h2>
                      <p className="info-desc">{t.launchDesc}</p>
                      
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
                      <h2>{t.studentsTitle}</h2>
                      <div className="students-grid">
                        {state.students.map((student) => {
                          const statusColors = {
                            "Idle": "idle", "空闲": "idle",
                            "Resting": "resting", "休息中": "resting",
                            "Searching ArXiv": "searching", "文献检索": "searching",
                            "Writing Proposal": "proposal", "撰写开题报告": "proposal",
                            "Awaiting PI Approval": "approval", "等待教授审批": "approval",
                            "Awaiting Approval": "approval", "等待审批": "approval",
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

                      {/* Selected Student Workspace Panel */}
                      {currentStudentObj && (
                        <section className="student-workspace glass-card">
                          <h2>{currentStudentObj.name}{t.workspaceTitle}</h2>
                          <div className="workspace-layout">
                            <div className="workspace-files-column">
                              <h4>📁 {t.filesTitle}</h4>
                              <div className="student-file-list">
                                {workspaceFiles.filter(f => f.student === currentStudentObj.name).length === 0 ? (
                                  <p className="empty-text">{t.emptyFiles}</p>
                                ) : (
                                  workspaceFiles.filter(f => f.student === currentStudentObj.name).map(file => (
                                    <div
                                      key={file.name}
                                      className="student-file-item"
                                      onClick={() => setActiveFile(file)}
                                    >
                                      📄 {file.name}
                                      {file.comments && file.comments.length > 0 && (
                                        <span className="file-comment-indicator">💬 {file.comments.length}</span>
                                      )}
                                    </div>
                                  ))
                                )}
                              </div>
                            </div>
                            
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
                                  value={chatMsg}
                                  onChange={(e) => setChatMsg(e.target.value)}
                                />
                                <button
                                  onClick={() => handleIntervenePrivate(currentStudentObj.name)}
                                  className="btn-primary"
                                  disabled={!chatMsg.trim()}
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

              {/* Chat Channels Tab */}
              {activeTab === 'meeting' && (
                <div className="channels-room glass-card">
                  <div className="channels-layout">
                    {/* Contacts list */}
                    <aside className="contacts-sidebar">
                      <h3>💬 {state.language === 'cn' ? '通讯录' : 'Channels'}</h3>
                      <div className="contacts-list">
                        {state.channels.map(ch => (
                          <div
                            key={ch.id}
                            className={`contact-item ${activeChannelId === ch.id ? 'active' : ''}`}
                            onClick={() => {
                              setActiveChannelId(ch.id);
                              // clear unread state
                              fetch(`${API_BASE}/api/game/channels/${ch.id}/read`, { method: 'POST' });
                            }}
                          >
                            <span className="contact-name">
                              {ch.id === 'group' ? '👥' : '👤'} {ch.name}
                            </span>
                            {ch.unread && <span className="unread-dot"></span>}
                          </div>
                        ))}
                      </div>
                    </aside>

                    {/* Chat box */}
                    <section className="chat-window">
                      {activeChannelObj ? (
                        <>
                          <div className="chat-window-header">
                            <h4>{activeChannelObj.name}</h4>
                          </div>

                          <div className="chat-messages-box">
                            {activeChannelObj.messages.map((msg, i) => {
                              let bubbleClass = "chat-student";
                              if (msg.sender === "PI") bubbleClass = "chat-pi";
                              else if (msg.sender === "System") bubbleClass = "chat-system";

                              return (
                                <div key={msg.id || i} className={`chat-message ${bubbleClass}`}>
                                  <div className="message-header">
                                    <strong>{msg.sender}</strong>
                                    {msg.role && <span className="role-tag">({msg.role})</span>}
                                  </div>
                                  <p className="message-content">{msg.message}</p>
                                </div>
                              );
                            })}
                          </div>

                          <form onSubmit={handleSendChannelMsg} className="chat-form">
                            <input
                              type="text"
                              placeholder={t.chatPlaceholder}
                              value={chatMsg}
                              onChange={(e) => setChatMsg(e.target.value)}
                            />
                            <button type="submit" className="btn-primary">{t.chatSend}</button>
                          </form>
                        </>
                      ) : (
                        <div className="empty-chat-message">
                          <p>Select a channel from the contact list to start discussion.</p>
                        </div>
                      )}
                    </section>
                  </div>
                </div>
              )}

              {/* Review & Approvals Tab */}
              {activeTab === 'papers' && (
                <div className="papers-tab">
                  {state.pending_approvals && state.pending_approvals.length > 0 ? (
                    <div className="approvals-container">
                      <h2>{t.reviewRequired}</h2>
                      {state.pending_approvals.map((approval) => (
                        <div key={approval.id} className="review-alert-card glass-card">
                          <div className="approval-card-header">
                            <h3>{approval.title}</h3>
                            <span className="approval-badge-type">{approval.type}</span>
                          </div>
                          <p className="desc">{approval.description}</p>
                          
                          {approval.content && (
                            <pre className="code-view-box">{approval.content}</pre>
                          )}

                          <div className="approval-actions-form">
                            {approval.type === 'paper_submission' && (
                              <div className="venue-row">
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
                            )}

                            {approval.type !== 'paper_submission' && (
                              <input
                                type="text"
                                placeholder={t.placeholderFeedback}
                                value={feedbackMsg}
                                onChange={(e) => setFeedbackMsg(e.target.value)}
                              />
                            )}

                            <div className="action-buttons">
                              <button
                                onClick={() => handleApprovalSubmit(approval.id, 'approve')}
                                className="btn-success"
                                disabled={loading}
                              >
                                {t.approveBtn}
                              </button>
                              <button
                                onClick={() => handleApprovalSubmit(approval.id, 'reject')}
                                className="btn-danger"
                                disabled={loading}
                              >
                                {t.rejectBtn}
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="glass-card empty-approvals">
                      <p>✨ Currently there are no approvals pending. Your students are working autonomously.</p>
                    </div>
                  )}

                  {/* Peer Review reports */}
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
                </div>
              )}
            </div>
          </div>

          {/* Right Side Global Workspace Explorer */}
          <aside className="file-browser-panel">
            <div className="file-browser-header">
              <span>📁</span>
              <h3>{state.language === 'cn' ? '全局实验室文件' : 'Lab Workspace Files'}</h3>
            </div>

            <div className="file-list">
              {workspaceFiles.length === 0 ? (
                <p className="empty-text" style={{ padding: '20px' }}>{state.language === 'cn' ? '工作区为空。' : 'Workspace is empty.'}</p>
              ) : (
                workspaceFiles.map((file) => (
                  <div
                    key={`${file.student}/${file.name}`}
                    className={`file-item ${activeFile && activeFile.name === file.name && activeFile.student === file.student ? 'selected' : ''}`}
                    onClick={() => setActiveFile(file)}
                  >
                    <div className="file-item-header">
                      <span className="name">📄 {file.name}</span>
                      <span className="student-owner-badge">{file.student}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </aside>
        </div>
      </main>

      {/* Settings Modal */}
      {showSettings && (
        <div className="file-modal-overlay">
          <div className="file-modal settings-modal" onClick={(e) => e.stopPropagation()}>
            <div className="file-modal-header">
              <h3>⚙️ {t.settingsTitle}</h3>
              <button className="btn-close" onClick={() => setShowSettings(false)}>✕</button>
            </div>
            
            <form onSubmit={handleSaveSettings} className="settings-form">
              <div className="form-group">
                <label>{t.llmProvider}</label>
                <select value={provider} onChange={(e) => { setProvider(e.target.value); setConnectionOk(false); setConnectionStatus(null); }}>
                  <option value="openai">OpenAI</option>
                  <option value="minimax">MiniMax</option>
                  <option value="deepseek">DeepSeek</option>
                  <option value="siliconflow">Silicon Flow</option>
                  <option value="custom">Custom Endpoint</option>
                </select>
              </div>

              <div className="form-group">
                <label>{t.apiKey}</label>
                <input
                  type="password"
                  placeholder="sk-..."
                  value={apiKey}
                  onChange={(e) => { setApiKey(e.target.value); setConnectionOk(false); setConnectionStatus(null); }}
                />
              </div>

              <div className="form-group">
                <label>{t.apiBase}</label>
                <input
                  type="text"
                  placeholder="https://api.openai.com/v1"
                  value={apiBase}
                  onChange={(e) => { setApiBase(e.target.value); setConnectionOk(false); setConnectionStatus(null); }}
                />
              </div>

              <div className="form-group">
                <label>{t.modelName}</label>
                <input
                  type="text"
                  placeholder="gpt-3.5-turbo"
                  value={model}
                  onChange={(e) => { setModel(e.target.value); setConnectionOk(false); setConnectionStatus(null); }}
                />
              </div>

              <div className="form-group connection-test-section">
                <button
                  type="button"
                  className="btn-tick"
                  style={{ background: '#475569', boxShadow: 'none', padding: '10px 14px', fontSize: '0.9rem' }}
                  onClick={handleTestConnection}
                  disabled={connectionStatus === 'testing'}
                >
                  {connectionStatus === 'testing' ? (state.language === 'cn' ? '正在测试...' : 'Testing...') : (state.language === 'cn' ? '⚡ 测试连通性' : '⚡ Test Connection')}
                </button>
                
                {connectionStatus && (
                  <div className={`connection-message-box ${connectionStatus}`} style={{ marginTop: '8px', padding: '10px', borderRadius: '6px', fontSize: '0.85rem', lineHeight: '1.4' }}>
                    {connectionMsg}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label>{t.fundingMode}</label>
                <div className="radio-group">
                  <label>
                    <input
                      type="radio"
                      name="fundingMode"
                      value="simulated"
                      checked={fundingMode === 'simulated'}
                      onChange={() => setFundingMode('simulated')}
                    />
                    {t.fundingSim}
                  </label>
                  <label style={{ opacity: (balanceAvailable && connectionOk) ? 1 : 0.5 }}>
                    <input
                      type="radio"
                      name="fundingMode"
                      value="real"
                      checked={fundingMode === 'real'}
                      disabled={!balanceAvailable || !connectionOk}
                      onChange={() => setFundingMode('real')}
                    />
                    {t.fundingReal}
                    {(!balanceAvailable || !connectionOk) && (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginLeft: '6px', fontWeight: 'normal' }}>
                        ({state.language === 'cn' ? '需先测试连通性并成功获取余额' : 'requires successful connection check'})
                      </span>
                    )}
                  </label>
                </div>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={autoMode}
                    onChange={(e) => setAutoMode(e.target.checked)}
                  />
                  <strong>{t.autoMode}</strong>
                </label>
                <p className="help-text">{t.autoModeDesc}</p>
              </div>

              {autoMode && (
                <div className="form-group">
                  <label>{t.maxCost}</label>
                  <input
                    type="number"
                    step="0.1"
                    value={maxCost}
                    onChange={(e) => setMaxCost(e.target.value)}
                  />
                </div>
              )}

              <button type="submit" className="btn-primary-large" disabled={loading || !connectionOk} style={{ opacity: connectionOk ? 1 : 0.5 }}>
                {t.saveSettings}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Overlay File Viewer and Commenting Modal */}
      {activeFile && (
        <div className="file-modal-overlay" onClick={() => setActiveFile(null)}>
          <div className="file-modal" onClick={(e) => e.stopPropagation()}>
            <div className="file-modal-header">
              <h3>📄 {activeFile.student} / {activeFile.name}</h3>
              <button className="btn-close" onClick={() => setActiveFile(null)}>✕</button>
            </div>
            
            <div className="file-modal-body">
              <div className="file-content-pane">
                <pre>{activeFile.content}</pre>
              </div>
              
              <div className="comments-pane">
                <h4>💬 {state.language === 'cn' ? '批注与反馈列表' : 'Annotations & Feedback'}</h4>
                
                <div className="comments-list">
                  {activeFile.comments && activeFile.comments.length > 0 ? (
                    activeFile.comments.map((comment, idx) => (
                      <div key={idx} className="comment-bubble">
                        <div className="comment-author">{state.language === 'cn' ? '导师/教授 (PI)' : 'Professor (PI)'}</div>
                        <div>{comment}</div>
                      </div>
                    ))
                  ) : (
                    <p className="empty-text" style={{ fontSize: '0.8rem', padding: '10px 0' }}>
                      {state.language === 'cn' ? '暂无批注。在下方输入框可添加新批注，指导该学生修改此文件。' : 'No annotations. Add comments below to guide revisions.'}
                    </p>
                  )}
                </div>
                
                <form onSubmit={handleCommentSubmit} className="comment-input-area">
                  <textarea 
                    placeholder={state.language === 'cn' ? '输入批注修改要求（例如：“在引言中增加关于收敛阶的数学证明”）...' : 'Type feedback (e.g. "Add details to section 3")...'}
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                  />
                  <button type="submit" className="btn-primary" disabled={!commentText.trim()}>
                    {state.language === 'cn' ? '发表批注' : 'Add Comment'}
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}

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
