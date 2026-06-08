import os
import time
import random
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Any, List, Optional
from app.game_state import GameState, Student, Project
from app.arxiv_tool import search_arxiv
from app.sandbox import execute_python_code

load_dotenv()

# Read settings from environment
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

def get_llm_client() -> Optional[OpenAI]:
    if not API_KEY or API_KEY.strip() == "" or API_KEY == "your_api_key_here":
        return None
    try:
        return OpenAI(api_key=API_KEY, base_url=API_BASE)
    except Exception as e:
        print(f"Error creating OpenAI client: {e}")
        return None

def call_llm(system_prompt: str, user_prompt: str) -> str:
    client = get_llm_client()
    if client is None:
        return get_mock_llm_response(system_prompt, user_prompt)
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM API call failed: {e}. Falling back to mock generator.")
        return get_mock_llm_response(system_prompt, user_prompt, error_msg=str(e))

def get_mock_llm_response(system_prompt: str, user_prompt: str, error_msg: str = "") -> str:
    """
    Generates realistic responses based on keywords in prompts to support out-of-the-box operations.
    """
    # Simple rule-based mock responses that mimic academic agent thoughts and documents
    user_prompt_lower = user_prompt.lower()
    
    if "arxiv search" in user_prompt_lower or "literature review" in user_prompt_lower:
        topic = user_prompt.split("topic:")[-1].strip() if "topic:" in user_prompt else "Deep Learning"
        return f"""### Literature Review Synthesis: {topic}

We conducted an extensive search on ArXiv regarding the topic: **{topic}**. 
Key findings from literature:
1. Modern methods struggle with computational efficiency and parameter scaling.
2. Self-attention mechanisms can be optimized by sparsification and low-rank approximation.
3. Benchmarks demonstrate that adaptive step-sizes improve convergence rates by 15-20%.

**Proposed Research Direction:**
We will investigate a novel adaptive learning rate schedule that scales weights dynamically based on gradient variance. This addresses the training instability identified in recent papers.

*Note: Running in simulation mode because no LLM API key is configured.*"""

    elif "proposal" in user_prompt_lower or "draft a proposal" in user_prompt_lower:
        topic = user_prompt.split("topic:")[-1].strip() if "topic:" in user_prompt else "AI optimization"
        return f"""# Research Proposal: Adaptive Variance Optimization (AVO)

**Research Objective:**
Develop a lightweight optimizer extension that scales training steps dynamically based on batch gradient variance, reducing transformer pre-training steps.

**Proposed Python Experiment Code:**
```python
import time
import random

def run_experiment():
    print("Initializing experiment: AVO vs AdamW benchmark...")
    # Simulate a training loop
    loss_adamw = 5.0
    loss_avo = 5.0
    
    print("Epoch | AdamW Loss | AVO Loss")
    print("----------------------------")
    for epoch in range(1, 6):
        time.sleep(0.5)
        loss_adamw -= random.uniform(0.5, 0.9)
        loss_avo -= random.uniform(0.7, 1.2) # AVO performs slightly better
        print(f"  {{epoch}}   |   {{loss_adamw:.4f}}   |   {{loss_avo:.4f}}")
    
    print("Experiment completed successfully.")
    print("Final Results: AVO achieved 12% lower final training loss than AdamW.")
    return True

run_experiment()
```

**Evaluation Metric:**
We will evaluate convergence speed (epochs to reach loss < 1.0) and final training loss.
"""

    elif "compile a paper" in user_prompt_lower or "paper draft" in user_prompt_lower:
        return """# Adaptive Variance Optimization for Stable Transformer Training

**Abstract:**
We introduce Adaptive Variance Optimization (AVO), a novel optimization strategy designed to stabilize transformer training. Traditional optimizers like AdamW suffer from instability under high gradient variance. AVO dynamically scales learning rates based on mini-batch variance metrics. Our empirical evaluations demonstrate that AVO achieves comparable or superior loss convergence while reducing training epochs by 12% on standard benchmarks.

## 1. Introduction
Transformers have revolutionized deep learning but remain computationally expensive and sensitive to optimization parameters...

## 2. Methodology
We formulate AVO as follows:
$$ \\theta_{t+1} = \\theta_t - \\frac{\\eta}{\\sqrt{V(\\nabla L(\\theta_t)) + \\epsilon}} \\cdot m_t $$

## 3. Experimental Results
Our sandbox runs show the following training convergence path:
- **Baseline AdamW**: Final Loss: 1.4502 (5 Epochs)
- **AVO (Ours)**: Final Loss: 1.1028 (5 Epochs)

## 4. Conclusion
AVO offers a simple, drop-in replacement for AdamW in transformer training, demonstrating improved stability.
"""

    elif "group meeting" in user_prompt_lower or "discuss" in user_prompt_lower:
        name = "Student"
        for student_name in ["Alice", "Bob", "Charlie"]:
            if student_name in system_prompt:
                name = student_name
                break
        
        responses = {
            "Alice": [
                "I finished running the baseline tests, Professor! The code compiled fine but we need to optimize the memory footprint.",
                "Let's write a python benchmark to test the convergence speed directly. I can set it up in the sandbox right now.",
                "I think we should focus on writing a custom training loop to test this optimizer."
            ],
            "Bob": [
                "According to the latest ArXiv papers, high gradient variance is a known bottleneck. I think our proposal is theoretically sound.",
                "I can write up the methodology section of the draft. Let's make sure the mathematical formulations are fully rigorous.",
                "Perhaps we should do a deeper literature search to see if any similar optimizer has been proposed for transformers."
            ],
            "Charlie": [
                "This sounds super cool! I'm happy to help Alice write the training code or help Bob search more papers.",
                "Professor, should we prioritize the training speed or focus on final model accuracy first?",
                "I will update the workspace files and make sure our logs are well organized."
            ]
        }
        return random.choice(responses.get(name, ["Interesting point, let's explore it further."]))

    return f"Default Agent Response for prompt: {user_prompt[:50]}..."

