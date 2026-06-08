import os
import time
import random
import json
import shutil
import threading
import requests
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Any, List, Optional
from app.game_state import GameState, Student, Project, ChatChannel, ChatMessage
from app.arxiv_tool import search_arxiv
from app.sandbox import execute_python_code

load_dotenv()

# Thread lock to prevent concurrent state modifications
state_lock = threading.Lock()

# Track consecutive replies for each channel to prevent infinite loops
consecutive_replies = {}

SYSTEM_PROMPTS = {
    "Alice": """You are Alice, a PhD student in the lab. You are a "Deep Learning Hacker" with exceptional coding skills (9/10), good research ideas (6/10), but average writing (5/10).
Personality: Direct, energetic, prefers writing code and running experiments over reading papers. Speaks colloquially, uses developer terms (e.g. "it compiles!", "bug fixed", "let's script this").
You will help the Professor run experiments and write code scripts.""",

    "Bob": """You are Bob, a PhD student in the lab. You are a "Theoretical Researcher" with superb literature synthesis and writing skills (9/10), but weak coding skills (4/10).
Personality: Meticulous, academic, precise, formal, sometimes a bit slow. Prefers reading papers and structuring theoretical proofs. Speaks formally and structures ideas logically.
You will help the Professor with literature search, reading papers, and drafting papers.""",

    "Charlie": """You are Charlie, an enthusiastic master's student doing an internship in the lab. You have average skills (research: 5/10, coding: 6/10, writing: 6/10).
Personality: Very eager to learn, asks lots of questions, highly motivated, but sometimes makes rookie mistakes. Speaks politely and calls you 'Professor' in every sentence.
You will assist on any task."""
}

def calculate_llm_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    model_lower = model.lower()
    # Cost per token in RMB (estimates based on 1 USD = 7.0 RMB)
    if "gpt-4o-mini" in model_lower:
        in_rate = 1.05 / 1_000_000
        out_rate = 4.20 / 1_000_000
    elif "gpt-4o" in model_lower:
        in_rate = 35.0 / 1_000_000
        out_rate = 105.0 / 1_000_000
    elif "gpt-3.5" in model_lower:
        in_rate = 3.5 / 1_000_000
        out_rate = 10.5 / 1_000_000
    elif "deepseek-coder" in model_lower or "deepseek-chat" in model_lower:
        in_rate = 1.0 / 1_000_000
        out_rate = 2.0 / 1_000_000
    else:
        # Default fallback pricing
        in_rate = 7.0 / 1_000_000
        out_rate = 21.0 / 1_000_000
    return (input_tokens * in_rate) + (output_tokens * out_rate)

def fetch_api_balance(provider: str, api_key: str, base_url: str) -> Optional[float]:
    if not api_key or api_key.strip() == "":
        return None
    try:
        if "openrouter" in base_url.lower():
            url = "https://openrouter.ai/api/v1/user/credits"
            r = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if "data" in data and "credits" in data["data"]:
                    return float(data["data"]["credits"]) * 7.0 # convert USD to RMB
        elif "minimax" in provider.lower() or "minimax" in base_url.lower() or "minimaxi" in base_url.lower():
            urls = [
                f"{base_url.rstrip('/')}/token_plan/remains",
                "https://api.minimaxi.com/v1/token_plan/remains",
                "https://api.minimax.chat/v1/token_plan/remains",
                "https://www.minimaxi.com/v1/token_plan/remains"
            ]
            for url in urls:
                try:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    r = requests.get(url, headers=headers, timeout=5)
                    if r.status_code == 200:
                        data = r.json()
                        # Parse actual model_remains array returned by MiniMax
                        if "model_remains" in data and isinstance(data["model_remains"], list):
                            remains_list = data["model_remains"]
                            gen = next((item for item in remains_list if item.get("model_name") == "general"), None)
                            if not gen and remains_list:
                                gen = remains_list[0]
                            if gen:
                                pct = gen.get("current_weekly_remaining_percent")
                                if pct is None:
                                    pct = gen.get("current_interval_remaining_percent")
                                if pct is not None:
                                    # Scale percentage (0-100) to game budget (e.g. 100% -> ¥500,000)
                                    return float(pct) * 5000.0
                        
                        # Fallback checks
                        if "current_weekly_usage_count" in data:
                            return float(data["current_weekly_usage_count"])
                        if "current_interval_usage_count" in data:
                            return float(data["current_interval_usage_count"])
                        if "remains" in data:
                            return float(data["remains"])
                        if "data" in data and isinstance(data["data"], dict):
                            d = data["data"]
                            if "current_weekly_usage_count" in d:
                                return float(d["current_weekly_usage_count"])
                            if "current_interval_usage_count" in d:
                                return float(d["current_interval_usage_count"])
                            if "remains" in d:
                                return float(d["remains"])
                except Exception as inner_ex:
                    print(f"Failed to fetch MiniMax balance from {url}: {inner_ex}")
    except Exception as e:
        print(f"Error fetching API balance: {e}")
    return None

