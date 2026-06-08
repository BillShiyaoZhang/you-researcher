import os
import random
import shutil
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.game_state import GameState, Student, Project, SAVE_FILE, LLMConfig, ChatChannel, ChatMessage
from app.agent_manager import (
    trigger_background_agent_loop,
    fetch_api_balance,
    SYSTEM_PROMPTS
)

app = FastAPI(title="Professor Simulator API")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
game_state = GameState.load()

# Local directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
SANDBOX_DIR = os.path.join(BASE_DIR, "sandbox_env")
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

class ProjectInit(BaseModel):
    topic: str

class ApprovalInput(BaseModel):
    approval_id: str
    decision: str  # approve / reject
    feedback: Optional[str] = None

class MessageInput(BaseModel):
    message: str

class InterveneInput(BaseModel):
    student_name: str
    message: str

class ConnectionCheckInput(BaseModel):
    provider: str
    api_key: str
    base_url: str
    model: str

class SettingsInput(BaseModel):
    provider: str
    api_key: str
    base_url: str
    model: str
    autonomous_mode: bool
    max_cost_limit: float
    funding_mode: str

class LanguageInput(BaseModel):
    language: str

class CommentInput(BaseModel):
    filename: str
    student: str
    comment: str

@app.get("/api/game/files")
def get_workspace_files():
    files = []
    if not os.path.exists(WORKSPACE_DIR):
        return files
        
    students = ["Alice", "Bob", "Charlie"]
    project = game_state.current_project
    comments_map = project.file_comments if project else {}
    
    for student in students:
        student_dir = os.path.join(WORKSPACE_DIR, student)
        if not os.path.exists(student_dir):
            continue
            
        for filename in os.listdir(student_dir):
            fpath = os.path.join(student_dir, filename)
            if os.path.isfile(fpath) and filename.endswith(('.md', '.py', '.txt', '.log')):
                content = ""
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    content = f"Error reading file: {str(e)}"
                
                comments_key = f"{student}/{filename}"
                comments = comments_map.get(comments_key, [])
                
                files.append({
                    "name": filename,
                    "student": student,
                    "exists": True,
                    "content": content,
                    "comments": comments
                })
    return files

@app.post("/api/game/comment")
def add_file_comment(data: CommentInput):
    global game_state
    project = game_state.current_project
    if not project or project.status != "Active":
        raise HTTPException(
            status_code=400,
            detail="No active project to comment on." if game_state.language == "en" else "当前没有进行中的项目可以发表批注。"
        )
    
    filename = data.filename
    student = data.student
    comments_key = f"{student}/{filename}"
    
    if comments_key not in project.file_comments:
        project.file_comments[comments_key] = []
        
    project.file_comments[comments_key].append(data.comment)
    
    is_chinese = (game_state.language == "cn")
    game_state.add_log(
        f"导师对 {student} 的文件 {filename} 发表了批注：'{data.comment}'" 
        if is_chinese else 
        f"PI added an annotation on {student}'s {filename}: '{data.comment}'"
    )
    
    # Comments update wakes up the target agent
    trigger_background_agent_loop("group", game_state)
    
    game_state.save()
    return {"status": "ok", "comments": project.file_comments[comments_key]}

@app.get("/api/game/state")
def get_state():
    return {
        "funding": game_state.funding,
        "reputation": game_state.reputation,
        "day": game_state.day,
        "language": game_state.language,
        "current_project": game_state.current_project.model_dump() if game_state.current_project else None,
        "students": [s.model_dump() for s in game_state.students],
        "system_logs": game_state.system_logs,
        "pending_approvals": game_state.pending_approvals,
        "autonomous_mode": game_state.autonomous_mode,
        "max_cost_limit": game_state.max_cost_limit,
        "session_cost": game_state.session_cost,
        "funding_mode": game_state.funding_mode,
        "llm_config": game_state.llm_config.model_dump(),
        "channels": [c.model_dump() for c in game_state.channels]
    }

@app.post("/api/game/settings")
def update_settings(data: SettingsInput):
    global game_state
    game_state.llm_config.provider = data.provider
    game_state.llm_config.api_key = data.api_key
    game_state.llm_config.base_url = data.base_url
    game_state.llm_config.model = data.model
    game_state.autonomous_mode = data.autonomous_mode
    game_state.max_cost_limit = data.max_cost_limit
    game_state.funding_mode = data.funding_mode
    
    # Try fetching balance if mode is real
    if data.funding_mode == "real":
        real_bal = fetch_api_balance(data.provider, data.api_key, data.base_url)
        if real_bal is not None:
            game_state.funding = real_bal
            game_state.add_log(f"成功同步真实 API 账户余额：¥{real_bal:.2f}")
        else:
            game_state.add_log("未能获取真实余额，继续使用现有模拟经费。")
            
    game_state.save()
    return get_state()

