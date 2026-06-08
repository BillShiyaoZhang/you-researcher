import os
import random
import shutil
from fastapi import FastAPI, HTTPException, BackgroundTasks
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
    run_group_discussion
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
    {"sender": "System", "role": "Moderator", "message": "Group meeting opened. Welcome, Professor."}
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

@app.get("/api/game/state")
def get_state():
    return {
        "funding": game_state.funding,
        "reputation": game_state.reputation,
        "day": game_state.day,
        "current_project": game_state.current_project.model_dump() if game_state.current_project else None,
        "students": [s.model_dump() for s in game_state.students],
        "system_logs": game_state.system_logs,
        "pending_approvals": game_state.pending_approvals,
        "meeting_chat": meeting_chat
    }

@app.post("/api/game/init_project")
def init_project(data: ProjectInit):
    global game_state
    if game_state.current_project and game_state.current_project.status == "Active":
        raise HTTPException(status_code=400, detail="A project is already active.")
    
    # Initialize workspace
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    game_state.current_project = Project(topic=data.topic)
    game_state.pending_approvals = []
    
    # Reset students
    for student in game_state.students:
        student.status = "Idle"
        student.activity = "Awaiting instructions."
        student.thoughts = []
        student.logs = []
        
    game_state.add_log(f"Started new research project: '{data.topic}'")
    
    # Assign Bob to start literature review immediately
    bob = next((s for s in game_state.students if s.name == "Bob"), game_state.students[0])
    bob.status = "Searching ArXiv"
    bob.activity = f"Literature review on '{data.topic}'"
    
    game_state.save()
    return get_state()