def call_llm(system_prompt: str, user_prompt: str, language: str = "cn", game_state: Optional[GameState] = None, caller_name: Optional[str] = None) -> str:
    config = game_state.llm_config if game_state else None
    provider = config.provider if config else "openai"
    api_key = config.api_key if config else os.getenv("OPENAI_API_KEY")
    base_url = config.base_url if config else os.getenv("OPENAI_API_BASE")
    model = config.model if config else os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # Check if API Key is not set or empty
    if not api_key or api_key.strip() == "" or api_key == "your_api_key_here":
        response_text = get_mock_llm_response(system_prompt, user_prompt, language=language, caller_name=caller_name, game_state=game_state)
        # Mock token estimation
        in_tokens = len(system_prompt + user_prompt) // 2
        out_tokens = len(response_text) // 2
        cost = calculate_llm_cost(model, in_tokens, out_tokens)
        if game_state:
            game_state.funding = max(0.0, game_state.funding - cost)
            game_state.session_cost += cost
            caller = f"{caller_name} " if caller_name else ""
            game_state.add_log(
                f"[模拟计费] {caller}调用模型 {model}，消耗 {in_tokens} prompt / {out_tokens} completion tokens，支出 ¥{cost:.4f}"
                if game_state.language == "cn" else
                f"[Sim Billing] {caller}called {model}, consumed {in_tokens} prompt / {out_tokens} completion tokens, cost ¥{cost:.4f}"
            )
            game_state.save()
        return response_text

    try:
        client_args = {"api_key": api_key}
        if base_url and base_url.strip() != "":
            client_args["base_url"] = base_url
        client = OpenAI(**client_args)
        
        # Add language output override to system prompt
        if language == "cn":
            system_prompt += "\n重要指示：必须使用中文回答且仅输出 JSON 格式。"
        else:
            system_prompt += "\nImportant instruction: You must respond in English and output ONLY in JSON format."
            
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        response_text = response.choices[0].message.content
        
        # Calculate precise cost
        in_tokens = response.usage.prompt_tokens
        out_tokens = response.usage.completion_tokens
        cost = calculate_llm_cost(model, in_tokens, out_tokens)
        
        if game_state:
            game_state.funding = max(0.0, game_state.funding - cost)
            game_state.session_cost += cost
            caller = f"{caller_name} " if caller_name else ""
            game_state.add_log(
                f"[经费支出] {caller}调用模型 {model}，消耗 {in_tokens} prompt / {out_tokens} completion tokens，计费 ¥{cost:.4f}"
                if game_state.language == "cn" else
                f"[Expense] {caller}called {model}, consumed {in_tokens} prompt / {out_tokens} completion tokens, cost ¥{cost:.4f}"
            )
            game_state.save()
            
        return response_text
    except Exception as e:
        print(f"API call failed: {e}. Falling back to mock response.")
        response_text = get_mock_llm_response(system_prompt, user_prompt, error_msg=str(e), language=language, caller_name=caller_name, game_state=game_state)
        in_tokens = len(system_prompt + user_prompt) // 2
        out_tokens = len(response_text) // 2
        cost = calculate_llm_cost(model, in_tokens, out_tokens)
        if game_state:
            game_state.funding = max(0.0, game_state.funding - cost)
            game_state.session_cost += cost
            caller = f"{caller_name} " if caller_name else ""
            game_state.add_log(
                f"[回退计费] {caller}大模型调用失败，回退到模拟。消耗 ¥{cost:.4f}"
                if game_state.language == "cn" else
                f"[Fallback Billing] {caller}LLM failed, fallback to simulation. Cost ¥{cost:.4f}"
            )
            game_state.save()
        return response_text