# Student prompts templates
SYSTEM_PROMPTS = {
    "Alice": """You are Alice, a PhD student in the lab. You are a "Deep Learning Hacker" with exceptional coding skills (9/10), good research ideas (6/10), but average writing (5/10).
Personality: Direct, energetic, prefers writing code and running experiments over reading papers. Speaks colloquially, uses developer terms (e.g. "it compiles!", "bug fixed", "let's script this").
You will help the Professor run experiments and write code scripts.""",

    "Bob": """You are Bob, a PhD student in the lab. You are a "Theoretical Researcher" with superb literature synthesis and writing skills (9/10), but weak coding skills (4/10).
Personality: Meticulous, academic, precise, formal, sometimes a bit slow. Prefers reading papers and structuring theoretical proofs. Speaks formally and structures ideas logically.
You will help the Professor with literature search, reading papers, and drafting papers.""",

    "Charlie": """You are Charlie, an enthusiastic master's student doing an internship in the lab. You have average skills (research: 5/10, coding: 6/10, writing: 6/10).
Personality: Very eager to learn, asks lots of questions, highly motivated, but sometimes makes rookie mistakes. Speaks politely and calls you 'Professor' in every sentence.
You will assist on any task.""",
}

def run_literature_review(student: Student, project: Project) -> str:
    """
    Executes ArXiv search using the real tool and synthesizes a literature review.
    """
    student.status = "Searching ArXiv"
    student.activity = f"Searching ArXiv papers about: '{project.topic}'"
    
    # Step 1: Query ArXiv
    papers = search_arxiv(project.topic, max_results=4)
    papers_text = ""
    for idx, p in enumerate(papers):
        if "error" in p:
            papers_text += f"\nError fetching paper: {p['error']}\n"
        elif "info" in p:
            papers_text += f"\nInfo: {p['info']}\n"
        else:
            papers_text += f"\nPaper {idx+1}: {p['title']}\nAbstract: {p['summary']}\nURL: {p['url']}\n"
            
    # Step 2: Query LLM to synthesize literature review
    sys_prompt = SYSTEM_PROMPTS[student.name] + "\nSynthesize the literature and write a review."
    user_prompt = f"""We are starting a new research project on the topic: '{project.topic}'.
I found the following papers on ArXiv:
{papers_text}

Write a structured literature review in markdown (3-4 paragraphs). Identify key trends, open issues, and outline a proposed next direction for our lab."""
    
    student.thoughts.append(f"Searching ArXiv for '{project.topic}'. Found {len(papers)} papers. Now synthesizing...")
    review = call_llm(sys_prompt, user_prompt)
    student.thoughts.append("Finished literature review draft.")
    student.status = "Idle"
    student.activity = "Finished literature review synthesis."
    return review

def run_proposal_drafting(student: Student, project: Project) -> str:
    """
    Drafts a formal research proposal with an implementation script code block.
    """
    student.status = "Writing Proposal"
    student.activity = f"Drafting research proposal and code script for: '{project.topic}'"
    
    sys_prompt = SYSTEM_PROMPTS[student.name] + "\nWrite a research proposal with a runnable Python script."
    user_prompt = f"""Topic: {project.topic}
Literature review synthesis:
{project.proposal_draft or ""}

Draft a formal Research Proposal in Markdown. It must include:
1. Research Objectives.
2. Methodology.
3. A complete, runnable Python code block that simulates the experiment or runs a lightweight benchmark comparing our method with a baseline. The script MUST run successfully, print epoch losses, and output results. Do not include heavy external library dependencies like torch or tensorflow unless you write mockup versions, to ensure it executes in our simple python sandbox. Write standard library code or lightweight math.
Format the code block as:
```python
# code here
```
"""
    student.thoughts.append("Drafting proposal. Designing the experiment script...")
    proposal = call_llm(sys_prompt, user_prompt)
    student.thoughts.append("Finished proposal draft with code. Awaiting PI review.")
    student.status = "Awaiting PI Approval"
    student.activity = "Awaiting Professor's review of the proposal."
    return proposal

