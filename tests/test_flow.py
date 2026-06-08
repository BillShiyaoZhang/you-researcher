from fastapi.testclient import TestClient
import os
import shutil
from unittest.mock import MagicMock, patch
from app.main import app

mock_openai_client = MagicMock()
mock_openai_client.chat.completions.create.side_effect = Exception("Mock LLM Call")

@patch("app.agent_manager.OpenAI", return_value=mock_openai_client)
def test_full_gameplay_flow(mock_openai):
    print("Initializing TestClient and cleaning workspace...")
    client = TestClient(app)
    
    # 1. Reset game state
    response = client.post("/api/game/reset")
    assert response.status_code == 200, f"Reset failed: {response.text}"
    response = client.post("/api/game/set_language", json={"language": "en"})
    assert response.status_code == 200
    state = response.json()
    assert state["day"] == 1
    assert state["current_project"] is None
    print("Step 1: Reset Game State and Language set to English verified.")
    
    # 2. Start project
    topic = "Parameter-efficient tuning via Sparse Weight Masking"
    response = client.post("/api/game/init_project", json={"topic": topic})
    assert response.status_code == 200, f"Init project failed: {response.text}"
    state = response.json()
    assert state["current_project"]["topic"] == topic
    assert state["current_project"]["stage"] == "Literature Review"
    print("Step 2: Project Initialization verified.")
    
    # 3. Tick 1: Literature review
    response = client.post("/api/game/tick")
    assert response.status_code == 200, f"Tick 1 failed: {response.text}"
    state = response.json()
    assert state["current_project"]["stage"] == "Proposal"
    assert os.path.exists("./workspace/literature_review.md")
    print("Step 3: Literature review and file creation verified.")
    
    # 4. Tick 2: Proposal Drafting
    response = client.post("/api/game/tick")
    assert response.status_code == 200, f"Tick 2 failed: {response.text}"
    state = response.json()
    assert state["current_project"]["stage"] == "Awaiting Proposal Approval"
    assert len(state["pending_approvals"]) == 1
    assert os.path.exists("./workspace/proposal.md")
    print("Step 4: Proposal drafting and approval request verified.")
    
    # 5. Approve Proposal
    response = client.post("/api/game/approve_proposal", json={"decision": "approve"})
    assert response.status_code == 200, f"Approval failed: {response.text}"
    state = response.json()
    assert state["current_project"]["stage"] == "Experimentation"
    assert len(state["pending_approvals"]) == 0
    print("Step 5: Proposal approval verified.")
    
    # 6. Tick 3: Experiment execution in sandbox
    response = client.post("/api/game/tick")
    assert response.status_code == 200, f"Tick 3 failed: {response.text}"
    state = response.json()
    assert state["current_project"]["stage"] == "Paper Writing"
    assert os.path.exists("./workspace/experiment.py")
    print("Step 6: Code sandbox execution and script copy verified.")
    
    # 7. Tick 4: Paper drafting
    response = client.post("/api/game/tick")
    assert response.status_code == 200, f"Tick 4 failed: {response.text}"
    state = response.json()
    assert state["current_project"]["stage"] == "Awaiting Submission"
    assert os.path.exists("./workspace/paper.md")
    print("Step 7: Paper draft compile verified.")
    
    # 8. Submit Paper to conference
    response = client.post("/api/game/submit_paper", json={"conference": "EMNLP (Specialized)"})
    assert response.status_code == 200, f"Submission failed: {response.text}"
    state = response.json()
    # EMNLP score should be calculated and stage changed to either Paper Writing (if rejected) or Completed (if accepted)
    assert state["current_project"]["stage"] in ["Paper Writing", "Completed (Accepted)"]
    print(f"Step 8: Paper submission and peer review simulation verified. (Final stage: {state['current_project']['stage']})")
    print("\n--- ALL GAMEPLAY FLOW INTEGRATION TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    test_full_gameplay_flow()
