import os
import shutil
import unittest
from app.arxiv_tool import search_arxiv
from app.sandbox import execute_python_code
from app.game_state import GameState, Project, Student
from app.agent_manager import call_llm, run_literature_review, run_proposal_drafting

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
        # Since we use placeholder key, this should return mock template response
        resp = call_llm("You are Alice", "Write a proposal about topic: attention mechanisms")
        self.assertIn("Proposal", resp)
        self.assertIn("Experiment", resp)
        print("LLM Mock Response verified successfully.")

    def test_game_state_flow(self):
        print("Testing Game State transitions...")
        state = GameState()
        # Initialize some students
        state.students = [
            Student(name="Alice", role="Deep Learning Hacker", skills={"research": 0.6, "coding": 0.9, "writing": 0.5}),
            Student(name="Bob", role="Theoretical Researcher", skills={"research": 0.9, "coding": 0.4, "writing": 0.9})
        ]
        
        # Check initial budget
        self.assertEqual(state.funding, 10000.0)
        self.assertEqual(state.day, 1)
        
        # Launch project
        state.current_project = Project(topic="Low-bit quantization")
        self.assertEqual(state.current_project.stage, "Literature Review")
        
        # Test log addition
        state.add_log("Test project initiated.")
        self.assertEqual(len(state.system_logs), 1)
        self.assertIn("Day 1: Test project initiated.", state.system_logs[0])
        print("Game State transitions verified successfully.")

if __name__ == "__main__":
    unittest.main()
