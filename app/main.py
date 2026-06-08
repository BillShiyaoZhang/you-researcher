import os
import random
import shutil
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.game_state import GameState, Student, Project, SAVE_FILE
from app.agent_manager import (
    run_literature_review, 
    run_proposal_drafting, 
    run_experimentation, 
    run_paper_drafting,
    run_group_discussion,
    SYSTEM_PROMPTS,
    call_llm
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

# In-memory meeting room chat
meeting_chat = [
    {"sender": "System", "role": "Moderator", "message": "组会已开启。欢迎回来，教授。" if game_state.language == "cn" else "Group meeting opened. Welcome, Professor."}
]

class ProjectInit(BaseModel):
    topic: str

class ApprovalDecision(BaseModel):
    decision: str  # approve / reject
    feedback: Optional[str] = None

class ChatInput(BaseModel):
    message: str

class InterveneInput(BaseModel):
    student_name: str
    message: str

class SubmissionInput(BaseModel):
    conference: str

class LanguageInput(BaseModel):
    language: str

class CommentInput(BaseModel):
    filename: str
    comment: str

@app.get("/api/game/files")
def get_workspace_files():
    files = []
    # Possible files we track:
    expected_files = [
        {"name": "literature_review.md", "type": "markdown", "displayName": "文献综述 / Literature Review"},
        {"name": "proposal.md", "type": "markdown", "displayName": "开题报告 / Research Proposal"},
        {"name": "experiment.py", "type": "python", "displayName": "实验脚本 / Experiment Script"},
        {"name": "paper.md", "type": "markdown", "displayName": "学术论文 / Research Paper"}
    ]
    
    project = game_state.current_project
    comments_map = project.file_comments if project else {}
    
    for f_info in expected_files:
        filename = f_info["name"]
        filepath = os.path.join(WORKSPACE_DIR, filename)
        exists = os.path.exists(filepath)
        content = ""
        if exists:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading file: {str(e)}"
        
        comments = comments_map.get(filename, [])
        files.append({
            "name": filename,
            "displayName": f_info["displayName"],
            "type": f_info["type"],
            "exists": exists,
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
            detail="No active project to comment on." if game_state.language == "en" else "当前没有进行中的项目可以发表评论。"
        )
    
    filename = data.filename
    if filename not in ["literature_review.md", "proposal.md", "experiment.py", "paper.md"]:
        raise HTTPException(status_code=400, detail="Invalid filename.")
        
    if filename not in project.file_comments:
        project.file_comments[filename] = []
        
    project.file_comments[filename].append(data.comment)
    
    is_chinese = (game_state.language == "cn")
    game_state.add_log(
        f"导师对文件 {filename} 发表了批注：'{data.comment}'" 
        if is_chinese else 
        f"PI added an annotation on {filename}: '{data.comment}'"
    )
    game_state.save()
    return {"status": "ok", "comments": project.file_comments[filename]}

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
        "meeting_chat": meeting_chat
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
    
    # Initialize workspace
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    game_state.current_project = Project(topic=data.topic)
    game_state.pending_approvals = []
    
    # Reset students
    is_chinese = (game_state.language == "cn")
    for student in game_state.students:
        student.status = "空闲" if is_chinese else "Idle"
        student.activity = "等待指令。" if is_chinese else "Awaiting instructions."
        student.thoughts = []
        student.logs = []
        
    game_state.add_log(
        f"启动了新科研项目：'{data.topic}'" 
        if is_chinese else 
        f"Started new research project: '{data.topic}'"
    )
    
    # Assign Bob to start literature review immediately
    bob = next((s for s in game_state.students if s.name == "Bob"), game_state.students[0])
    bob.status = "文献检索" if is_chinese else "Searching ArXiv"
    bob.activity = f"正在检索关于 '{data.topic}' 的文献综述" if is_chinese else f"Literature review on '{data.topic}'"
    
    game_state.save()
    return get_state()

@app.post("/api/game/tick")
def game_tick():
    global game_state
    game_state.day += 1
    is_chinese = (game_state.language == "cn")
    
    # Daily costs: Base office overhead ¥100 + Student stipends (¥8,000/month per student, i.e., ¥266.67/student/day)
    base_cost = 100.0
    student_cost = len(game_state.students) * 266.67
    daily_cost = base_cost + student_cost
    game_state.funding = max(0.0, game_state.funding - daily_cost)
    
    game_state.add_log(
        f"每日基本实验室运营开支 (房租水电 ¥{base_cost:.2f} + 学生补贴 ¥{student_cost:.2f})：¥{daily_cost:.2f}" 
        if is_chinese else 
        f"Daily basic lab operating expenses (Office ¥{base_cost:.2f} + Student stipends ¥{student_cost:.2f}): ¥{daily_cost:.2f}"
    )
    
    if game_state.funding <= 0:
        game_state.add_log(
            "严重警告：实验室经费已耗尽！" 
            if is_chinese else 
            "CRITICAL: Lab has run out of funding!"
        )
        
    # Re-charge resting student energy
    for s in game_state.students:
        if s.status == ("休息中" if is_chinese else "Resting"):
            s.energy = min(100, s.energy + 35)
            if s.energy >= 80:
                s.status = "空闲" if is_chinese else "Idle"
                s.activity = "休息结束，重新投入工作！" if is_chinese else "Finished resting. Ready for work!"
                s.thoughts.append("精力充沛，可以继续写代码了！" if is_chinese else "I feel fully charged and ready to hack!")
                
    project = game_state.current_project
    if not project or project.status != "Active":
        game_state.save()
        return get_state()
        
    # Progress active tasks
    if project.stage == "Literature Review":
        bob = next((s for s in game_state.students if s.name == "Bob"), game_state.students[0])
        if bob.status == ("休息中" if is_chinese else "Resting"):
            game_state.add_log(
                "Bob 处于精疲力竭状态。文献综述工作被迫顺延。" 
                if is_chinese else 
                "Bob is too tired to do literature review. Literature synthesis delayed."
            )
        else:
            bob.energy = max(0, bob.energy - 30)
            try:
                review_text = run_literature_review(bob, project, language=game_state.language, game_state=game_state)
                project.proposal_draft = review_text
                
                # Write to workspace file
                with open(os.path.join(WORKSPACE_DIR, "literature_review.md"), "w", encoding="utf-8") as f:
                    f.write(review_text)
                    
                project.stage = "Proposal"
                # Clear comments on literature_review.md as it has been updated
                if "literature_review.md" in project.file_comments:
                    project.file_comments["literature_review.md"] = []

                game_state.add_log(
                    "Bob 完成了文献检索与综述。文件已保存至 workspace/literature_review.md" 
                    if is_chinese else 
                    "Bob completed the ArXiv literature synthesis. File saved to workspace/literature_review.md"
                )
                
                # Assign Alice to draft the proposal next day
                alice = next((s for s in game_state.students if s.name == "Alice"), game_state.students[0])
                if alice.status != ("休息中" if is_chinese else "Resting"):
                    alice.status = "撰写开题报告" if is_chinese else "Writing Proposal"
                    alice.activity = "正在拟定开题报告草案..." if is_chinese else "Drafting experiment proposal..."
            except Exception as e:
                game_state.add_log(f"Error in literature review: {str(e)}")
                bob.status = "空闲" if is_chinese else "Idle"
                
    elif project.stage == "Proposal":
        alice = next((s for s in game_state.students if s.name == "Alice"), game_state.students[0])
        if alice.status == ("休息中" if is_chinese else "Resting"):
            game_state.add_log(
                "Alice 处于精疲力竭状态。开题报告撰写顺延。" 
                if is_chinese else 
                "Alice is resting. Proposal drafting delayed."
            )
        else:
            alice.energy = max(0, alice.energy - 30)
            try:
                proposal_text = run_proposal_drafting(alice, project, language=game_state.language, game_state=game_state)
                project.proposal_draft = proposal_text
                
                with open(os.path.join(WORKSPACE_DIR, "proposal.md"), "w", encoding="utf-8") as f:
                    f.write(proposal_text)
                    
                # Create a pending approval
                if is_chinese:
                    game_state.pending_approvals.append({
                        "id": "approve_proposal",
                        "title": f"评审开题报告: {project.topic[:40]}...",
                        "description": "Alice 已经完成了开题报告草拟（附带实验代码）。请评审并批准以启动实验。",
                        "content": proposal_text
                    })
                else:
                    game_state.pending_approvals.append({
                        "id": "approve_proposal",
                        "title": f"Review Project Proposal: {project.topic[:40]}...",
                        "description": "Alice has drafted a research proposal including experiment code. Review and approve to start execution.",
                        "content": proposal_text
                    })
                project.stage = "Awaiting Proposal Approval"
                # Clear comments on proposal.md as it has been updated
                if "proposal.md" in project.file_comments:
                    project.file_comments["proposal.md"] = []

                game_state.add_log(
                    "Alice 完成了开题报告初稿。等待教授（PI）审核中。" 
                    if is_chinese else 
                    "Alice finished the research proposal. Pending Professor's approval."
                )
            except Exception as e:
                game_state.add_log(f"Error in proposal drafting: {str(e)}")
                alice.status = "空闲" if is_chinese else "Idle"
                
    elif project.stage == "Experimentation":
        alice = next((s for s in game_state.students if s.name == "Alice"), game_state.students[0])
        if alice.status == ("休息中" if is_chinese else "Resting"):
            game_state.add_log(
                "Alice 正在休息。沙箱实验顺延。" 
                if is_chinese else 
                "Alice is resting. Experimentation run delayed."
            )
        else:
            alice.energy = max(0, alice.energy - 40)
            try:
                sandbox_result = run_experimentation(alice, project, SANDBOX_DIR, language=game_state.language, game_state=game_state)
                exit_code = sandbox_result.get("exit_code", -1)
                
                if os.path.exists(os.path.join(SANDBOX_DIR, "experiment.py")):
                    shutil.copy(os.path.join(SANDBOX_DIR, "experiment.py"), os.path.join(WORKSPACE_DIR, "experiment.py"))
                    
                if exit_code == 0:
                    project.stage = "Paper Writing"
                    # Clear comments on experiment.py as it ran successfully
                    if "experiment.py" in project.file_comments:
                        project.file_comments["experiment.py"] = []

                    game_state.add_log(
                        "Alice 完成了沙箱实验，退出码 0。实验代码已同步至 workspace/experiment.py" 
                        if is_chinese else 
                        "Alice ran the experiment. Exit code: 0. Output saved to workspace/experiment.py and project results."
                    )
                    
                    bob = next((s for s in game_state.students if s.name == "Bob"), game_state.students[0])
                    if bob.status != ("休息中" if is_chinese else "Resting"):
                        bob.status = "撰写论文" if is_chinese else "Writing Draft"
                        bob.activity = "正在撰写学术手稿..." if is_chinese else "Structuring research paper draft..."
                else:
                    game_state.add_log(
                        f"警告：实验运行失败，退出码 {exit_code}。Alice 正在尝试 Debug..." 
                        if is_chinese else 
                        f"CRITICAL: Experiment run failed with exit code {exit_code}. Alice is debugging..."
                    )
                    project.stage = "Experimentation"
            except Exception as e:
                game_state.add_log(f"Error in experiment: {str(e)}")
                alice.status = "空闲" if is_chinese else "Idle"
                
    elif project.stage == "Paper Writing":
        bob = next((s for s in game_state.students if s.name == "Bob"), game_state.students[0])
        if bob.status == ("休息中" if is_chinese else "Resting"):
            game_state.add_log(
                "Bob 正在休息。学术论文初稿顺延。" 
                if is_chinese else 
                "Bob is resting. Paper writing delayed."
            )
        else:
            bob.energy = max(0, bob.energy - 35)
            try:
                paper_text = run_paper_drafting(bob, project, language=game_state.language, game_state=game_state)
                project.paper_draft = paper_text
                
                with open(os.path.join(WORKSPACE_DIR, "paper.md"), "w", encoding="utf-8") as f:
                    f.write(paper_text)
                    
                project.stage = "Awaiting Submission"
                # Clear comments on paper.md as draft is ready
                if "paper.md" in project.file_comments:
                    project.file_comments["paper.md"] = []

                game_state.add_log(
                    "Bob 完成了论文撰写。论文草稿已保存至 workspace/paper.md，准备提交会议投稿。" 
                    if is_chinese else 
                    "Bob finished drafting the paper. File saved to workspace/paper.md. Ready for conference submission."
                )
            except Exception as e:
                game_state.add_log(f"Error in paper writing: {str(e)}")
                bob.status = "空闲" if is_chinese else "Idle"
                
    # Energy exhaustion check
    for s in game_state.students:
        if s.energy < 15 and s.status != ("休息中" if is_chinese else "Resting"):
            s.status = "休息中" if is_chinese else "Resting"
            s.activity = "补充睡眠和能量..." if is_chinese else "Sleeping and recharging energy."
            s.thoughts.append(
                "我彻底累垮了……必须睡个饱觉。" 
                if is_chinese else 
                "I am completely burned out... I need to sleep."
            )
            game_state.add_log(
                f"学生 {s.name} 精疲力竭，被迫停工休息。" 
                if is_chinese else 
                f"Student {s.name} is burned out and is resting today."
            )

    game_state.save()
    return get_state()

@app.post("/api/game/approve_proposal")
def approve_proposal(data: ApprovalDecision):
    global game_state
    project = game_state.current_project
    is_chinese = (game_state.language == "cn")
    
    if not project or project.stage != "Awaiting Proposal Approval":
        raise HTTPException(
            status_code=400, 
            detail="No proposal is pending approval." if game_state.language == "en" else "当前没有待审核的开题报告。"
        )
        
    game_state.pending_approvals = [ap for ap in game_state.pending_approvals if ap["id"] != "approve_proposal"]
    
    if data.decision.lower() == "approve":
        project.stage = "Experimentation"
        game_state.add_log(
            "教授批准了该开题报告。正式启动沙箱代码运行！" 
            if is_chinese else 
            "Professor approved the proposal. Starting sandbox experiment execution!"
        )
        
        # Trigger Alice to execute
        alice = next((s for s in game_state.students if s.name == "Alice"), game_state.students[0])
        if alice.status != ("休息中" if is_chinese else "Resting"):
            alice.status = "实验中" if is_chinese else "Experimenting"
            alice.activity = "正在沙箱隔离环境中运行验证脚本。" if is_chinese else "Executing script in sandbox environment."
    else:
        # Reject and return to Proposal stage with feedback
        project.stage = "Proposal"
        feedback = data.feedback or ("请修改实验设计。" if is_chinese else "Please revise the experiment design.")
        game_state.add_log(
            f"教授驳回了开题报告。修改意见：'{feedback}'" 
            if is_chinese else 
            f"Professor rejected the proposal. Feedback: '{feedback}'"
        )
        
        # Give feedback to Alice
        alice = next((s for s in game_state.students if s.name == "Alice"), game_state.students[0])
        alice.thoughts.append(
            f"教授发来了修改意见: {feedback}" 
            if is_chinese else 
            f"Professor requested revisions: {feedback}"
        )
        alice.status = "撰写开题报告" if is_chinese else "Writing Proposal"
        alice.activity = "正在根据教授意见修改开题报告。" if is_chinese else "Revising proposal draft based on feedback."
        
    game_state.save()
    return get_state()

@app.post("/api/game/submit_paper")
def submit_paper(data: SubmissionInput):
    global game_state
    project = game_state.current_project
    is_chinese = (game_state.language == "cn")
    
    if not project or project.stage != "Awaiting Submission":
        raise HTTPException(
            status_code=400, 
            detail="No paper is ready for submission." if game_state.language == "en" else "当前没有待提交的论文草稿。"
        )
        
    # Conference registration fee mapping in RMB
    conf_fees = {
        "NeurIPS": 6800.0,
        "ICML": 6500.0,
        "CVPR": 6800.0,
        "EMNLP": 5800.0
    }
    reg_fee = conf_fees.get(data.conference, 6000.0)
    
    if game_state.funding < reg_fee:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient funding (Requires ¥{reg_fee:.2f}) to submit paper." if game_state.language == "en" else f"经费不足，无法支付会议注册费（需要 ¥{reg_fee:.2f}）。"
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
        if is_chinese:
            reviews = [
                "审稿人 1：评分 8 (强烈推荐录用)。方法非常新颖，沙箱实验展示了明显的理论提升和出色的效果。",
                "审稿人 2：评分 7 (录用)。论文写作严谨且可读性极强。沙箱环境中的对比极具说服力。",
                "审稿人 3：评分 8 (录用)。梯度方差稳定分析很扎实，是一篇扎实的优化器改良论文。"
            ]
        else:
            reviews = [
                "Reviewer 1: Score 8 (Strong Accept). The methodology is highly novel and sandbox results demonstrate clear improvement.",
                "Reviewer 2: Score 7 (Accept). A clean and well-written paper. The sandbox evaluation is convincing.",
                "Reviewer 3: Score 8 (Accept). Outstanding variance analysis. Very solid drop-in replacement."
            ]
        game_state.funding += funding_reward
        game_state.reputation += rep_reward
        project.status = "Completed"
        project.stage = "Completed (Accepted)" if game_state.language == "en" else "已结束 (录用)"
        game_state.add_log(
            f"🎉 祝贺！我们的论文被 {data.conference} 正式录用！荣获了 ¥{funding_reward:.2f} 经费支持和 +{rep_reward} 声望值！" 
            if is_chinese else 
            f"CONGRATULATIONS! Our paper was ACCEPTED at {data.conference}! Won a ¥{funding_reward:.2f} grant and +{rep_reward} Reputation!"
        )
    else:
        if is_chinese:
            reviews = [
                "审稿人 1：评分 4 (拒稿)。所做的工作属于渐进式改进，基线对比不太充分。",
                "审稿人 2：评分 5 (弱拒)。论文写得不错，但方法论章节缺少对泛化能力的实验佐证。",
                "审稿人 3：评分 4 (拒稿)。实验部分过于薄弱，未提供更深维度的调参曲线分析。"
            ]
        else:
            reviews = [
                "Reviewer 1: Score 4 (Reject). The contribution is incremental and baseline evaluations are limited.",
                "Reviewer 2: Score 5 (Weak Reject). Methodology section requires more details, though writing is solid.",
                "Reviewer 3: Score 4 (Reject). Not enough experiments to justify generalizability."
            ]
        project.stage = "Paper Writing"
        game_state.add_log(
            f"投稿驳回：论文在 {data.conference} 遗憾被拒。同行审稿总评分：{score:.1f}/10。手稿退回 Bob 进行修改。" 
            if is_chinese else 
            f"Paper REJECTED at {data.conference}. Score: {score:.1f}/10. Returning draft to Bob for revisions."
        )
        if bob:
            bob.thoughts.append(
                f"在 {data.conference} 投稿失败。我会针对审稿人意见重新修订 Methodology 部分。" 
                if is_chinese else 
                f"Our paper got rejected from {data.conference}. Let's work harder on revising the methodology."
            )
            bob.status = "撰写论文" if is_chinese else "Writing Draft"
            
    project.reviews = reviews
    game_state.save()
    return get_state()

@app.post("/api/game/group_chat")
def group_chat(data: ChatInput):
    global meeting_chat
    meeting_chat.append({
        "sender": "Professor",
        "role": "PI" if game_state.language == "en" else "实验室负责人",
        "message": data.message
    })
    
    # Trigger agents to reply
    is_chinese = (game_state.language == "cn")
    active_students = [s for s in game_state.students if s.status != ("休息中" if is_chinese else "Resting")]
    replies = run_group_discussion(active_students, meeting_chat[:-1], data.message, language=game_state.language, game_state=game_state)
    
    for r in replies:
        meeting_chat.append(r)
        
    game_state.save()
    return get_state()

@app.post("/api/game/intervene")
def intervene(data: InterveneInput):
    global game_state
    student = next((s for s in game_state.students if s.name.lower() == data.student_name.lower()), None)
    is_chinese = (game_state.language == "cn")
    if not student:
        raise HTTPException(status_code=404, detail="Student not found." if game_state.language == "en" else "未找到对应的学生。")
        
    student.thoughts.append(
        f"导师消息：'{data.message}'" 
        if is_chinese else 
        f"PI message: '{data.message}'"
    )
    
    # Let the student reply
    sys_prompt = SYSTEM_PROMPTS[student.name] + (
        f"\n你正在私信直接回复你的教授。你当前的科研状态是: {student.status}。"
        if is_chinese else 
        f"\nYou are responding directly to a private message from your Professor. Your status is: {student.status}."
    )
    
    reply = call_llm(sys_prompt, f"Professor private message: '{data.message}'\nReply in character (1-2 sentences).", language=game_state.language, game_state=game_state, caller_name=student.name)
    
    student.thoughts.append(
        f"我的私信答复：'{reply}'" 
        if is_chinese else 
        f"My reply: '{reply}'"
    )
    game_state.save()
    
    return {
        "reply": reply,
        "state": get_state()
    }

@app.post("/api/game/reset")
def reset_game():
    global game_state, meeting_chat
    is_chinese = (game_state.language == "cn")
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
    meeting_chat = [
        {"sender": "System", "role": "Moderator" if game_state.language == "en" else "主持人", "message": "实验室重置。欢迎回来，教授。" if game_state.language == "cn" else "Group meeting reset. Welcome, Professor."}
    ]
    return get_state()

# Serve frontend build static files if they exist
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
