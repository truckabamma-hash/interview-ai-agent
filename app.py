import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

# Load your secret API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================
# STEP 1: PUT YOUR RESUME BIO HERE (BE SPECIFIC WITH NUMBERS!)
# ============================================================
MY_RESUME_BIO = """
Computer Science graduate with 2 years of internship experience.
- Led a team of 3 to build a React Native mobile app for a local coffee shop, increasing their loyalty sign-ups by 40%.
- Resolved a major database deadlock issue in a PostgreSQL database that was slowing down queries by 15 seconds.
- Created a Python automation script that reduced manual data entry time by 10 hours per week.
- Strong skills in: Python, React, PostgreSQL, AWS (S3 & EC2), and Agile methodologies.
"""

# ============================================================
# THE MAIN AGENT FUNCTION
# ============================================================
def interview_agent(job_description):
    
    # ---------- AGENT 1: The "Question Extractor" ----------
    question_prompt = f"""
    You are an expert hiring manager. Read this job description:
    ---
    {job_description}
    ---
    
    Based on this job description, list the 5 most likely interview questions they will ask.
    Return the questions as a numbered list (1 to 5). Only return the questions, no extra text.
    """
    
    questions_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question_prompt}],
        temperature=0.5
    )
    
    raw_questions = questions_response.choices[0].message.content
    
    # ---------- AGENT 2: The "STAR Answer Writer" ----------
    star_prompt = f"""
    You are a career coach. I have a job interview coming up.
    
    Here is my resume/bio:
    ---
    {MY_RESUME_BIO}
    ---
    
    Here are the questions the interviewer will ask:
    ---
    {raw_questions}
    ---
    
    For each question, write a perfect interview answer using the STAR method:
    - **S**ituation: Set the context
    - **T**ask: What needed to be done?
    - **A**ction: What specifically did YOU do?
    - **R**esult: What was the measurable outcome?
    
    Format clearly with each question and STAR section.
    """
    
    star_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": star_prompt}],
        temperature=0.7
    )
    
    final_output = star_response.choices[0].message.content
    return raw_questions, final_output

# ============================================================
# BUILD THE WEB INTERFACE
# ============================================================
def generate_interview_prep(job_text):
    if not job_text or len(job_text) < 20:
        return "Please paste a valid job description.", "Error: Need more text."
    
    try:
        questions, answers = interview_agent(job_text)
        return questions, answers
    except Exception as e:
        return f"Error: {str(e)}", "Check your API key or internet connection."

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎤 AI Interview Simulator
    **Paste a Job Description below** and my AI agents will:
    1. Predict the 5 questions you'll be asked
    2. Write personalized STAR-method answers using YOUR resume
    """)
    
    with gr.Row():
        with gr.Column():
            job_input = gr.Textbox(
                label="📋 Paste Job Description Here", 
                placeholder="Copy and paste the entire job description...",
                lines=10
            )
            submit_btn = gr.Button("🚀 Generate My Interview Prep", variant="primary")
        
        with gr.Column():
            questions_output = gr.Textbox(
                label="❓ Predicted Interview Questions", 
                lines=8
            )
            answers_output = gr.Textbox(
                label="✅ Your STAR-Format Answers", 
                lines=20
            )
    
    submit_btn.click(
        fn=generate_interview_prep, 
        inputs=job_input, 
        outputs=[questions_output, answers_output]
    )

if __name__ == "__main__":
    demo.launch(share=False)