@app.post("/api/game/check_connection")
def check_connection(data: ConnectionCheckInput):
    api_key = data.api_key.strip()
    base_url = data.base_url.strip()
    model = data.model.strip()
    provider = data.provider
    
    if not api_key:
        return {"status": "error", "message": "API Key is required." if game_state.language == "en" else "API Key 不能为空。"}
        
    try:
        from openai import OpenAI
        client_args = {"api_key": api_key}
        if base_url:
            client_args["base_url"] = base_url
        client = OpenAI(**client_args)
        
        # Test completion call
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=2,
            timeout=8
        )
        
        # Test fetching balance
        real_bal = fetch_api_balance(provider, api_key, base_url)
        if real_bal is not None:
            return {
                "status": "ok",
                "has_balance": True,
                "balance": real_bal,
                "message": f"连接测试成功！接口连通且已成功获取账户余额：¥{real_bal:.2f}" if game_state.language == "cn" else f"Connection check successful! Balance retrieved: ¥{real_bal:.2f}"
            }
        else:
            return {
                "status": "ok",
                "has_balance": False,
                "message": "连接测试成功！接口可以连通，但无法获取余额参数。将强制使用模拟经费（模拟额度 ¥500,000.00）。" if game_state.language == "cn" else "Connected successfully! However, balance could not be fetched. Simulated funding mode will be forced."
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"连接测试失败：无法连通大模型接口。报错详情: {str(e)}" if game_state.language == "cn" else f"Connection check failed: {str(e)}"
        }

@app.post("/api/game/set_language")
def set_language(data: LanguageInput):
    global game_state
    lang = data.language
    if lang not in ["cn", "en"]:
        raise HTTPException(status_code=400, detail="Invalid language choice.")
    
    game_state.language = lang
    
    # Translate students' roles, statuses and activities dynamically to match UI
    role_map = {
        "cn": {
            "Deep Learning Hacker": "深度学习极客",
            "Theoretical Researcher": "学术理论家",
            "Enthusiastic PhD Intern": "热情的 PhD 实习生",
            "Idle": "空闲",
            "Resting": "休息中",
            "Searching ArXiv": "文献检索",
            "Writing Proposal": "撰写开题报告",
            "Awaiting PI Approval": "等待教授审批",
            "Experimenting": "实验中",
            "Writing Draft": "撰写论文",
            "Awaiting instructions.": "等待指令。"
        },
        "en": {
            "深度学习极客": "Deep Learning Hacker",
            "学术理论家": "Theoretical Researcher",
            "热情的 PhD 实习生": "Enthusiastic PhD Intern",
            "空闲": "Idle",
            "休息中": "Resting",
            "文献检索": "Searching ArXiv",
            "撰写开题报告": "Writing Proposal",
            "等待教授审批": "Awaiting PI Approval",
            "实验中": "Experimenting",
            "撰写论文": "Writing Draft",
            "等待指令。": "Awaiting instructions."
        }
    }
    
    for s in game_state.students:
        s.role = role_map[lang].get(s.role, s.role)
        s.status = role_map[lang].get(s.status, s.status)
        s.activity = role_map[lang].get(s.activity, s.activity)
        
    game_state.save()
    return get_state()

@app.post("/api/game/init_project")
def init_project(data: ProjectInit):
    global game_state
    if game_state.current_project and game_state.current_project.status == "Active":
        raise HTTPException(status_code=400, detail="A project is already active." if game_state.language == "en" else "当前已有正在进行的科研项目。")
    
    # Initialize workspace subdirectories
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    students = ["Alice", "Bob", "Charlie"]
    for s_name in students:
        os.makedirs(os.path.join(WORKSPACE_DIR, s_name), exist_ok=True)
        
    game_state.current_project = Project(topic=data.topic)
    game_state.pending_approvals = []
    game_state.session_cost = 0.0
    
    # Reset students
    is_chinese = (game_state.language == "cn")
    for student in game_state.students:
        student.status = "空闲" if is_chinese else "Idle"
        student.activity = "等待指令。" if is_chinese else "Awaiting instructions."
        student.thoughts = []
        student.logs = []
        student.energy = 100
        
    # Initialize default channels
    game_state.channels = [
        ChatChannel(
            id="group",
            name="实验室群聊" if is_chinese else "Lab Group Chat",
            members=["Alice", "Bob", "Charlie", "PI"],
            messages=[
                ChatMessage(
                    id="init_msg",
                    sender="System",
                    role="Moderator",
                    message="新课题已启动！文献讨论组已自动开启。" if is_chinese else "New project started! Discussion channel initialized.",
                    timestamp=time.time()
                )
            ]
        ),
        ChatChannel(id="alice", name="Alice (私聊)" if is_chinese else "Alice (Private)", members=["Alice", "PI"]),
        ChatChannel(id="bob", name="Bob (私聊)" if is_chinese else "Bob (Private)", members=["Bob", "PI"]),
        ChatChannel(id="charlie", name="Charlie (私聊)" if is_chinese else "Charlie (Private)", members=["Charlie", "PI"])
    ]
    
    game_state.add_log(
        f"启动了新科研项目：'{data.topic}'" 
        if is_chinese else 
        f"Started new research project: '{data.topic}'"
    )
    
    # Trigger Bob to wake up on group chat to search literature immediately
    trigger_background_agent_loop("group", game_state)
    
    game_state.save()
    return get_state()

