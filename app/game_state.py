import json
import os
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "save_state.json")

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

class GameState(BaseModel):
    funding: float = 10000.0
    reputation: float = 0.0
    day: int = 1
    current_project: Optional[Project] = None
    students: List[Student] = Field(default_factory=list)
    system_logs: List[str] = Field(default_factory=list)
    pending_approvals: List[Dict[str, Any]] = Field(default_factory=list)

    def add_log(self, text: str):
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
        state.students = [
            Student(
                name="Alice",
                role="Deep Learning Hacker",
                skills={"research": 0.6, "coding": 0.9, "writing": 0.5},
            ),
            Student(
                name="Bob",
                role="Theoretical Researcher",
                skills={"research": 0.9, "coding": 0.4, "writing": 0.9},
            ),
            Student(
                name="Charlie",
                role="Enthusiastic PhD Intern",
                skills={"research": 0.5, "coding": 0.6, "writing": 0.6},
            )
        ]
        state.add_log("Lab opened! Welcome back, Professor.")
        state.save()
        return state