def get_mock_llm_response(system_prompt: str, user_prompt: str, error_msg: str = "", language: str = "cn", caller_name: Optional[str] = None, game_state: Optional[GameState] = None) -> str:
    """
    Generates structured JSON mock responses for agents based on their current workspace files.
    """
    is_cn = (language == "cn")
    name = caller_name or "Student"
    
    # Base topic
    topic = game_state.current_project.topic if game_state and game_state.current_project else "Deep Learning"
    stage = game_state.current_project.stage if game_state and game_state.current_project else "Literature Review"
    
    # 1. Bob Literature Review Flow
    if name == "Bob" and "arxiv_results.txt" not in system_prompt and stage == "Literature Review":
        return json.dumps({
            "thoughts": "课题刚启动，我需要先在 ArXiv 上搜索一下最新的研究文献。" if is_cn else "The project just started. I need to query ArXiv for papers first.",
            "message": f"教授，我正准备在 ArXiv 上检索关于 '{topic}' 的最新文献。" if is_cn else f"Professor, I am starting literature search on ArXiv for '{topic}'.",
            "action": {
                "type": "search_arxiv",
                "params": {"query": topic}
            }
        }, ensure_ascii=False)
        
    elif name == "Bob" and "arxiv_results.txt" in system_prompt and stage == "Literature Review":
        lit_content = f"""### 文献综述：{topic}
关于 {topic}，我们近期完成了文献综述：
1. Transformer 自适应优化方法已在各类视觉和语言基准上取得突破。
2. 梯度方差对训练稳定性具有直接影响。
3. 提出轻量级优化算法在基础沙箱环境中极具可行性。
我们拟定以自适应学习率优化为切入点展开研究。"""
        return json.dumps({
            "thoughts": "我已经拿到了 ArXiv 文献检索结果，并写好了文献综述 literature_review.md。现在，我申请把文献传输给 Alice 以便她撰写开题报告和代码。" if is_cn else "I got the literature query. I wrote literature_review.md. Now transferring it to Alice.",
            "message": "教授，我写好了文献综述 literature_review.md，并申请把文件传输给 Alice 协同。Alice，你看看我们在这个基础上怎么做实验代码。" if is_cn else "Professor, literature_review.md is ready in my workspace. I request transfer to Alice.",
            "action": {
                "type": "request_file_transfer",
                "params": {"filename": "literature_review.md", "target_agent": "Alice"}
            }
        }, ensure_ascii=False)
        
    # 2. Alice Proposal Flow
    elif name == "Alice" and "literature_review.md" in system_prompt and "proposal.md" not in system_prompt:
        proposal_content = f"""# 开题报告：自适应优化实验
拟在沙箱中测试一种简单的自适应梯度下降算法，打印 Epoch 损失曲线。

```python
import time
import random

def run_experiment():
    print("Initializing AVO vs AdamW Experiment...")
    loss_adam = 4.8
    loss_avo = 4.8
    print("Epoch | AdamW Loss | AVO Loss")
    print("----------------------------")
    for epoch in range(1, 6):
        time.sleep(0.2)
        loss_adam -= random.uniform(0.5, 0.8)
        loss_avo -= random.uniform(0.7, 1.1)
        print(f"  {{epoch}}   |   {{loss_adam:.4f}}   |   {{loss_avo:.4f}}")
    print("Experiment completed. AVO performs slightly better!")
    return True

run_experiment()
```"""
        code_content = """import time
import random

def run_experiment():
    print("Initializing AVO vs AdamW Experiment...")
    loss_adam = 4.8
    loss_avo = 4.8
    print("Epoch | AdamW Loss | AVO Loss")
    print("----------------------------")
    for epoch in range(1, 6):
        time.sleep(0.2)
        loss_adam -= random.uniform(0.5, 0.8)
        loss_avo -= random.uniform(0.7, 1.1)
        print(f"  {epoch}   |   {loss_adam:.4f}   |   {loss_avo:.4f}")
    print("Experiment completed. AVO performs slightly better!")
    return True

run_experiment()"""
        # We need to write code to Alice's folder and request approval
        # To do this in mockup, Alice first writes proposal and experiment scripts, then requests approval
        # Let's let her write the files first
        if "experiment.py" not in system_prompt:
            return json.dumps({
                "thoughts": "我收到了文献综述，正在我自己的工作区撰写 experiment.py 脚本以及开题报告 proposal.md。" if is_cn else "Drafting proposal and experiment.py in my workspace.",
                "message": "文献综述收到了！我已经在写 proposal.md 和实验代码了，一会儿写完发出来。" if is_cn else "Got literature review! I am writing proposal.md and experiment.py.",
                "action": {
                    "type": "write_file",
                    "params": {"filename": "experiment.py", "content": code_content}
                }
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "thoughts": "代码和开题报告已写好。我需要向教授发起开题报告评审申请。" if is_cn else "Writing proposal and requesting PI approval.",
                "message": "教授，我写好了开题报告和实验代码 `experiment.py`！请在『论文评审与文档』面板中审批，批准后我立刻开始实验。" if is_cn else "Professor, proposal.md and experiment.py are ready. Please approve.",
                "action": {
                    "type": "request_approval",
                    "params": {
                        "type": "proposal_approval",
                        "title": f"评审 Alice 的开题报告: {topic[:20]}...",
                        "description": "Alice 已经完成了开题报告草拟（附带实验代码）。请评审并批准以启动实验。",
                        "content": proposal_content
                    }
                }
            }, ensure_ascii=False)
            
    # 3. Alice Sandbox Run Flow
    elif name == "Alice" and stage == "Experimentation" and "results.log" not in system_prompt:
        return json.dumps({
            "thoughts": "开题报告已经被教授批准了！我立刻启动沙箱实验运行。" if is_cn else "Proposal approved. Starting experiment in sandbox.",
            "message": "教授，我这就启动隔离沙箱，运行我们的 `experiment.py` 代码！" if is_cn else "Professor, starting sandbox simulation now!",
            "action": {
                "type": "run_experiment",
                "params": {}
            }
        }, ensure_ascii=False)
        
    elif name == "Alice" and "results.log" in system_prompt and stage == "Experimentation":
        return json.dumps({
            "thoughts": "实验已跑通且拿到 logs 了。我需要把 results.log 共享给 Bob 方便他去写论文。" if is_cn else "Experiment completed. Sharing results.log with Bob.",
            "message": "Bob，实验代码在沙箱完美跑通，退出码为 0！我已经把实验日志 `results.log` 发给你了，你开始写论文手稿吧。" if is_cn else "Bob, experiment succeeded! I've shared results.log with you.",
            "action": {
                "type": "request_file_transfer",
                "params": {"filename": "results.log", "target_agent": "Bob"}
            }
        }, ensure_ascii=False)
        
    # 4. Bob Paper Writing Flow
    elif name == "Bob" and "results.log" in system_prompt and "paper.md" not in system_prompt:
        paper_content = f"""# 论文标题：自适应优化在 Transformer 上的应用
**摘要**：本研究在沙箱隔离环境下验证了一种轻量级自适应方差优化算法(AVO)。

## 1. 介绍
传统优化算法收敛较慢...

## 2. 实验结果
沙箱测试显示：
- AdamW 最终损失: 1.45
- AVO 最终损失: 1.10
AVO 收敛效果表现优异。"""
        # Write file first
        return json.dumps({
            "thoughts": "收到 Alice 发来的实验数据了，开始在工作区组装写 paper.md 论文草稿。" if is_cn else "Drafting paper.md based on results.log.",
            "message": "Alice 收到！我已经在写学术手稿 paper.md 了，今天就能整完。" if is_cn else "Got it Alice! Writing paper.md now.",
            "action": {
                "type": "write_file",
                "params": {"filename": "paper.md", "content": paper_content}
            }
        }, ensure_ascii=False)
        
    elif name == "Bob" and "paper.md" in system_prompt and stage == "Paper Writing":
        paper_content = f"""# 论文标题：自适应优化在 Transformer 上的应用
**摘要**：本研究在沙箱隔离环境下验证了一种轻量级自适应方差优化算法(AVO)。

## 1. 介绍
传统优化算法收敛较慢...

## 2. 实验结果
沙箱测试显示：
- AdamW 最终损失: 1.45
- AVO 最终损失: 1.10
AVO 收敛效果表现优异。"""
        return json.dumps({
            "thoughts": "论文写好了，向教授申请进行论文盲审与会议投稿。" if is_cn else "Paper ready. Requesting PI to submit to conference.",
            "message": "教授，学术手稿 `paper.md` 已经写好了！请在『评审与文档』面板里审核，并选择一个顶级会议进行手稿提交。" if is_cn else "Professor, paper.md is complete. Please review and submit.",
            "action": {
                "type": "request_approval",
                "params": {
                    "type": "paper_submission",
                    "title": f"学术论文投稿审查: {topic[:20]}...",
                    "description": "Bob 已经完成了论文草稿。请评审并选择合适的学术会议进行手稿双盲评审投稿。",
                    "content": paper_content
                }
            }
        }, ensure_ascii=False)
        
    # Default idle response
    return json.dumps({
        "thoughts": "现在事情进展顺利。我需要随时准备协助团队。" if is_cn else "Things are progressing fine. Standing by to help.",
        "message": f"教授，我们目前的科研主题是 '{topic}'，我会继续跟进项目。" if is_cn else f"Professor, standing by to assist with '{topic}'.",
        "action": None
    }, ensure_ascii=False)

