import json
import os
import time
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "save_state.json")

class LLMConfig(BaseModel):
    provider: str = "openai" # openai, minimax, deepseek, siliconflow, custom
    api_key: str = ""
    base_url: str = ""
    model: str = "gpt-3.5-turbo"

class ChatMessage(BaseModel):
    id: str
    sender: str
    role: str
    message: str
    timestamp: float = Field(default_factory=time.time)

class ChatChannel(BaseModel):
    id: str
    name: str
    members: List[str]
    messages: List[ChatMessage] = Field(default_factory=list)
    unread: bool = False

class Student(BaseModel):
    name: str
    role: str
    skills: Dict[str, float]  # research, coding, writing (0.0 to 1.0)
    energy: int = 100         # 0 to 100
    status: str = "Idle"      # e.g., Idle, Searching ArXiv, Writing Code, Experimenting, Writing Draft
    activity: str = "Awaiting instructions."
    thoughts: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)

class Project(BaseModel):
    topic: str
    stage: str = "Literature Review"  # Literature Review, Proposal, Experimentation, Paper Writing, Completed
    proposal_draft: Optional[str] = None
    experiment_results: Optional[str] = None
    paper_draft: Optional[str] = None
    reviews: Optional[List[str]] = None
    status: str = "Active"
    file_comments: Dict[str, List[str]] = Field(default_factory=dict)

class GameState(BaseModel):
    funding: float = 500000.0
    reputation: float = 0.0
    day: int = 1
    language: str = "cn"  # cn or en
    current_project: Optional[Project] = None
    students: List[Student] = Field(default_factory=list)
    system_logs: List[str] = Field(default_factory=list)
    pending_approvals: List[Dict[str, Any]] = Field(default_factory=list)
    
    # New configurations
    llm_config: LLMConfig = Field(default_factory=LLMConfig)
    autonomous_mode: bool = False
    max_cost_limit: float = 10.0
    session_cost: float = 0.0
    funding_mode: str = "simulated" # real or simulated
    channels: List[ChatChannel] = Field(default_factory=list)

    def add_log(self, text: str):
        if self.language == "cn":
            self.system_logs.append(f"第 {self.day} 天: {text}")
        else:
            self.system_logs.append(f"Day {self.day}: {text}")

    def save(self):
        os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def load(cls) -> "GameState":
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception as e:
                print(f"Error loading save file: {e}")
        # Default initialization
        state = cls()
        if state.language == "cn":
            state.students = [
                Student(
                    name="Alice",
                    role="深度学习极客",
                    skills={"research": 0.6, "coding": 0.9, "writing": 0.5},
                    status="空闲",
                    activity="等待指令。"
                ),
                Student(
                    name="Bob",
                    role="学术理论家",
                    skills={"research": 0.9, "coding": 0.4, "writing": 0.9},
                    status="空闲",
                    activity="等待指令。"
                ),
                Student(
                    name="Charlie",
                    role="热情的 PhD 实习生",
                    skills={"research": 0.5, "coding": 0.6, "writing": 0.6},
                    status="空闲",
                    activity="等待指令。"
                )
            ]
            state.add_log("实验室正式开张！欢迎回来，教授。")
        else:
            state.students = [
                Student(
                    name="Alice",
                    role="Deep Learning Hacker",
                    skills={"research": 0.6, "coding": 0.9, "writing": 0.5},
                    status="Idle",
                    activity="Awaiting instructions."
                ),
                Student(
                    name="Bob",
                    role="Theoretical Researcher",
                    skills={"research": 0.9, "coding": 0.4, "writing": 0.9},
                    status="Idle",
                    activity="Awaiting instructions."
                ),
                Student(
                    name="Charlie",
                    role="Enthusiastic PhD Intern",
                    skills={"research": 0.5, "coding": 0.6, "writing": 0.6},
                    status="Idle",
                    activity="Awaiting instructions."
                )
            ]
            state.add_log("Lab opened! Welcome back, Professor.")
            
        # Initialize default channels
        is_cn = (state.language == "cn")
        state.channels = [
            ChatChannel(
                id="group",
                name="实验室群聊" if is_cn else "Lab Group Chat",
                members=["Alice", "Bob", "Charlie", "PI"],
                messages=[
                    ChatMessage(
                        id="init_msg",
                        sender="System",
                        role="Moderator",
                        message="学术交流通道已建立。欢迎各位！" if is_cn else "Research channel established. Welcome everyone!",
                        timestamp=time.time()
                    )
                ]
            ),
            ChatChannel(id="alice", name="Alice (私聊)" if is_cn else "Alice (Private)", members=["Alice", "PI"]),
            ChatChannel(id="bob", name="Bob (私聊)" if is_cn else "Bob (Private)", members=["Bob", "PI"]),
            ChatChannel(id="charlie", name="Charlie (私聊)" if is_cn else "Charlie (Private)", members=["Charlie", "PI"])
        ]
        
        state.save()
        return state