@app.post("/api/game/tick")
def game_tick():
    global game_state
    game_state.day += 1
    
    # Daily costs
    daily_cost = 150.0 + (len(game_state.students) * 50.0)
    game_state.funding = max(0.0, game_state.funding - daily_cost)
    game_state.add_log(f"Daily operational expenses: ${daily_cost:.2f}")
    
    if game_state.funding <= 0:
        game_state.add_log("CRITICAL: Lab has run out of funding!")
        
    # Re-charge resting student energy
    for s in game_state.students:
        if s.status == "Resting":
            s.energy = min(100, s.energy + 35)
            if s.energy >= 80:
                s.status = "Idle"
                s.activity = "Finished resting. Ready for work!"
                s.thoughts.append("I feel fully charged and ready to hack!")
                
    project = game_state.current_project
    if not project or project.status != "Active":
        game_state.save()
        return get_state()
        
    # Progress active tasks
    if project.stage == "Literature Review":
        # Find Bob (or whoever is assigned)
        bob = next((s for s in game_state.students if s.name == "Bob"), game_state.students[0])
        if bob.status == "Resting":
            game_state.add_log("Bob is too tired to do literature review. Literature synthesis delayed.")
        else:
            bob.energy = max(0, bob.energy - 30)
            try:
                review_text = run_literature_review(bob, project)
                project.proposal_draft = review_text
                
                # Write to workspace file
                with open(os.path.join(WORKSPACE_DIR, "literature_review.md"), "w", encoding="utf-8") as f:
                    f.write(review_text)
                    
                project.stage = "Proposal"
                game_state.add_log("Bob completed the ArXiv literature synthesis. File saved to workspace/literature_review.md")
                
                # Assign Alice to draft the proposal next day
                alice = next((s for s in game_state.students if s.name == "Alice"), game_state.students[0])
                if alice.status != "Resting":
                    alice.status = "Writing Proposal"
                    alice.activity = "Drafting experiment proposal..."
            except Exception as e:
                game_state.add_log(f"Error in literature review: {str(e)}")
                bob.status = "Idle"
                
    elif project.stage == "Proposal":
        alice = next((s for s in game_state.students if s.name == "Alice"), game_state.students[0])
        if alice.status == "Resting":
            game_state.add_log("Alice is resting. Proposal drafting delayed.")
        else:
            alice.energy = max(0, alice.energy - 30)
            try:
                proposal_text = run_proposal_drafting(alice, project)
                project.proposal_draft = proposal_text
                
                with open(os.path.join(WORKSPACE_DIR, "proposal.md"), "w", encoding="utf-8") as f:
                    f.write(proposal_text)
                    
                # Create a pending approval
                game_state.pending_approvals.append({
                    "id": "approve_proposal",
                    "title": f"Review Project Proposal: {project.topic[:40]}...",
                    "description": "Alice has drafted a research proposal including experiment code. Review and approve to start execution.",
                    "content": proposal_text
                })
                project.stage = "Awaiting Proposal Approval"
                game_state.add_log("Alice finished the research proposal. Pending Professor's approval.")
            except Exception as e:
                game_state.add_log(f"Error in proposal drafting: {str(e)}")
                alice.status = "Idle"
                
    elif project.stage == "Experimentation":
        alice = next((s for s in game_state.students if s.name == "Alice"), game_state.students[0])
        if alice.status == "Resting":
            game_state.add_log("Alice is resting. Experimentation run delayed.")
        else:
            alice.energy = max(0, alice.energy - 40)
            try:
                # Run experiment code
                sandbox_result = run_experimentation(alice, project, SANDBOX_DIR)
                exit_code = sandbox_result.get("exit_code", -1)
                
                # Copy the experiment code to workspace
                if os.path.exists(os.path.join(SANDBOX_DIR, "experiment.py")):
                    shutil.copy(os.path.join(SANDBOX_DIR, "experiment.py"), os.path.join(WORKSPACE_DIR, "experiment.py"))
                    
                if exit_code == 0:
                    project.stage = "Paper Writing"
                    game_state.add_log("Alice ran the experiment. Exit code: 0. Output saved to workspace/experiment.py and project results.")
                    
                    # Assign Bob to start paper writing
                    bob = next((s for s in game_state.students if s.name == "Bob"), game_state.students[0])
                    if bob.status != "Resting":
                        bob.status = "Writing Draft"
                        bob.activity = "Structuring research paper draft..."
                else:
                    game_state.add_log(f"CRITICAL: Experiment run failed with exit code {exit_code}. Alice is debugging...")
                    # Allow Alice to retry once next day
                    project.stage = "Experimentation"
            except Exception as e:
                game_state.add_log(f"Error in experiment: {str(e)}")
                alice.status = "Idle"
                
    elif project.stage == "Paper Writing":
        bob = next((s for s in game_state.students if s.name == "Bob"), game_state.students[0])
        if bob.status == "Resting":
            game_state.add_log("Bob is resting. Paper writing delayed.")
        else:
            bob.energy = max(0, bob.energy - 35)
            try:
                paper_text = run_paper_drafting(bob, project)
                project.paper_draft = paper_text
                
                with open(os.path.join(WORKSPACE_DIR, "paper.md"), "w", encoding="utf-8") as f:
                    f.write(paper_text)
                    
                project.stage = "Awaiting Submission"
                game_state.add_log("Bob finished drafting the paper. File saved to workspace/paper.md. Ready for conference submission.")
            except Exception as e:
                game_state.add_log(f"Error in paper writing: {str(e)}")
                bob.status = "Idle"
                
    # Energy exhaustion check
    for s in game_state.students:
        if s.energy < 15 and s.status != "Resting":
            s.status = "Resting"
            s.activity = "Sleeping and recharging energy."
            s.thoughts.append("I am completely burned out... I need to sleep.")
            game_state.add_log(f"Student {s.name} is burned out and is resting today.")

    game_state.save()
    return get_state()

@app.post("/api/game/approve_proposal")
def approve_proposal(data: ApprovalDecision):
    global game_state
    project = game_state.current_project
    if not project or project.stage != "Awaiting Proposal Approval":
        raise HTTPException(status_code=400, detail="No proposal is pending approval.")
        
    game_state.pending_approvals = [ap for ap in game_state.pending_approvals if ap["id"] != "approve_proposal"]
    
    if data.decision.lower() == "approve":
        project.stage = "Experimentation"
        game_state.add_log("Professor approved the proposal. Starting sandbox experiment execution!")
        
        # Trigger Alice to execute
        alice = next((s for s in game_state.students if s.name == "Alice"), game_state.students[0])
        if alice.status != "Resting":
            alice.status = "Experimenting"
            alice.activity = "Executing script in sandbox environment."
    else:
        # Reject and return to Proposal stage with feedback
        project.stage = "Proposal"
        feedback = data.feedback or "Please revise the experiment design."
        game_state.add_log(f"Professor rejected the proposal. Feedback: '{feedback}'")
        
        # Give feedback to Alice
        alice = next((s for s in game_state.students if s.name == "Alice"), game_state.students[0])
        alice.thoughts.append(f"Professor requested revisions: {feedback}")
        alice.status = "Writing Proposal"
        alice.activity = "Revising proposal draft based on feedback."
        
    game_state.save()
    return get_state()

