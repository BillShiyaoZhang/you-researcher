# 🔬 教授模拟器 (科研 Agent 模拟游戏)

欢迎来到 **教授模拟器 (Professor Simulator)**！这是一款基于 Agent 的科研模拟游戏。在游戏中，你将扮演科研实验室的负责人（PI / 教授），管理多名 PhD 学生，从 ArXiv 检索真实文献，撰写并评审开题报告，在本地沙箱运行实验代码，撰写学术论文，并将其提交给顶级学术会议！

---

## 🚀 快速开始

### 1. 安装与环境配置
确保你已安装 `uv`（现代 Python 包管理工具）。如果未安装，可以运行以下命令安装：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装所有依赖并初始化虚拟环境：
```bash
uv sync
```

### 2. 配置环境变量（可选）
在根目录下创建或修改 **[`.env`](file:///Users/shiyaozhang/Developer/you-researcher/.env)** 文件，填入你的 API 密钥：
```env
OPENAI_API_KEY=your_real_api_key_here
OPENAI_API_BASE=https://api.minimaxi.com/v1
LLM_MODEL=MiniMax-M3
```
*提示：如果未配置 API 密钥（留空或保持默认值），系统将自动运行在**本地模拟模式**（Mock Simulation Mode），提供高度逼真的模拟科研产出，让你能够完全免费体验全部游戏流程！*

### 3. 编译并运行

**编译前端界面：**
```bash
cd frontend
npm install
npm run build
cd ..
```

**启动服务器：**
```bash
uv run main.py
```
启动后在浏览器中打开 **[http://localhost:8000](http://localhost:8000)** 即可开始游戏！

---

## 🕹️ 游戏核心流程

1. **办公室 (启动项目)**：选择一个当前热门的研究方向（如注意力机制优化、RLAIF、DPO、稀疏掩码微调）或输入完全自定义的科研课题。
2. **文献检索**：指派 Bob（理论研究员）检索 ArXiv 真实论文，生成文献综述文件 `workspace/literature_review.md`。
3. **撰写开题报告**：指派 Alice（深度学习极客）撰写正式开题报告，并附带用于验证的 Python 实验代码，生成 `workspace/proposal.md`。
4. **教授评审（决策门槛）**：在 Web 界面中审查开题报告。你可以**批准**开始实验，或者**驳回**并写下修改意见让学生重新修改。
5. **沙箱实验**：Alice 在本地隔离子进程沙箱中运行 Python 脚本，捕获标准输出和错误。实验代码将被保存为 `workspace/experiment.py`。若代码运行出错，Alice 会自动调用 LLM 进行自我 Debug 修复！
6. **撰写论文**：指派 Bob 整合实验结果和文献综述，撰写完整的学术论文草稿 `workspace/paper.md`。
7. **论文提交与盲审**：支付 $800 注册费提交给 NeurIPS、ICML、CVPR 或 EMNLP。游戏会模拟学术同行评审（Peer Review），给出评分和意见。如果被录用（Accept），你的实验室将获得大量科研声望（Reputation）和新一轮科研经费（Funding）！

---

## 🧪 自动化测试

运行后端单元测试：
```bash
uv run python -m unittest tests/test_backend.py
```

运行完整的科研流程集成测试：
```bash
PYTHONPATH=. uv run python tests/test_flow.py
```
