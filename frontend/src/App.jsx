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
    sessionCostLabel: "当前会话消耗 (元)",
    btnProjectManager: "📁 课题项目管理",
    btnResetProject: "🔄 重置当前项目",
    resetProjectConfirm: "确定要重置当前正在进行的课题吗？当前课题的经费、天数、学生状态和工作区文件都将被重置为第1天，但保留该课题研究方向。此操作不可撤销！",
    projectManagerTitle: "项目管理器 (课题存档管理)",
    projectListHeader: "历史课题与进行中课题列表",
    thTopic: "课题名称 / 研究方向",
    thStage: "当前阶段",
    thDay: "模拟天数",
    thFunding: "剩余经费",
    thReputation: "声望",
    thLastSaved: "上次自动保存时间",
    thActions: "操作",
    btnLoad: "加载存档",
    btnDelete: "删除存档",
    btnCreateNewProject: "🆕 新建课题项目",
    createNewConfirm: "确定要新建一个课题项目吗？当前进行中的项目进度与工作区文件将自动保存。您可以随时从项目管理器中重新加载它。",
    loadConfirm: "确定要加载此项目吗？加载前会自动保存当前进行中项目的最新进度。加载后将切换到选定项目的进度、学生和工作区文件。",
    deleteConfirm: "确定要彻底删除该项目吗？这会永久删除其所有存档数据和工作区文件。此操作不可逆！",
    activeBadge: "进行中",
    noProjects: "暂无历史项目存档。",
    btnRecruitStudent: "➕ 招募科研学生",
    btnDismissStudent: "Dismiss / 退出实验室",
    dismissConfirm: "确定要将学生 {name} 移出实验室吗？这会将其移出团队和群聊。但其个人工作区文件夹（包含所有生成的代码和日志文件）仍然会完整保留，不会丢失任何研究成果。",
    recruitModalTitle: "招募新实验室成员 (PhD 学生)",
    labelPreset: "选择学生职位预设",
    presetDataEng: "数据工程师 (Data Engineer)",
    presetTheoAnalyst: "理论分析师 (Theoretical Analyst)",
    presetMLDev: "机器学习开发 (ML Dev)",
    presetWriter: "学术论文写手 (Academic Writer)",
    presetCustom: "自定义职位 (Custom Role)",
    labelName: "学生姓名",
    labelRole: "科研角色 (Role Title)",
    labelSkills: "专业技能分布 (0 - 10分)",
    labelResearch: "研究 (Research)",
    labelCoding: "编码 (Coding)",
    labelWriting: "写作 (Writing)",
    labelPersonality: "性格与背景特征 (Personality Profile)",
    placeholderName: "例如：David",
    placeholderRole: "例如：强化学习工程师",
    placeholderPersonality: "例如：做事严谨，性格活跃，偏好快速实验，常用Emoji表达情绪。",
    btnRecruitSubmit: "确认录用并招募入所",
    validationNameEmpty: "学生姓名不能为空！",
    validationRoleEmpty: "角色标签不能为空！",
    validationNameExists: "该姓名的学生已在实验团队中。"
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
    sessionCostLabel: "Current Session Cost (RMB)",
    btnProjectManager: "📁 Project Manager",
    btnResetProject: "🔄 Reset Current Project",
    resetProjectConfirm: "Are you sure you want to reset the current active project? The budget, day, student statuses, and workspace files will be reset to Day 1, keeping the same topic. This action cannot be undone!",
    projectManagerTitle: "Project Manager (Saves & Progression)",
    projectListHeader: "All Active & Historical Projects",
    thTopic: "Research Topic / Question",
    thStage: "Stage",
    thDay: "Day",
    thFunding: "Budget Left",
    thReputation: "Reputation",
    thLastSaved: "Last Auto-Saved",
    thActions: "Actions",
    btnLoad: "Load Save",
    btnDelete: "Delete Save",
    btnCreateNewProject: "🆕 Create New Project",
    createNewConfirm: "Are you sure you want to create a new project? The current active project's progress and workspace files will be saved automatically, and you can reload it anytime.",
    loadConfirm: "Are you sure you want to load this project? The current project's progress will be saved automatically. Loading will switch you to the selected project's state, students, and workspace files.",
    deleteConfirm: "Are you sure you want to delete this project? This will permanently delete all its saved data and workspace files. This action cannot be undone!",
    activeBadge: "Active Now",
    noProjects: "No historical projects found.",
    btnRecruitStudent: "➕ Recruit PhD Student",
    btnDismissStudent: "Dismiss / Exit Lab",
    dismissConfirm: "Are you sure you want to dismiss {name}? This will remove them from the team and channels. However, their workspace directory (containing all code and results) will be preserved on disk so no research data is lost.",
    recruitModalTitle: "Recruit PhD Student",
    labelPreset: "Select Student Preset",
    presetDataEng: "Data Engineer",
    presetTheoAnalyst: "Theoretical Analyst",
    presetMLDev: "ML Dev",
    presetWriter: "Academic Writer",
    presetCustom: "Custom Role",
    labelName: "Student Name",
    labelRole: "Role Title",
    labelSkills: "Skill distribution (0 - 10)",
    labelResearch: "Research",
    labelCoding: "Coding",
    labelWriting: "Writing",
    labelPersonality: "Personality Profile & Preferences",
    placeholderName: "e.g., David",
    placeholderRole: "e.g., RL Engineer",
    placeholderPersonality: "e.g., Very detail-oriented, energetic, likes running quick experiments.",
    btnRecruitSubmit: "Confirm Hire & Recruit",
    validationNameEmpty: "Student name cannot be empty!",
    validationRoleEmpty: "Role title cannot be empty!",
    validationNameExists: "A student with this name is already in the lab."
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

  // Project Manager States
  const [showProjectManager, setShowProjectManager] = useState(false);
  const [historicalProjects, setHistoricalProjects] = useState([]);

  // Student Recruitment States
  const [showRecruitModal, setShowRecruitModal] = useState(false);
  const [recruitPreset, setRecruitPreset] = useState('data_engineer');
  const [recruitName, setRecruitName] = useState('');
  const [recruitRole, setRecruitRole] = useState('Data Engineer');
  const [recruitResearch, setRecruitResearch] = useState(0.5);
  const [recruitCoding, setRecruitCoding] = useState(0.9);
  const [recruitWriting, setRecruitWriting] = useState(0.4);
  const [recruitPersonality, setRecruitPersonality] = useState('');

  const handleOpenRecruitModal = () => {
    setRecruitPreset('data_engineer');
    setRecruitName('');
    setRecruitRole(state.language === 'cn' ? '数据工程师' : 'Data Engineer');
    setRecruitResearch(0.5);
    setRecruitCoding(0.9);
    setRecruitWriting(0.4);
    setRecruitPersonality(state.language === 'cn' ? '做事非常有逻辑，擅长处理庞大复杂的数据清洗与流水线构建。' : 'Highly logical, excels at data cleaning pipelines.');
    setShowRecruitModal(true);
  };

  const handlePresetChange = (preset) => {
    setRecruitPreset(preset);
    const isCn = state.language === 'cn';
    if (preset === 'data_engineer') {
      setRecruitRole(isCn ? '数据工程师' : 'Data Engineer');
      setRecruitResearch(0.5);
      setRecruitCoding(0.9);
      setRecruitWriting(0.4);
      setRecruitPersonality(isCn ? '做事非常有逻辑，擅长处理庞大复杂的数据清洗与流水线构建。' : 'Highly logical, excels at data cleaning pipelines.');
    } else if (preset === 'theoretical_analyst') {
      setRecruitRole(isCn ? '理论分析师' : 'Theoretical Analyst');
      setRecruitResearch(0.9);
      setRecruitCoding(0.4);
      setRecruitWriting(0.9);
      setRecruitPersonality(isCn ? '学术严谨，喜欢钻研数学证明与论文细节，说话较为正式。' : 'Rigorous academic, enjoys math proofs and paper details, speaks formally.');
    } else if (preset === 'ml_dev') {
      setRecruitRole(isCn ? '机器学习开发' : 'ML Dev');
      setRecruitResearch(0.6);
      setRecruitCoding(0.9);
      setRecruitWriting(0.5);
      setRecruitPersonality(isCn ? '代码极客，开发运行测试极快，喜欢尝试最新算法与架构。' : 'Code hacker, runs tests extremely fast, loves testing new models.');
    } else if (preset === 'academic_writer') {
      setRecruitRole(isCn ? '学术论文写手' : 'Academic Writer');
      setRecruitResearch(0.6);
      setRecruitCoding(0.5);
      setRecruitWriting(0.9);
      setRecruitPersonality(isCn ? '文字表达极佳，擅长将复杂的实验日志撰写成结构严整的学术论文。' : 'Excellent writing, excels at drafting papers from raw experiment results.');
    } else {
      setRecruitRole('');
      setRecruitResearch(0.5);
      setRecruitCoding(0.5);
      setRecruitWriting(0.5);
      setRecruitPersonality('');
    }
  };

  const handleRecruitSubmit = async (e) => {
    e.preventDefault();
    if (!recruitName.trim()) {
      alert(t.validationNameEmpty);
      return;
    }
    if (!recruitRole.trim()) {
      alert(t.validationRoleEmpty);
      return;
    }
    if (state.students.some(s => s.name.toLowerCase() === recruitName.trim().toLowerCase())) {
      alert(t.validationNameExists);
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/students/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: recruitName.trim(),
          role: recruitRole.trim(),
          skills: {
            research: Number(recruitResearch),
            coding: Number(recruitCoding),
            writing: Number(recruitWriting)
          },
          personality: recruitPersonality,
          preset_id: recruitPreset
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Recruitment failed");
      }

      const data = await res.json();
      setState(data);
      setSelectedStudent(recruitName.trim());
      setShowRecruitModal(false);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDismissStudent = async (studentName) => {
    const confirmMsg = t.dismissConfirm.replace("{name}", studentName);
    if (!window.confirm(confirmMsg)) return;

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/students/dismiss`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: studentName })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Dismissal failed");
      }

      const data = await res.json();
      setState(data);
      if (selectedStudent === studentName) {
        setSelectedStudent(data.students.length > 0 ? data.students[0].name : null);
      }
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalProjects = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/game/projects`);
      if (res.ok) {
        const data = await res.json();
        setHistoricalProjects(data);
      }
    } catch (err) {
      console.error("Failed to fetch historical projects", err);
    }
  };

  const handleOpenProjectManager = () => {
    fetchHistoricalProjects();
    setShowProjectManager(true);
  };

  const handleResetProject = async () => {
    if (!window.confirm(t.resetProjectConfirm)) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/projects/reset`, { method: 'POST' });
      if (!res.ok) throw new Error("Reset project failed");
      const data = await res.json();
      setState(data);
      if (data.students && data.students.length > 0) {
        setSelectedStudent(data.students[0].name);
      }
      setActiveChannelId('group');
      setActiveTab('office');
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNewProjectIntent = async () => {
    if (!window.confirm(t.createNewConfirm)) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/projects/new_intent`, { method: 'POST' });
      if (!res.ok) throw new Error("Creating new project failed");
      const data = await res.json();
      setState(data);
      setShowProjectManager(false);
      setActiveTab('office');
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadProject = async (projectId) => {
    if (!window.confirm(t.loadConfirm)) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/projects/load`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId })
      });
      if (!res.ok) throw new Error("Loading project failed");
      const data = await res.json();
      setState(data);
      if (data.students && data.students.length > 0) {
        setSelectedStudent(data.students[0].name);
      }
      setActiveChannelId('group');
      setShowProjectManager(false);
      setActiveTab('office');
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (!window.confirm(t.deleteConfirm)) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/game/projects/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId })
      });
      if (!res.ok) throw new Error("Deleting project failed");
      const data = await res.json();
      setState(data);
      fetchHistoricalProjects();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

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
            <div className="project-info" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <p className="topic">"{project.topic}"</p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
                <div className="stage-badge">{project.stage}</div>
                <button 
                  onClick={handleResetProject} 
                  className="btn-reset" 
                  style={{ padding: '3px 8px', fontSize: '0.75rem', marginTop: '0', display: 'flex', alignItems: 'center', gap: '4px' }}
                  title={t.btnResetProject}
                >
                  🔄 {state.language === 'cn' ? '重置项目' : 'Reset'}
                </button>
              </div>
            </div>
          ) : (
            <p className="no-project-text">{t.noProject}</p>
          )}
        </div>

        <div className="sidebar-footer" style={{ gap: '6px' }}>
          <button 
            onClick={handleOpenProjectManager} 
            className="btn-primary" 
            style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', background: 'linear-gradient(135deg, var(--accent-color) 0%, #4f46e5 100%)', padding: '10px' }}
          >
            {t.btnProjectManager}
          </button>
          <div style={{ display: 'flex', gap: '8px', width: '100%' }}>
            <button onClick={handleOpenSettings} className="btn-settings" style={{ flex: 1 }}>
              {t.settingsBtn}
            </button>
            <button onClick={handleReset} className="btn-reset" style={{ flex: 1, padding: '8px' }}>
              {t.resetSim}
            </button>
          </div>
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
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <h2 style={{ margin: 0 }}>{t.studentsTitle}</h2>
                        <button 
                          onClick={handleOpenRecruitModal} 
                          className="btn-primary" 
                          style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'linear-gradient(135deg, var(--accent-color) 0%, #4f46e5 100%)' }}
                        >
                          {t.btnRecruitStudent}
                        </button>
                      </div>
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
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '10px' }}>
                            <h2 style={{ border: 'none', padding: 0, margin: 0 }}>{currentStudentObj.name}{t.workspaceTitle}</h2>
                            <button 
                              onClick={() => handleDismissStudent(currentStudentObj.name)}
                              className="btn-danger" 
                              style={{ padding: '6px 12px', fontSize: '0.8rem', borderRadius: '6px', background: 'var(--color-danger)' }}
                            >
                              ⚠️ {t.btnDismissStudent}
                            </button>
                          </div>
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

      {/* Recruit Student Modal */}
      {showRecruitModal && (
        <div className="file-modal-overlay" onClick={() => setShowRecruitModal(false)}>
          <div className="file-modal settings-modal" onClick={(e) => e.stopPropagation()}>
            <div className="file-modal-header">
              <h3>🎓 {t.recruitModalTitle}</h3>
              <button className="btn-close" onClick={() => setShowRecruitModal(false)}>✕</button>
            </div>
            
            <form onSubmit={handleRecruitSubmit} className="settings-form" style={{ maxHeight: '75vh', overflowY: 'auto', padding: '20px' }}>
              <div className="form-group">
                <label>{t.labelPreset}</label>
                <select value={recruitPreset} onChange={(e) => handlePresetChange(e.target.value)}>
                  <option value="data_engineer">{t.presetDataEng}</option>
                  <option value="theoretical_analyst">{t.presetTheoAnalyst}</option>
                  <option value="ml_dev">{t.presetMLDev}</option>
                  <option value="academic_writer">{t.presetWriter}</option>
                  <option value="custom">{t.presetCustom}</option>
                </select>
              </div>

              <div className="form-group">
                <label>{t.labelName}</label>
                <input
                  type="text"
                  placeholder={t.placeholderName}
                  value={recruitName}
                  onChange={(e) => setRecruitName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>{t.labelRole}</label>
                <input
                  type="text"
                  placeholder={t.placeholderRole}
                  value={recruitRole}
                  onChange={(e) => setRecruitRole(e.target.value)}
                  disabled={recruitPreset !== 'custom'}
                  required
                />
              </div>

              <div className="form-group">
                <label>{t.labelSkills}</label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t.labelResearch}</span>
                      <span style={{ fontSize: '0.85rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{(recruitResearch * 10).toFixed(0)}</span>
                    </div>
                    <input
                      type="range"
                      min="0.0"
                      max="1.0"
                      step="0.1"
                      value={recruitResearch}
                      onChange={(e) => setRecruitResearch(Number(e.target.value))}
                      disabled={recruitPreset !== 'custom'}
                      style={{ width: '100%', accentColor: 'var(--accent-color)', cursor: recruitPreset === 'custom' ? 'pointer' : 'not-allowed' }}
                    />
                  </div>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t.labelCoding}</span>
                      <span style={{ fontSize: '0.85rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{(recruitCoding * 10).toFixed(0)}</span>
                    </div>
                    <input
                      type="range"
                      min="0.0"
                      max="1.0"
                      step="0.1"
                      value={recruitCoding}
                      onChange={(e) => setRecruitCoding(Number(e.target.value))}
                      disabled={recruitPreset !== 'custom'}
                      style={{ width: '100%', accentColor: 'var(--accent-color)', cursor: recruitPreset === 'custom' ? 'pointer' : 'not-allowed' }}
                    />
                  </div>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t.labelWriting}</span>
                      <span style={{ fontSize: '0.85rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{(recruitWriting * 10).toFixed(0)}</span>
                    </div>
                    <input
                      type="range"
                      min="0.0"
                      max="1.0"
                      step="0.1"
                      value={recruitWriting}
                      onChange={(e) => setRecruitWriting(Number(e.target.value))}
                      disabled={recruitPreset !== 'custom'}
                      style={{ width: '100%', accentColor: 'var(--accent-color)', cursor: recruitPreset === 'custom' ? 'pointer' : 'not-allowed' }}
                    />
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label>{t.labelPersonality}</label>
                <textarea
                  placeholder={t.placeholderPersonality}
                  value={recruitPersonality}
                  onChange={(e) => setRecruitPersonality(e.target.value)}
                  style={{ width: '100%', minHeight: '80px', padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'rgba(0,0,0,0.3)', color: 'white', resize: 'vertical' }}
                  required
                />
              </div>

              <button type="submit" className="btn-primary-large" style={{ marginTop: '10px' }} disabled={loading}>
                {t.btnRecruitSubmit}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Project Manager Modal */}
      {showProjectManager && (
        <div className="file-modal-overlay" onClick={() => setShowProjectManager(false)}>
          <div className="file-modal settings-modal" onClick={(e) => e.stopPropagation()}>
            <div className="file-modal-header">
              <h3>⚙️ {t.projectManagerTitle}</h3>
              <button className="btn-close" onClick={() => setShowProjectManager(false)}>✕</button>
            </div>
            
            <div className="file-modal-body" style={{ display: 'flex', flexDirection: 'column', padding: '20px', overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
                <h4 style={{ color: 'var(--text-secondary)' }}>{t.projectListHeader}</h4>
                <button onClick={handleNewProjectIntent} className="btn-primary-large" style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'linear-gradient(135deg, var(--accent-color) 0%, #10b981 100%)', boxShadow: '0 4px 12px rgba(16, 185, 129, 0.2)' }}>
                  {t.btnCreateNewProject}
                </button>
              </div>
              
              <div className="project-history-list" style={{ flexGrow: 1, overflowY: 'auto' }}>
                {historicalProjects.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                    <p style={{ fontSize: '1.5rem', marginBottom: '10px' }}>📁</p>
                    <p>{t.noProjects}</p>
                  </div>
                ) : (
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', color: 'var(--text-primary)' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                        <th style={{ padding: '12px 8px' }}>{t.thTopic}</th>
                        <th style={{ padding: '12px 8px' }}>{t.thStage}</th>
                        <th style={{ padding: '12px 8px' }}>{t.thDay}</th>
                        <th style={{ padding: '12px 8px' }}>{t.thFunding}</th>
                        <th style={{ padding: '12px 8px' }}>{t.thReputation}</th>
                        <th style={{ padding: '12px 8px' }}>{t.thLastSaved}</th>
                        <th style={{ padding: '12px 8px', textAlign: 'right' }}>{t.thActions}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {historicalProjects.map((proj) => {
                        const isActive = state.active_project_id === proj.project_id;
                        return (
                          <tr key={proj.project_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', background: isActive ? 'rgba(99,102,241,0.05)' : 'transparent' }}>
                            <td style={{ padding: '14px 8px', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontWeight: isActive ? 'bold' : 'normal' }}>
                              {isActive && <span style={{ marginRight: '6px', background: 'var(--accent-color)', color: '#fff', fontSize: '0.7rem', padding: '2px 6px', borderRadius: '4px' }}>{t.activeBadge}</span>}
                              <span title={proj.topic}>{proj.topic}</span>
                            </td>
                            <td style={{ padding: '14px 8px' }}>
                              <span className="stage-badge" style={{ padding: '2px 6px', fontSize: '0.75rem', background: isActive ? 'var(--accent-color)' : '#334155', boxShadow: 'none' }}>
                                {proj.stage}
                              </span>
                            </td>
                            <td style={{ padding: '14px 8px' }}>Day {proj.day}</td>
                            <td style={{ padding: '14px 8px' }}>¥{proj.funding.toLocaleString()}</td>
                            <td style={{ padding: '14px 8px' }}>{proj.reputation.toFixed(1)}</td>
                            <td style={{ padding: '14px 8px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                              {new Date(proj.last_saved * 1000).toLocaleString(state.language === 'cn' ? 'zh-CN' : 'en-US')}
                            </td>
                            <td style={{ padding: '14px 8px', textAlign: 'right' }}>
                              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                                <button 
                                  onClick={() => handleLoadProject(proj.project_id)}
                                  className="btn-primary" 
                                  style={{ padding: '6px 12px', fontSize: '0.8rem', background: '#3b82f6' }}
                                >
                                  {t.btnLoad}
                                </button>
                                <button 
                                  onClick={() => handleDeleteProject(proj.project_id)}
                                  className="btn-danger" 
                                  style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                                >
                                  {t.btnDelete}
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
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