@app.post("/api/game/channels/{channel_id}/messages")
def send_channel_message(channel_id: str, data: MessageInput):
    global game_state
    channel = next((c for c in game_state.channels if c.id == channel_id), None)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
        
    msg_id = f"msg_{int(time.time()*1000)}"
    channel.messages.append(ChatMessage(
        id=msg_id,
        sender="PI",
        role="PI" if game_state.language == "en" else "导师/教授",
        message=data.message,
        timestamp=time.time()
    ))
    channel.unread = False
    
    # Reset consecutive counts since user spoke
    from app.agent_manager import consecutive_replies
    consecutive_replies[channel_id] = 0
    
    # Trigger background wakeups for agents in this channel
    trigger_background_agent_loop(channel_id, game_state)
    
    game_state.save()
    return get_state()

@app.post("/api/game/channels/{channel_id}/read")
def read_channel(channel_id: str):
    global game_state
    channel = next((c for c in game_state.channels if c.id == channel_id), None)
    if channel:
        channel.unread = False
        game_state.save()
    return get_state()

@app.post("/api/game/approve")
def handle_approval(data: ApprovalInput):
    global game_state
    approval = next((ap for ap in game_state.pending_approvals if ap["id"] == data.approval_id), None)
    if not approval:
        raise HTTPException(
            status_code=404, 
            detail="Approval request not found" if game_state.language == "en" else "未找到待审批的项目"
        )
        
    game_state.pending_approvals = [ap for ap in game_state.pending_approvals if ap["id"] != data.approval_id]
    
    is_cn = (game_state.language == "cn")
    app_type = approval.get("type")
    
    if data.decision.lower() == "approve":
        if app_type == "file_transfer":
            source = approval["source"]
            target = approval["target"]
            filename = approval["filename"]
            
            src_path = os.path.join(WORKSPACE_DIR, source, filename)
            dst_dir = os.path.join(WORKSPACE_DIR, target)
            os.makedirs(dst_dir, exist_ok=True)
            dst_path = os.path.join(dst_dir, filename)
            
            if os.path.exists(src_path):
                shutil.copy(src_path, dst_path)
                game_state.add_log(f"教授批准文件共享：{filename} 已从 {source} 工作区复制到 {target}")
                # Trigger target agent update
                trigger_background_agent_loop("group", game_state)
            else:
                game_state.add_log(f"传输失败：找不到源文件 {filename}")
                
        elif app_type == "proposal_approval":
            project = game_state.current_project
            if project:
                project.stage = "Experimentation"
            game_state.add_log("教授批准了开题报告！Alice 开始启动沙箱实验。")
            # Wake up Alice
            trigger_background_agent_loop("group", game_state)
            
        elif app_type == "run_sandbox":
            student_name = approval["student"]
            student = next((s for s in game_state.students if s.name == student_name), None)
            student_ws_dir = os.path.join(WORKSPACE_DIR, student_name)
            
            code_path = os.path.join(student_ws_dir, "experiment.py")
            code_block = ""
            if os.path.exists(code_path):
                with open(code_path, "r", encoding="utf-8") as f_in:
                    code_block = f_in.read()
            else:
                code_block = "print('Running default simulation...')"
                
            if student:
                student.status = "实验中" if is_cn else "Experimenting"
                student.activity = "运行沙箱实验脚本..." if is_cn else "Executing code sandbox..."
                
            from app.sandbox import execute_python_code
            sandbox_result = execute_python_code(code_block, student_ws_dir)
            stdout = sandbox_result.get("stdout", "")
            stderr = sandbox_result.get("stderr", "")
            exit_code = sandbox_result.get("exit_code", -1)
            
            with open(os.path.join(student_ws_dir, "results.log"), "w", encoding="utf-8") as f_out:
                f_out.write(f"--- Sandbox Exit Code: {exit_code} ---\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
                
            if student:
                student.thoughts.append("沙箱实验已顺利跑通。结果写入 results.log。" if is_cn else "Sandbox finished. Output saved to results.log.")
                student.status = "空闲" if is_cn else "Idle"
                student.activity = "沙箱脚本执行完毕。" if is_cn else "Sandbox run completed."
                student.energy = max(0, student.energy - 25)
                
            # Deduct sandbox run expense
            sandbox_cost = 5.0
            game_state.funding = max(0.0, game_state.funding - sandbox_cost)
            game_state.add_log(f"批准 Alice 运行沙箱实验，扣除设施使用费 ¥{sandbox_cost:.2f}" if is_cn else f"Approved Alice's sandbox experiment, cost ¥{sandbox_cost:.2f}")
            
            # Wake up Alice to notice results
            trigger_background_agent_loop("group", game_state)
            
        elif app_type == "paper_submission":
            project = game_state.current_project
            # conference name can be passed in feedback
            conf = data.feedback or "NeurIPS"
            
            reg_fee = 6800.0
            if game_state.funding < reg_fee:
                raise HTTPException(
                    status_code=400, 
                    detail="Insufficient funding to pay conference fee." if is_cn else "经费不足，无法支付会议注册费。"
                )
                
            game_state.funding -= reg_fee
            
            bob = next((s for s in game_state.students if s.name == "Bob"), None)
            alice = next((s for s in game_state.students if s.name == "Alice"), None)
            writing_factor = bob.skills["writing"] if bob else 0.5
            coding_factor = alice.skills["coding"] if alice else 0.5
            
            score = random.uniform(3.0, 7.5) + (writing_factor * 2.0) + (coding_factor * 1.0)
            
            reviews = []
            if score >= 7.5:
                funding_reward = 100000.0
                rep_reward = 15.0
                if is_cn:
                    reviews = [
                        "审稿人 1：评分 8 (强烈推荐录用)。方法新颖，实验效果明显。",
                        "审稿人 2：评分 7 (录用)。数学证明严谨，可读性极高。",
                        "审稿人 3：评分 8 (录用)。是一篇很棒的自适应算法改良论文。"
                    ]
                else:
                    reviews = [
                        "Reviewer 1: Score 8 (Strong Accept). Novel method, solid results.",
                        "Reviewer 2: Score 7 (Accept). Rigorous math proof and very well written.",
                        "Reviewer 3: Score 8 (Accept). A clean contribution."
                    ]
                game_state.funding += funding_reward
                game_state.reputation += rep_reward
                if project:
                    project.status = "Completed"
                    project.stage = "Completed (Accepted)" if not is_cn else "已结束 (录用)"
                game_state.add_log(f"🎉 祝贺！论文被 {conf} 正式录用！获得奖励经费 ¥{funding_reward:.2f} 及声望 +{rep_reward}！")
            else:
                if is_cn:
                    reviews = [
                        "审稿人 1：评分 4 (拒稿)。对比不够充分。",
                        "审稿人 2：评分 5 (弱拒)。方法偏向增量式改进。",
                        "审稿人 3：评分 4 (拒稿)。缺乏多场景的深度分析。"
                    ]
                else:
                    reviews = [
                        "Reviewer 1: Score 4 (Reject). Insufficient baseline comparison.",
                        "Reviewer 2: Score 5 (Weak Reject). Incremental improvement.",
                        "Reviewer 3: Score 4 (Reject). Lacks multi-environment experiments."
                    ]
                if project:
                    project.stage = "Paper Writing"
                game_state.add_log(f"投稿遗憾被拒 (评分 {score:.1f}/10)。论文退回 Bob 修改。")
                if bob:
                    bob.status = "撰写论文" if is_cn else "Writing Draft"
                    
            if project:
                project.reviews = reviews
    else:
        # Reject and give feedback
        feedback = data.feedback or ("请修改设计。" if is_cn else "Please revise the design.")
        student_name = approval.get("student") or approval.get("source")
        game_state.add_log(f"教授驳回了申请。反馈意见：'{feedback}'")
        
        if student_name:
            student = next((s for s in game_state.students if s.name == student_name), None)
            if student:
                student.thoughts.append(f"教授驳回了我的请求，修改意见: {feedback}")
                student.status = "空闲" if is_cn else "Idle"
                
        # Wake up student
        trigger_background_agent_loop("group", game_state)
        
    game_state.save()
    return get_state()

@app.post("/api/game/intervene")
def intervene(data: InterveneInput):
    # Backward compatibility: mapping student private chat message to channel messages
    channel_id = data.student_name.lower()
    return send_channel_message(channel_id, MessageInput(message=data.message))

@app.post("/api/game/reset")
def reset_game():
    global game_state
    if os.path.exists(SAVE_FILE):
        try:
            os.remove(SAVE_FILE)
        except Exception:
            pass
            
    if os.path.exists(WORKSPACE_DIR):
        try:
            shutil.rmtree(WORKSPACE_DIR)
        except Exception:
            pass
            
    game_state = GameState.load()
    return get_state()

# Serve frontend build static files if they exist
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
