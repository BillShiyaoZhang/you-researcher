# 🔬 You Researcher (Research Agent Simulator)

Welcome to **You Researcher**, an agentic simulator game where you play the Principal Investigator (PI) of a research lab. Manage PhD students, synthesize research from ArXiv, approve proposals, run code in a sandbox, compile manuscripts, and submit them to top-tier conferences!

---

## 🚀 Quick Start

### 1. Installation & Environment Setup
Ensure you have `uv` installed (Python package manager). If not, you can run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install all dependencies and prepare the virtual environment:
```bash
uv sync
```

### 2. Configure Environment Variables (Optional)
Create or modify the **[`.env`](file:///Users/shiyaozhang/Developer/you-researcher/.env)** file in the root directory:
```env
OPENAI_API_KEY=your_real_api_key_here
OPENAI_API_BASE=https://api.minimaxi.com/v1
LLM_MODEL=MiniMax-M3
```
*Note: If no API key is provided, the simulator will automatically run in **Mock Simulation Mode**, allowing you to play the entire game out-of-the-box for free.*

### 3. Build & Run

**Build the Frontend:**
```bash
cd frontend
npm install
npm run build
cd ..
```

**Start the Server:**
```bash
uv run main.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser to play!

---

## 🕹️ Gameplay Flow

1. **Office (Launch Project)**: Select a trending research topic or enter a custom one.
2. **Literature Review**: Bob (Theoretical Researcher) queries ArXiv and compiles findings in `workspace/literature_review.md`.
3. **Design Proposal**: Alice (Deep Learning Hacker) designs a proposal with python script simulation in `workspace/proposal.md`.
4. **Professor Gate**: Review the proposal and code draft in the UI. Either **Approve** or **Reject** with revision comments.
5. **Sandbox Run**: Alice executes the python script in a local subprocess sandbox. The code is saved to `workspace/experiment.py` along with result logs.
6. **Compile Draft**: Bob structures the final paper draft in `workspace/paper.md`.
7. **Submit Manuscript**: Pay registration fees ($800) and submit to EMNLP, NeurIPS, ICML, or CVPR. Peer review simulation scores your manuscript and generates reviews. If accepted, you earn reputation and new research grants (funding)!

---

## 🧪 Verification & Tests

Run the backend unit tests:
```bash
uv run python -m unittest tests/test_backend.py
```

Run the end-to-end integration tests:
```bash
PYTHONPATH=. uv run python tests/test_flow.py
```
