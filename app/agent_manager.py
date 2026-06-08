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

def call_llm(system_prompt: str, user_prompt: str, language: str = "cn") -> str:
    client = get_llm_client()
    if client is None:
        return get_mock_llm_response(system_prompt, user_prompt, language=language)
    
    # Append language instructions to the system prompt
    if language == "cn":
        system_prompt += "\n重要指示：请使用中文回答本对话，并用中文撰写所有科研报告、论文草稿、开题报告和言论。"
    else:
        system_prompt += "\nImportant instruction: Please respond in English, and draft all research proposals, paper drafts, and meeting comments in English."

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
        return get_mock_llm_response(system_prompt, user_prompt, error_msg=str(e), language=language)

def get_mock_llm_response(system_prompt: str, user_prompt: str, error_msg: str = "", language: str = "cn") -> str:
    """
    Generates realistic responses based on keywords in prompts to support out-of-the-box operations.
    """
    user_prompt_lower = user_prompt.lower()
    is_chinese = (language == "cn")
    
    if "arxiv search" in user_prompt_lower or "literature review" in user_prompt_lower:
        topic = user_prompt.split("topic:")[-1].strip() if "topic:" in user_prompt else "Deep Learning"
        if is_chinese:
            return f"""### 文献综述合成：{topic}

针对主题 **{topic}** 我们进行了广泛的 ArXiv 检索。
文献中的关键发现：
1. 传统方法在计算效率和参数规模上存在瓶颈。
2. 自注意力机制可以通过稀疏化和低秩近似来优化。
3. 基准测试表明，自适应步长能够使收敛速度提升 15-20%。

**拟定的研究方向：**
我们将研究一种新型的自适应学习率策略，根据梯度方差动态缩放权重，以解决近期文献中指出的训练不稳定问题。

*注：由于未配置 LLM API 密钥，当前运行在模拟模式。*"""
        else:
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
        if is_chinese:
            return f"""# 课题开题报告：自适应方差优化 (AVO)

**研究目标：**
开发一种轻量级的优化器扩展，根据小批量梯度方差动态缩放训练步长，以减少 Transformer 的预训练步数。

**拟议的 Python 实验代码：**
```python
import time
import random

def run_experiment():
    print("初始化实验：AVO 与 AdamW 基准对比测试...")
    # 模拟训练循环
    loss_adamw = 5.0
    loss_avo = 5.0
    
    print("Epoch | AdamW 损失值 | AVO 损失值")
    print("-------------------------------")
    for epoch in range(1, 6):
        time.sleep(0.5)
        loss_adamw -= random.uniform(0.5, 0.9)
        loss_avo -= random.uniform(0.7, 1.2) # AVO 表现稍好
        print(f"  {{epoch}}   |   {{loss_adamw:.4f}}   |   {{loss_avo:.4f}}")
    
    print("实验圆满完成。")
    print("最终结果：AVO 的最终训练损失值比 AdamW 降低了 12%。")
    return True

run_experiment()
```

**评估指标：**
我们将评估收敛速度（损失值达到 1.0 以下所需的 Epoch 数量）和最终的训练损失。
"""
        else:
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
        if is_chinese:
            return """# 用于稳定 Transformer 训练的的自适应方差优化算法

**摘要：**
我们提出了一种新型的优化策略——自适应方差优化 (AVO)，旨在稳定 Transformer 的训练过程。传统的 AdamW 优化器在高梯度方差下容易出现训练不稳定的问题。AVO 根据小批量梯度方差指标动态缩放学习率。我们的实证评估表明，AVO 在标准基准测试中将训练 Epoch 减少了 12%，同时实现了相当或更优的损失收敛。

## 1. 引言
Transformer 彻底改变了深度学习，但在优化参数上依然计算昂贵且非常敏感...

## 2. 方法论
We formulate AVO as follows:
$$ \\theta_{t+1} = \\theta_t - \\frac{\\eta}{\\sqrt{V(\\nabla L(\\theta_t)) + \\epsilon}} \\cdot m_t $$

## 3. 实验结果
我们的沙箱运行展示了以下训练收敛曲线：
- **基线 AdamW**: 最终损失: 1.4502 (5 Epochs)
- **AVO (本方法)**: 最终损失: 1.1028 (5 Epochs)

## 4. 结论
AVO 提供了一个简单、即插即用的 AdamW 替代方案，有效提升了 Transformer 训练的稳定性。
"""
        else:
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
        
        responses_cn = {
            "Alice": [
                "我已经跑完了基线测试，教授！代码编译没问题，但我们得优化一下内存占用。",
                "我们写个 Python 基准脚本来直接测试收敛速度吧，我现在就可以在沙箱里写好。",
                "我觉得我们应该专注于写一个自定义的训练循环来测试这个优化器。"
            ],
            "Bob": [
                "根据最新的 ArXiv 论文，高梯度方差是一个已知的瓶颈，我们的方案在理论上是完全行得通的。",
                "我可以撰写论文的 Methodology 章节。我们必须确保数学公式的绝对严谨。",
                "也许我们应该做更深入的文献检索，看看之前有没有针对 Transformer 提出类似的优化器。"
            ],
            "Charlie": [
                "这听起来太酷了！我很乐意帮 Alice 写训练代码，或者帮 Bob 搜搜更多论文。",
                "教授，我们应该优先考虑训练速度，还是先把精力放在最终模型的准确率上？",
                "我会去更新工作区的文件，确保我们的日志都井井有条。"
            ]
        }
        
        responses_en = {
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
        
        resp_list = responses_cn.get(name, []) if is_chinese else responses_en.get(name, [])
        return random.choice(resp_list) if resp_list else ("想法很好，我们可以继续推进。" if is_chinese else "Interesting point, let's explore it further.")

    return ("默认智能体响应..." if is_chinese else f"Default Agent Response for prompt: {user_prompt[:50]}...")

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

def run_literature_review(student: Student, project: Project, language: str = "cn") -> str:
    """
    Executes ArXiv search using the real tool and synthesizes a literature review.
    """
    is_chinese = (language == "cn")
    student.status = "文献检索" if is_chinese else "Searching ArXiv"
    student.activity = f"正在检索关于 '{project.topic}' 的 ArXiv 论文" if is_chinese else f"Searching ArXiv papers about: '{project.topic}'"
    
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
    sys_prompt = SYSTEM_PROMPTS[student.name] + ("\n请撰写一篇文献综述。" if is_chinese else "\nSynthesize the literature and write a review.")
    
    if is_chinese:
        user_prompt = f"""我们正在针对课题“{project.topic}”展开一项新研究。
我在 ArXiv 上找到了以下几篇论文：
{papers_text}

请用中文撰写一篇结构化的文献综述（3-4个段落），包括目前技术趋势、瓶颈，以及为我们实验室指明一个接下来可行的研究切入点。"""
    else:
        user_prompt = f"""We are starting a new research project on the topic: '{project.topic}'.
I found the following papers on ArXiv:
{papers_text}

Write a structured literature review in markdown (3-4 paragraphs). Identify key trends, open issues, and outline a proposed next direction for our lab."""
    
    student.thoughts.append(
        f"正在检索关于 '{project.topic}' 的文献。找到 {len(papers)} 篇论文。开始合成中..." 
        if is_chinese else 
        f"Searching ArXiv for '{project.topic}'. Found {len(papers)} papers. Now synthesizing..."
    )
    
    review = call_llm(sys_prompt, user_prompt, language=language)
    student.thoughts.append("文献综述草稿已完成。" if is_chinese else "Finished literature review draft.")
    student.status = "空闲" if is_chinese else "Idle"
    student.activity = "已完成文献综述合成。" if is_chinese else "Finished literature review synthesis."
    return review

def run_proposal_drafting(student: Student, project: Project, language: str = "cn") -> str:
    """
    Drafts a formal research proposal with an implementation script code block.
    """
    is_chinese = (language == "cn")
    student.status = "撰写开题报告" if is_chinese else "Writing Proposal"
    student.activity = f"正在为项目 '{project.topic}' 撰写开题报告和代码草稿" if is_chinese else f"Drafting research proposal and code script for: '{project.topic}'"
    
    sys_prompt = SYSTEM_PROMPTS[student.name] + ("\n请写一份开题报告并附带可运行的 Python 代码。" if is_chinese else "\nWrite a research proposal with a runnable Python script.")
    
    if is_chinese:
        user_prompt = f"""课题: {project.topic}
文献综述内容:
{project.proposal_draft or ""}

请用中文撰写一份正式的开题报告（Markdown 格式），必须包括：
1. 研究目标 (Objectives)
2. 实验方法 (Methodology)
3. 一个完整的、可运行的 Python 实验验证代码块（用以模拟或运行简单的基准指标）。脚本必须能直接在没有 torch/tensorflow 的基础 python 沙箱环境中运行，打印 epoch 和 loss 指标，且最后要有结果输出。
格式如下：
```python
# 代码写在这里
```
"""
    else:
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
    
    student.thoughts.append("正在撰写开题报告，正在设计实验验证代码..." if is_chinese else "Drafting proposal. Designing the experiment script...")
    proposal = call_llm(sys_prompt, user_prompt, language=language)
    student.thoughts.append("开题报告撰写完成。已提交给教授评审。" if is_chinese else "Finished proposal draft with code. Awaiting PI review.")
    student.status = "等待教授审批" if is_chinese else "Awaiting PI Approval"
    student.activity = "等待教授审核开题报告。" if is_chinese else "Awaiting Professor's review of the proposal."
    return proposal

def run_experimentation(student: Student, project: Project, workspace_dir: str, language: str = "cn") -> Dict[str, Any]:
    """
    Extracts the python script from the proposal, runs it in the sandbox,
    and returns logs. If it fails, attempts self-debugging up to 2 times.
    """
    is_chinese = (language == "cn")
    student.status = "实验中" if is_chinese else "Experimenting"
    student.activity = "提取实验代码并在沙箱中执行..." if is_chinese else "Extracting experiment script and executing in sandbox."
    student.thoughts.append("正在从开题报告中提取 Python 代码段..." if is_chinese else "Extracting experiment script from proposal...")
    
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
        student.thoughts.append("开题报告中未找到 python 代码段。使用默认测试代码。" if is_chinese else "No python code block found in proposal. Using fallback test code.")

    # Execute code in sandbox
    retries = 2
    sandbox_result = {}
    for attempt in range(1, retries + 2):
        student.activity = f"运行沙箱实验（第 {attempt} 次尝试）..." if is_chinese else f"Running sandbox experiment (Attempt {attempt})..."
        student.thoughts.append(f"正在启动沙箱子进程（第 {attempt} 次尝试）..." if is_chinese else f"Running code sandbox (Attempt {attempt})...")
        
        sandbox_result = execute_python_code(code_block, workspace_dir)
        exit_code = sandbox_result.get("exit_code", -1)
        stdout = sandbox_result.get("stdout", "")
        stderr = sandbox_result.get("stderr", "")
        
        if exit_code == 0:
            student.thoughts.append(
                f"沙箱实验执行圆满成功（退出码 0）。\n标准输出：\n{stdout[:150]}..." 
                if is_chinese else 
                f"Experiment completed successfully (Exit Code 0).\nStdout:\n{stdout[:150]}..."
            )
            break
        else:
            student.thoughts.append(
                f"沙箱运行失败（退出码 {exit_code}）。\n标准错误：{stderr}\n正在尝试自我 Debug..." 
                if is_chinese else 
                f"Experiment failed (Exit Code {exit_code}).\nStderr: {stderr}\nAttempting to debug..."
            )
            # Query LLM to debug the code
            sys_prompt = SYSTEM_PROMPTS[student.name] + ("\n你正在调试一个运行失败的实验脚本。" if is_chinese else "\nYou are debugging a failed experiment script.")
            
            if is_chinese:
                debug_prompt = f"""以下 python 代码在沙箱中运行出错：
```python
{code_block}
```
退出码: {exit_code}
标准错误: {stderr}
标准输出: {stdout}

请修复这些代码错误。确保可以直接在基础 Python 环境中独立运行。仅输出修复后的 python 代码块（包含在 ```python 中）。"""
            else:
                debug_prompt = f"""The following python script failed to execute:
```python
{code_block}
```
Exit code: {exit_code}
Stderr: {stderr}
Stdout: {stdout}

Rewrite the script to fix the bugs. Make sure it is fully runnable in a basic python sandbox. Output ONLY the updated python script code block."""
                
            debugged_code = call_llm(sys_prompt, debug_prompt, language=language)
            if "```python" in debugged_code:
                code_block = debugged_code.split("```python")[1].split("```")[0]
            else:
                code_block = debugged_code
                
    student.status = "空闲" if is_chinese else "Idle"
    student.activity = "实验结束。" if is_chinese else "Experiment finished."
    
    # Summarize results
    sys_prompt = SYSTEM_PROMPTS[student.name] + ("\n请总结实验输出。" if is_chinese else "\nSummarize the experiment output.")
    
    if is_chinese:
        summary_prompt = f"""请总结以下实验运行结果，以便我们撰写论文：
标准输出: {sandbox_result.get('stdout')}
标准错误: {sandbox_result.get('stderr')}
退出码: {sandbox_result.get('exit_code')}"""
    else:
        summary_prompt = f"""Write a summary of the experiment results for our paper draft.
Stdout: {sandbox_result.get('stdout')}
Stderr: {sandbox_result.get('stderr')}
Exit Code: {sandbox_result.get('exit_code')}"""
    
    results_summary = call_llm(sys_prompt, summary_prompt, language=language)
    
    if is_chinese:
        project.experiment_results = f"### 沙箱运行日志：\n```\n{sandbox_result.get('stdout')}\n```\n\n### 实验总结：\n{results_summary}"
    else:
        project.experiment_results = f"### Sandbox Output:\n```\n{sandbox_result.get('stdout')}\n```\n\n### Synthesis:\n{results_summary}"
    
    return sandbox_result

def run_paper_drafting(student: Student, project: Project, language: str = "cn") -> str:
    """
    Drafts the final academic paper.
    """
    is_chinese = (language == "cn")
    student.status = "撰写论文" if is_chinese else "Writing Draft"
    student.activity = "正在组装并撰写学术论文草稿..." if is_chinese else "Writing academic paper draft..."
    student.thoughts.append("正在整合开题报告、实验结果和相关文献，编译学术论文手稿..." if is_chinese else "Synthesizing proposal, experiments, and literature into a full paper draft...")
    
    sys_prompt = SYSTEM_PROMPTS[student.name] + ("\n请撰写一篇正式的学术论文。" if is_chinese else "\nWrite a formal academic paper draft in markdown.")
    
    if is_chinese:
        user_prompt = f"""我们正在完成课题“{project.topic}”的学术研究。
以下是所有相关材料：
- 研究目标和方法: {project.proposal_draft[:1000]}...
- 实验验证结果: {project.experiment_results}

请撰写一篇完整的中文学术论文手稿（Markdown 格式）。必须包含 Title, Abstract, Introduction, Methodology, Experiments, 和 Conclusion。保持专业的科研文风，并提供严谨的公式。"""
    else:
        user_prompt = f"""We are finalizing our project: '{project.topic}'.
Here are the project inputs:
- Proposal and Objectives: {project.proposal_draft[:1000]}...
- Experiment Results: {project.experiment_results}

Write a complete academic research paper in markdown. It should contain Title, Abstract, Introduction, Methodology, Experiments, and Conclusion sections. Format the mathematical formulas and keep it highly professional."""

    paper = call_llm(sys_prompt, user_prompt, language=language)
    student.thoughts.append("论文初稿撰写完毕！可以准备向学术会议投稿了。" if is_chinese else "Paper draft completed! Ready for conference submission.")
    student.status = "空闲" if is_chinese else "Idle"
    student.activity = "完成论文撰写。" if is_chinese else "Paper writing completed."
    return paper

def run_group_discussion(students: List[Student], history: List[Dict[str, str]], user_msg: str, language: str = "cn") -> List[Dict[str, str]]:
    """
    Simulates a group discussion where student agents discuss in response to the user.
    """
    new_replies = []
    is_chinese = (language == "cn")
    for student in students:
        if student.energy < 15:
            continue
            
        sys_prompt = SYSTEM_PROMPTS[student.name] + f"\nParticipate in the lab group meeting. You are talking to the Professor and your peers. Keep your response short (1-2 sentences) and highly in-character. Your current project status is: {student.status}."
        
        chat_context = ""
        for h in history[-6:]:
            chat_context += f"{h['sender']}: {h['message']}\n"
        chat_context += f"Professor: {user_msg}\n"
        
        if is_chinese:
            prompt = f"""以下是最近的组会交谈内容：
{chat_context}
请继续发表你的看法（用中文，保持你的角色性格特征，控制在1-2句话内）。"""
        else:
            prompt = f"""Here is the group meeting history:
{chat_context}
Provide your next response in the meeting (in English, keeping to your student profile, 1-2 sentences)."""
        
        reply = call_llm(sys_prompt, prompt, language=language)
        student.energy = max(0, student.energy - 5)
        new_replies.append({
            "sender": student.name,
            "role": student.role,
            "message": reply
        })
    return new_replies
