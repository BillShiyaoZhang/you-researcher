import os
import shutil
import unittest
from app.arxiv_tool import search_arxiv
from app.sandbox import execute_python_code
from app.game_state import GameState, Project, Student
from app.agent_manager import call_llm

class TestProfessorSimulator(unittest.TestCase):
    
    def test_arxiv_tool(self):
        print("Testing ArXiv Search Tool...")
        results = search_arxiv("attention", max_results=2)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # Verify first entry has title and URL/id
        first = results[0]
        if "error" not in first:
            self.assertIn("title", first)
            self.assertIn("url", first)
            print(f"ArXiv Search Result Success: {first['title']}")
        else:
            print(f"ArXiv Search skipped/failed due to network: {first['error']}")

    def test_sandbox(self):
        print("Testing Python Execution Sandbox...")
        test_dir = "./test_run_env"
        code = "a = 5\nb = 10\nprint(f'Result={a+b}')"
        result = execute_python_code(code, test_dir)
        
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("Result=15", result["stdout"])
        self.assertEqual(result["stderr"], "")
        
        # Cleanup test env
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        print("Sandbox execution verified successfully.")

    def test_mock_llm(self):
        print("Testing LLM Fallback Call...")
        from unittest.mock import MagicMock, patch
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Mock Error")
        with patch("app.agent_manager.OpenAI", return_value=mock_client):
            # Test English mock
            resp_en = call_llm("You are Alice, literature_review.md is in your workspace.", "Write a proposal", language="en", caller_name="Alice")
            self.assertIn("proposal", resp_en.lower())
            self.assertIn("experiment", resp_en.lower())
            
            # Test Chinese mock
            resp_cn = call_llm("You are Alice, literature_review.md is in your workspace.", "Write a proposal", language="cn", caller_name="Alice")
            self.assertIn("开题报告", resp_cn)
            self.assertIn("实验", resp_cn)
        print("LLM Mock Response verified successfully.")

    def test_game_state_flow(self):
        print("Testing Game State transitions...")
        state = GameState()
        state.language = "en"
        # Initialize some students
        state.students = [
            Student(name="Alice", role="Deep Learning Hacker", skills={"research": 0.6, "coding": 0.9, "writing": 0.5}),
            Student(name="Bob", role="Theoretical Researcher", skills={"research": 0.9, "coding": 0.4, "writing": 0.9})
        ]
        
        # Check initial budget
        self.assertEqual(state.funding, 500000.0)
        self.assertEqual(state.day, 1)
        
        # Launch project
        state.current_project = Project(topic="Low-bit quantization")
        self.assertEqual(state.current_project.stage, "Literature Review")
        
        # Test log addition
        state.add_log("Test project initiated.")
        self.assertEqual(len(state.system_logs), 1)
        self.assertIn("Day 1: Test project initiated.", state.system_logs[0])
        print("Game State transitions verified successfully.")

    def test_commenting_endpoints(self):
        print("Testing Commenting Endpoints...")
        from fastapi.testclient import TestClient
        from app.main import app, WORKSPACE_DIR
        
        client = TestClient(app)
        
        # Reset to clear any previous run state
        client.post("/api/game/reset")
        
        # Adding a comment without active project should return 400
        resp = client.post("/api/game/comment", json={"filename": "literature_review.md", "student": "Bob", "comment": "Add details"})
        self.assertEqual(resp.status_code, 400)
        
        # Init project
        client.post("/api/game/init_project", json={"topic": "Quantum Machine Learning"})
        
        # Write dummy file to workspace Bob folder
        bob_dir = os.path.join(WORKSPACE_DIR, "Bob")
        os.makedirs(bob_dir, exist_ok=True)
        with open(os.path.join(bob_dir, "literature_review.md"), "w", encoding="utf-8") as f:
            f.write("Dummy literature review content")
        
        # Now add a comment
        resp = client.post("/api/game/comment", json={"filename": "literature_review.md", "student": "Bob", "comment": "Please focus on attention layers"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("Please focus on attention layers", data["comments"])
        
        # Retrieve files and check comment
        resp_files = client.get("/api/game/files")
        self.assertEqual(resp_files.status_code, 200)
        files = resp_files.json()
        lit_file = next(f for f in files if f["name"] == "literature_review.md")
        self.assertIn("Please focus on attention layers", lit_file["comments"])
        print("Commenting endpoints verified successfully.")
        
    def test_usage_based_costs(self):
        print("Testing Usage-based cost deductions...")
        from app.game_state import GameState
        from app.agent_manager import call_llm
        from unittest.mock import patch
        
        state = GameState()
        state.funding = 1000.0
        
        with patch("app.game_state.GameState.save") as mock_save:
            # Call LLM and check if funding decreases
            call_llm("System prompt", "User prompt", game_state=state)
            self.assertLess(state.funding, 1000.0)
        print("Usage-based cost deductions verified successfully.")

    def test_project_management_lifecycle(self):
        print("Testing Project Management lifecycle...")
        from fastapi.testclient import TestClient
        from app.main import app
        import json
        
        client = TestClient(app)
        
        # 1. Reset everything to start fresh
        client.post("/api/game/reset")
        
        # 2. Get projects (should be empty initially)
        resp = client.get("/api/game/projects")
        self.assertEqual(resp.status_code, 200)
        projects = resp.json()
        self.assertEqual(len(projects), 0)
        
        # 3. Init a new project
        topic_1 = "Adaptive Optimization Schedules"
        resp = client.post("/api/game/init_project", json={"topic": topic_1})
        self.assertEqual(resp.status_code, 200)
        state_1 = resp.json()
        self.assertIsNotNone(state_1["current_project"])
        self.assertEqual(state_1["current_project"]["topic"], topic_1)
        self.assertIsNotNone(state_1["active_project_id"])
        project_id_1 = state_1["active_project_id"]
        
        # 4. List projects (should contain 1 project)
        resp = client.get("/api/game/projects")
        self.assertEqual(resp.status_code, 200)
        projects = resp.json()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["project_id"], project_id_1)
        self.assertEqual(projects[0]["topic"], topic_1)
        
        # 5. Reset the current active project
        resp = client.post("/api/game/projects/reset")
        self.assertEqual(resp.status_code, 200)
        state_reset = resp.json()
        self.assertEqual(state_reset["day"], 1)
        self.assertEqual(state_reset["current_project"]["topic"], topic_1)
        
        # 6. Intent to create new project (wants to back up current project 1 and clear active state)
        resp = client.post("/api/game/projects/new_intent")
        self.assertEqual(resp.status_code, 200)
        state_new_intent = resp.json()
        self.assertIsNone(state_new_intent["current_project"])
        self.assertIsNone(state_new_intent["active_project_id"])
        
        # 7. Start second project
        topic_2 = "Parameter-efficient fine-tuning"
        resp = client.post("/api/game/init_project", json={"topic": topic_2})
        self.assertEqual(resp.status_code, 200)
        state_2 = resp.json()
        project_id_2 = state_2["active_project_id"]
        
        # 8. List projects (should now contain both projects)
        resp = client.get("/api/game/projects")
        self.assertEqual(resp.status_code, 200)
        projects = resp.json()
        self.assertEqual(len(projects), 2)
        topics = [p["topic"] for p in projects]
        self.assertIn(topic_1, topics)
        self.assertIn(topic_2, topics)
        
        # 9. Load first project back
        resp = client.post("/api/game/projects/load", json={"project_id": project_id_1})
        self.assertEqual(resp.status_code, 200)
        state_load = resp.json()
        self.assertEqual(state_load["active_project_id"], project_id_1)
        self.assertEqual(state_load["current_project"]["topic"], topic_1)
        
        # 10. Delete second project
        resp = client.post("/api/game/projects/delete", json={"project_id": project_id_2})
        self.assertEqual(resp.status_code, 200)
        
        # 11. List projects (should only contain project 1 now)
        resp = client.get("/api/game/projects")
        self.assertEqual(resp.status_code, 200)
        projects = resp.json()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["project_id"], project_id_1)
        print("Project lifecycle testing verified successfully.")

    def test_student_recruitment_and_dismissal(self):
        print("Testing Student Recruitment & Dismissal Lifecycle...")
        from fastapi.testclient import TestClient
        from app.main import app, WORKSPACE_DIR
        
        client = TestClient(app)
        
        # 1. Reset everything to start fresh
        client.post("/api/game/reset")
        
        # 2. Recruit David (preset: data_engineer)
        resp = client.post("/api/game/students/create", json={
            "name": "David",
            "role": "Data Engineer",
            "skills": {"research": 0.5, "coding": 0.9, "writing": 0.4},
            "personality": "Strict and detail-oriented.",
            "preset_id": "data_engineer"
        })
        self.assertEqual(resp.status_code, 200)
        state_data = resp.json()
        
        # Verify student is in list
        students = state_data["students"]
        david = next((s for s in students if s["name"] == "David"), None)
        self.assertIsNotNone(david)
        self.assertEqual(david["role"], "Data Engineer")
        self.assertIn("David", david["custom_prompt"])
        self.assertIn("Data Engineer", david["custom_prompt"])
        self.assertIn("Strict and detail-oriented.", david["custom_prompt"])
        
        # Verify private channel and group membership
        channels = state_data["channels"]
        group_channel = next((c for c in channels if c["id"] == "group"), None)
        self.assertIsNotNone(group_channel)
        self.assertIn("David", group_channel["members"])
        
        david_channel = next((c for c in channels if c["id"] == "david"), None)
        self.assertIsNotNone(david_channel)
        self.assertIn("David", david_channel["members"])
        self.assertIn("PI", david_channel["members"])
        
        # Verify workspace directory exists
        david_ws = os.path.join(WORKSPACE_DIR, "David")
        self.assertTrue(os.path.exists(david_ws))
        
        # 3. Recruit Eva (preset: custom)
        resp = client.post("/api/game/students/create", json={
            "name": "Eva",
            "role": "Optimizer Scientist",
            "skills": {"research": 0.8, "coding": 0.7, "writing": 0.6},
            "personality": "Always positive, likes mathematical proofs.",
            "preset_id": "custom"
        })
        self.assertEqual(resp.status_code, 200)
        state_data = resp.json()
        
        students = state_data["students"]
        eva = next((s for s in students if s["name"] == "Eva"), None)
        self.assertIsNotNone(eva)
        self.assertEqual(eva["role"], "Optimizer Scientist")
        self.assertIn("Eva", eva["custom_prompt"])
        self.assertIn("Optimizer Scientist", eva["custom_prompt"])
        self.assertIn("Always positive", eva["custom_prompt"])
        
        # 4. Attempt to recruit duplicate student (David)
        resp_dup = client.post("/api/game/students/create", json={
            "name": "David",
            "role": "Data Engineer",
            "skills": {"research": 0.5, "coding": 0.9, "writing": 0.4},
            "personality": "Attempt to duplicate",
            "preset_id": "data_engineer"
        })
        self.assertEqual(resp_dup.status_code, 400)
        
        # 5. Dismiss David
        resp_dismiss = client.post("/api/game/students/dismiss", json={"name": "David"})
        self.assertEqual(resp_dismiss.status_code, 200)
        state_dismissed = resp_dismiss.json()
        
        # Verify David is gone from students list
        self.assertFalse(any(s["name"] == "David" for s in state_dismissed["students"]))
        
        # Verify David is gone from group channel members
        group_channel = next((c for c in state_dismissed["channels"] if c["id"] == "group"), None)
        self.assertIsNotNone(group_channel)
        self.assertNotIn("David", group_channel["members"])
        
        # Verify David's private channel is deleted
        self.assertFalse(any(c["id"] == "david" for c in state_dismissed["channels"]))
        
        # Verify David's workspace is NOT deleted (data preservation)
        self.assertTrue(os.path.exists(david_ws))
        
        # 6. Attempt to dismiss non-existent student
        resp_fail = client.post("/api/game/students/dismiss", json={"name": "David"})
        self.assertEqual(resp_fail.status_code, 404)
        
        print("Student recruitment & dismissal lifecycle verified successfully.")


if __name__ == "__main__":
    unittest.main()