def parse_json_response(text: str) -> Dict[str, Any]:
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except Exception as e:
        # Fallback regex parsing
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        raise e

def get_agent_system_prompt(student: Student, project: Project, workspace_files: Dict[str, str], channel_name: str, language: str) -> str:
    profile = SYSTEM_PROMPTS.get(student.name, "")
    
    files_str = ""
    if workspace_files:
        for fname, fcontent in workspace_files.items():
            files_str += f"\n--- File: {fname} ---\n{fcontent}\n"
    else:
        files_str = "No files present in your directory."
        
    is_cn = (language == "cn")
    
    prompt = f"""{profile}
You are currently working inside your isolated workspace folder: `workspace/{student.name}/`.
You CANNOT view or write files in other agents' directories directly.
To share code, logs, or reports with peers, you must use a 'File Transfer Request' action.

Project Topic: "{project.topic}"
Project Stage: {project.stage}

Files in your workspace directory:
{files_str}

Active Chat Channel Name: {channel_name}

Instructions:
1. Review the conversation history and workspace files.
2. Based on your role, skills, and current files, decide what to do next.
3. You must respond ONLY with a valid JSON block containing:
   - "thoughts": "Your internal monologue in Chinese" if language is cn, otherwise in English.
   - "message": "Message to send to the chat channel" (string, or null if you don't need to speak).
   - "action": an action object or null.
   
Allowed actions:
- {{"type": "search_arxiv", "params": {{"query": "search query"}}}}
- {{"type": "write_file", "params": {{"filename": "name of file", "content": "content of file"}}}}
- {{"type": "run_experiment", "params": {{}}}}  (Only Alice can execute python experiments in her sandbox)
- {{"type": "request_file_transfer", "params": {{"filename": "file to send", "target_agent": "Alice or Bob or Charlie"}}}}
- {{"type": "request_approval", "params": {{"type": "proposal_approval" or "paper_submission", "title": "short title", "description": "description", "content": "content to review"}}}}

IMPORTANT:
- Ground all your statements in the files physically present in your workspace. Do NOT hallucinate experiments, literature reviews, or files that do not exist in your directory.
- Keep your thoughts and message highly in-character.
- If you request approval, state clearly in your chat message what you are requesting approval for.
"""
    return prompt