def run_experimentation(student: Student, project: Project, workspace_dir: str) -> Dict[str, Any]:
    """
    Extracts the python script from the proposal, runs it in the sandbox,
    and returns logs. If it fails, attempts self-debugging up to 2 times.
    """
    student.status = "Experimenting"
    student.activity = "Extracting experiment script and executing in sandbox."
    student.thoughts.append("Extracting experiment script from proposal...")
    
    # Extract python code block
    proposal_text = project.proposal_draft or ""
    code_block = ""
    if "```python" in proposal_text:
        parts = proposal_text.split("```python")
        if len(parts) > 1:
            code_block = parts[1].split("```")[0]
            
    if not code_block.strip():
        # Fallback code
        code_block = """
import time
import random
print("Running default experiment...")
for i in range(1, 4):
    time.sleep(0.5)
    print(f"Epoch {i}: Loss = {5.0 - i * 1.2:.4f}")
print("Completed successfully!")
"""
        student.thoughts.append("No python code block found in proposal. Using fallback test code.")

    # Execute code in sandbox
    retries = 2
    sandbox_result = {}
    for attempt in range(1, retries + 2):
        student.activity = f"Running sandbox experiment (Attempt {attempt})..."
        student.thoughts.append(f"Running code sandbox (Attempt {attempt})...")
        
        sandbox_result = execute_python_code(code_block, workspace_dir)
        exit_code = sandbox_result.get("exit_code", -1)
        stdout = sandbox_result.get("stdout", "")
        stderr = sandbox_result.get("stderr", "")
        
        if exit_code == 0:
            student.thoughts.append(f"Experiment completed successfully (Exit Code 0).\nStdout:\n{stdout[:150]}...")
            break
        else:
            student.thoughts.append(f"Experiment failed (Exit Code {exit_code}).\nStderr: {stderr}\nAttempting to debug...")
            # Query LLM to debug the code
            sys_prompt = SYSTEM_PROMPTS[student.name] + "\nYou are debugging a failed experiment script."
            debug_prompt = f"""The following python script failed to execute:
```python
{code_block}
```
Exit code: {exit_code}
Stderr: {stderr}
Stdout: {stdout}

Rewrite the script to fix the bugs. Make sure it is fully runnable in a basic python sandbox. Output ONLY the updated python script code block."""
            debugged_code = call_llm(sys_prompt, debug_prompt)
            if "```python" in debugged_code:
                code_block = debugged_code.split("```python")[1].split("```")[0]
            else:
                code_block = debugged_code
                
    student.status = "Idle"
    student.activity = "Experiment finished."
    
    # Summarize results
    sys_prompt = SYSTEM_PROMPTS[student.name] + "\nSummarize the experiment output."
    summary_prompt = f"""Write a summary of the experiment results for our paper draft.
Stdout: {sandbox_result.get('stdout')}
Stderr: {sandbox_result.get('stderr')}
Exit Code: {sandbox_result.get('exit_code')}"""
    
    results_summary = call_llm(sys_prompt, summary_prompt)
    project.experiment_results = f"### Sandbox Output:\n```\n{sandbox_result.get('stdout')}\n```\n\n### Synthesis:\n{results_summary}"
    
    return sandbox_result

def run_paper_drafting(student: Student, project: Project) -> str:
    """
    Drafts the final academic paper.
    """
    student.status = "Writing Draft"
    student.activity = "Writing academic paper draft..."
    student.thoughts.append("Synthesizing proposal, experiments, and literature into a full paper draft...")
    
    sys_prompt = SYSTEM_PROMPTS[student.name] + "\nWrite a formal academic paper draft in markdown."
    user_prompt = f"""We are finalizing our project: '{project.topic}'.
Here are the project inputs:
- Proposal and Objectives: {project.proposal_draft[:1000]}...
- Experiment Results: {project.experiment_results}

Write a complete academic research paper in markdown. It should contain Title, Abstract, Introduction, Methodology, Experiments, and Conclusion sections. Format the mathematical formulas and keep it highly professional."""

    paper = call_llm(sys_prompt, user_prompt)
    student.thoughts.append("Paper draft completed! Ready for conference submission.")
    student.status = "Idle"
    student.activity = "Paper writing completed."
    return paper

def run_group_discussion(students: List[Student], history: List[Dict[str, str]], user_msg: str) -> List[Dict[str, str]]:
    """
    Simulates a group discussion where student agents discuss in response to the user.
    """
    new_replies = []
    # Let each student reply in character
    for student in students:
        # Check energy levels
        if student.energy < 15:
            continue
            
        sys_prompt = SYSTEM_PROMPTS[student.name] + f"\nParticipate in the lab group meeting. You are talking to the Professor and your peers. Keep your response short (1-2 sentences) and highly in-character. Your current project is: {student.status}"
        
        chat_context = ""
        for h in history[-6:]:
            chat_context += f"{h['sender']}: {h['message']}\n"
        chat_context += f"Professor: {user_msg}\n"
        
        prompt = f"""Here is the group meeting history:
{chat_context}
Provide your next response in the meeting."""
        
        reply = call_llm(sys_prompt, prompt)
        student.energy = max(0, student.energy - 5)
        new_replies.append({
            "sender": student.name,
            "role": student.role,
            "message": reply
        })
    return new_replies