@app.post("/api/game/submit_paper")
def submit_paper(data: SubmissionInput):
    global game_state
    project = game_state.current_project
    if not project or project.stage != "Awaiting Submission":
        raise HTTPException(status_code=400, detail="No paper is ready for submission.")
        
    # Cost to submit (conference registration/fees)
    reg_fee = 800.0
    if game_state.funding < reg_fee:
        raise HTTPException(status_code=400, detail="Insufficient funding to register/submit paper.")
    
    game_state.funding -= reg_fee
    
    # Calculate score based on student skills and success factors
    bob = next((s for s in game_state.students if s.name == "Bob"), None)
    alice = next((s for s in game_state.students if s.name == "Alice"), None)
    
    writing_factor = bob.skills["writing"] if bob else 0.5
    coding_factor = alice.skills["coding"] if alice else 0.5
    
    # Random variance + factors
    score = random.uniform(3.0, 7.5) + (writing_factor * 2.0) + (coding_factor * 1.0)
    
    reviews = []
    if score >= 7.5:
        decision = "ACCEPTED"
        funding_reward = 8000.0
        rep_reward = 15.0
        reviews = [
            "Reviewer 1: Score 8 (Strong Accept). The methodology is highly novel and sandbox results demonstrate clear improvement.",
            "Reviewer 2: Score 7 (Accept). A clean and well-written paper. The sandbox evaluation is convincing.",
            "Reviewer 3: Score 8 (Accept). Outstanding variance analysis. Very solid drop-in replacement."
        ]
        game_state.funding += funding_reward
        game_state.reputation += rep_reward
        project.status = "Completed"
        project.stage = "Completed (Accepted)"
        game_state.add_log(f"CONGRATULATIONS! Our paper was ACCEPTED at {data.conference}! Won a ${funding_reward} grant and +{rep_reward} Reputation!")
    else:
        decision = "REJECTED"
        reviews = [
            f"Reviewer 1: Score 4 (Reject). The contribution is incremental and baseline evaluations are limited.",
            f"Reviewer 2: Score 5 (Weak Reject). Methodology section requires more details, though writing is solid.",
            f"Reviewer 3: Score 4 (Reject). Not enough experiments to justify generalizability."
        ]
        # Return to writing stage to improve it
        project.stage = "Paper Writing"
        game_state.add_log(f"Paper REJECTED at {data.conference}. Score: {score:.1f}/10. Returning draft to Bob for revisions.")
        if bob:
            bob.thoughts.append(f"Our paper got rejected from {data.conference}. Let's work harder on revising the methodology.")
            bob.status = "Writing Draft"
            
    project.reviews = reviews
    game_state.save()
    return get_state()

@app.post("/api/game/group_chat")
def group_chat(data: ChatInput):
    global meeting_chat
    meeting_chat.append({
        "sender": "Professor",
        "role": "PI",
        "message": data.message
    })
    
    # Trigger agents to reply
    active_students = [s for s in game_state.students if s.status != "Resting"]
    replies = run_group_discussion(active_students, meeting_chat[:-1], data.message)
    
    for r in replies:
        meeting_chat.append(r)
        
    game_state.save()
    return get_state()

@app.post("/api/game/intervene")
def intervene(data: InterveneInput):
    global game_state
    student = next((s for s in game_state.students if s.name.lower() == data.student_name.lower()), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
        
    student.thoughts.append(f"PI message: '{data.message}'")
    
    # Let the student reply
    sys_prompt = SYSTEM_PROMPTS[student.name] + f"\nYou are responding directly to a private message from your Professor. Your status is: {student.status}."
    reply = call_llm(sys_prompt, f"Professor private message: '{data.message}'\nReply in character (1-2 sentences).")
    
    student.thoughts.append(f"My reply: '{reply}'")
    game_state.save()
    
    return {
        "reply": reply,
        "state": get_state()
    }

@app.post("/api/game/reset")
def reset_game():
    global game_state, meeting_chat
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
        {"sender": "System", "role": "Moderator", "message": "Group meeting reset. Welcome, Professor."}
    ]
    return get_state()

# Serve frontend build static files if they exist
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