def trigger_background_agent_loop(channel_id: str, game_state: GameState):
    """
    Spawns a background thread to update agent states and responses for the channel.
    """
    thread = threading.Thread(target=_background_agent_worker, args=(channel_id, game_state))
    thread.daemon = True
    thread.start()

def _background_agent_worker(channel_id: str, game_state: GameState):
    with state_lock:
        channel = next((c for c in game_state.channels if c.id == channel_id), None)
        if not channel:
            return
            
    # Prevent infinite loops in normal mode
    if channel_id not in consecutive_replies:
        consecutive_replies[channel_id] = 0
        
    members = [m for m in channel.members if m != "PI"]
    
    # Process each student agent in the channel
    for member_name in members:
        with state_lock:
            student = next((s for s in game_state.students if s.name == member_name), None)
            if not student:
                continue
                
            # If resting, skip
            if student.status in ["休息中", "Resting"]:
                # Re-charge energy slightly
                student.energy = min(100, student.energy + 20)
                if student.energy >= 80:
                    student.status = "空闲" if game_state.language == "cn" else "Idle"
                    student.activity = "休息完毕！重新恢复科研工作。" if game_state.language == "cn" else "Finished resting. Ready for work."
                game_state.save()
                continue
                
            # Check energy depletion
            if student.energy < 15:
                student.status = "休息中" if game_state.language == "cn" else "Resting"
                student.activity = "补充睡眠中..." if game_state.language == "cn" else "Sleeping and recharging energy."
                student.thoughts.append("累垮了，我得去睡个长觉。" if game_state.language == "cn" else "I'm exhausted... need to rest.")
                game_state.add_log(f"学生 {student.name} 精疲力竭，被迫停工休息。")
                game_state.save()
                continue
                
            # Check maximum replies limit in normal mode
            if not game_state.autonomous_mode:
                if consecutive_replies[channel_id] >= 3:
                    game_state.add_log("已达到连续发言最大上限（3次）。等待教授介入..." if game_state.language == "cn" else "Reached maximum consecutive replies. Awaiting PI guidance.")
                    game_state.save()
                    break

        # Read isolated workspace files
        workspace_files = {}
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        student_ws_dir = os.path.join(base_dir, "workspace", member_name)
        os.makedirs(student_ws_dir, exist_ok=True)
        
        for f in os.listdir(student_ws_dir):
            fpath = os.path.join(student_ws_dir, f)
            if os.path.isfile(fpath) and f.endswith(('.md', '.py', '.txt', '.log')):
                try:
                    with open(fpath, "r", encoding="utf-8") as fh:
                        workspace_files[f] = fh.read()[:2000] # Cap reading length
                except Exception as ex:
                    print(f"Error reading file {f}: {ex}")
                    
        # Generate prompt and call LLM
        sys_prompt = get_agent_system_prompt(student, game_state.current_project, workspace_files, channel.name, game_state.language)
        
        history_str = ""
        with state_lock:
            for msg in channel.messages[-8:]:
                history_str += f"{msg.sender}: {msg.message}\n"
                
        user_prompt = f"Recent conversation history in channel:\n{history_str}\nPlease decide your response and next action."
        
        response_text = call_llm(sys_prompt, user_prompt, language=game_state.language, game_state=game_state, caller_name=member_name)
        
        # Parse JSON
        try:
            resp_data = parse_json_response(response_text)
        except Exception as err:
            print(f"Error parsing JSON from {member_name}: {err}. Raw: {response_text}")
            resp_data = {
                "thoughts": f"Error parsing: {str(err)}",
                "message": "我的思维断了，等我缓一缓。" if game_state.language == "cn" else "I got a bit stuck. Sorry!",
                "action": None
            }
            
        # Apply edits under lock
        with state_lock:
            # Re-fetch references to ensure thread safety
            student = next((s for s in game_state.students if s.name == member_name), None)
            project = game_state.current_project
            channel = next((c for c in game_state.channels if c.id == channel_id), None)
            
            if not student or not project or not channel:
                continue
                
            # Monologue / Thoughts
            if resp_data.get("thoughts"):
                student.thoughts.append(resp_data["thoughts"])
                
            # Message
            msg_text = resp_data.get("message")
            if msg_text:
                msg_id = f"msg_{int(time.time()*1000)}"
                channel.messages.append(ChatMessage(
                    id=msg_id,
                    sender=member_name,
                    role=student.role,
                    message=msg_text,
                    timestamp=time.time()
                ))
                channel.unread = True
                if not game_state.autonomous_mode:
                    consecutive_replies[channel_id] += 1
                student.energy = max(0, student.energy - 8)
                
            # Action execution
            action = resp_data.get("action")
            if action and action.get("type"):
                action_type = action["type"]
                params = action.get("params", {})
                
                # Auto approval check
                is_auto = game_state.autonomous_mode and (action_type in ["run_experiment", "request_file_transfer"])
                
                if action_type == "search_arxiv":
                    query = params.get("query", project.topic)
                    student.status = "文献检索" if game_state.language == "cn" else "Searching ArXiv"
                    student.activity = f"检索 ArXiv: '{query}'" if game_state.language == "cn" else f"Querying ArXiv: '{query}'"
                    
                    papers = search_arxiv(query, max_results=4)
                    papers_text = ""
                    for idx, p in enumerate(papers):
                        if "error" in p:
                            papers_text += f"\nError: {p['error']}\n"
                        elif "info" in p:
                            papers_text += f"\nInfo: {p['info']}\n"
                        else:
                            papers_text += f"\nPaper {idx+1}: {p['title']}\nAbstract: {p['summary']}\nURL: {p['url']}\n"
                            
                    # Write to workspace
                    with open(os.path.join(student_ws_dir, "arxiv_results.txt"), "w", encoding="utf-8") as f_out:
                        f_out.write(papers_text)
                    student.thoughts.append("文献检索完成。结果已保存至 arxiv_results.txt。" if game_state.language == "cn" else "ArXiv query completed. Saved to arxiv_results.txt.")
                    student.status = "空闲" if game_state.language == "cn" else "Idle"
                    student.activity = "完成文献综述数据拉取。" if game_state.language == "cn" else "Literature search completed."
                    student.energy = max(0, student.energy - 10)
                    
                elif action_type == "write_file":
                    filename = params.get("filename")
                    content = params.get("content")
                    if filename and content:
                        with open(os.path.join(student_ws_dir, filename), "w", encoding="utf-8") as f_out:
                            f_out.write(content)
                        student.thoughts.append(f"已生成工作区文件: {filename}" if game_state.language == "cn" else f"Written workspace file: {filename}")
                        student.energy = max(0, student.energy - 12)
                        
                        # Backwards compatibility stages
                        if member_name == "Bob" and filename == "literature_review.md":
                            project.proposal_draft = content
                            project.stage = "Proposal"
                        elif member_name == "Bob" and filename == "paper.md":
                            project.paper_draft = content
                            project.stage = "Awaiting Submission"
                        elif member_name == "Alice" and filename == "proposal.md":
                            project.proposal_draft = content
                            
                elif action_type == "run_experiment" and member_name == "Alice":
                    if is_auto:
                        code_path = os.path.join(student_ws_dir, "experiment.py")
                        code_block = ""
                        if os.path.exists(code_path):
                            with open(code_path, "r", encoding="utf-8") as f_in:
                                code_block = f_in.read()
                        else:
                            code_block = "print('Running default code...')"
                            
                        student.status = "实验中" if game_state.language == "cn" else "Experimenting"
                        student.activity = "运行沙箱实验脚本..." if game_state.language == "cn" else "Executing code sandbox..."
                        
                        sandbox_result = execute_python_code(code_block, student_ws_dir)
                        stdout = sandbox_result.get("stdout", "")
                        stderr = sandbox_result.get("stderr", "")
                        exit_code = sandbox_result.get("exit_code", -1)
                        
                        with open(os.path.join(student_ws_dir, "results.log"), "w", encoding="utf-8") as f_out:
                            f_out.write(f"--- Sandbox Exit Code: {exit_code} ---\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
                            
                        student.thoughts.append("沙箱实验已顺利跑通。结果写入 results.log。" if game_state.language == "cn" else "Sandbox finished. Output saved to results.log.")
                        student.status = "空闲" if game_state.language == "cn" else "Idle"
                        student.activity = "沙箱脚本执行完毕。" if game_state.language == "cn" else "Sandbox run completed."
                        student.energy = max(0, student.energy - 25)
                        
                        # Apply expense
                        sandbox_cost = 5.0
                        game_state.funding = max(0.0, game_state.funding - sandbox_cost)
                        game_state.add_log(f"Alice 自动运行沙箱实验，消耗 ¥{sandbox_cost:.2f}" if game_state.language == "cn" else f"Alice executed sandbox experiment automatically, cost ¥{sandbox_cost:.2f}")
                    else:
                        app_id = f"sandbox_{int(time.time()*1000)}"
                        game_state.pending_approvals.append({
                            "id": app_id,
                            "type": "run_sandbox",
                            "student": "Alice",
                            "title": "审批沙箱实验运行" if game_state.language == "cn" else "Approve Sandbox Experiment",
                            "description": "Alice 请求运行她的实验代码 `experiment.py`。这需要开启安全沙箱隔离容器。"
                        })
                        student.status = "等待审批" if game_state.language == "cn" else "Awaiting Approval"
                        student.activity = "等待教授批准启动实验..." if game_state.language == "cn" else "Awaiting sandbox run approval..."
                        
                elif action_type == "request_file_transfer":
                    filename = params.get("filename")
                    target = params.get("target_agent")
                    if filename and target:
                        if is_auto:
                            src = os.path.join(student_ws_dir, filename)
                            dst_dir = os.path.join(base_dir, "workspace", target)
                            os.makedirs(dst_dir, exist_ok=True)
                            dst = os.path.join(dst_dir, filename)
                            if os.path.exists(src):
                                shutil.copy(src, dst)
                                game_state.add_log(f"[自动传输] 文件 {filename} 已从 {member_name} 共享至 {target}" if game_state.language == "cn" else f"[Auto Transfer] File {filename} shared from {member_name} to {target}")
                                # Trigger background wakeup for target
                                trigger_background_agent_loop("group", game_state)
                        else:
                            app_id = f"transfer_{int(time.time()*1000)}"
                            game_state.pending_approvals.append({
                                "id": app_id,
                                "type": "file_transfer",
                                "source": member_name,
                                "target": target,
                                "filename": filename,
                                "title": f"共享文件请求: {member_name} -> {target}" if game_state.language == "cn" else f"File Shared Request: {member_name} -> {target}",
                                "description": f"{member_name} 请求将工作区文件 `{filename}` 传输给 {target}。"
                            })
                            student.status = "等待审批" if game_state.language == "cn" else "Awaiting Approval"
                            student.activity = "等待教授批准文件传输..." if game_state.language == "cn" else "Awaiting file transfer approval..."
                            
                elif action_type == "request_approval":
                    app_type = params.get("type")
                    title = params.get("title")
                    description = params.get("description")
                    content = params.get("content")
                    
                    app_id = f"approval_{int(time.time()*1000)}"
                    game_state.pending_approvals.append({
                        "id": app_id,
                        "type": app_type,
                        "student": member_name,
                        "title": title,
                        "description": description,
                        "content": content
                    })
                    student.status = "等待审批" if game_state.language == "cn" else "Awaiting Approval"
                    student.activity = f"审核中：{title}" if game_state.language == "cn" else f"Awaiting review: {title}"
                    
            game_state.save()
            
            # Since an agent reacted, let's break and give other agents a chance in the next background loop
            break
