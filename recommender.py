import os
from dotenv import load_dotenv
from groq import Groq
from nlp_clean import extract_skills

# This securely loads the secrets from your .env file!
load_dotenv() 

#  Identify missing skills
def get_missing_skills(resume_skills, job_description):
    job_skills = extract_skills(job_description)
    missing_skills = [skill for skill in job_skills if skill not in resume_skills]
    return missing_skills

# GROQ AI 
def generate_advanced_roadmap(missing_skills, job_title):
    if len(missing_skills) == 0:
        print("🌟 You have every skill required for this job! Apply now!")
        return
        
    print(f"\n🚀 ASKING GROQ AI FOR A CUSTOM {job_title.upper()} ROADMAP 🚀\n")
    
    # 1. Initialize the Groq Client
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # 2. Write the Prompt
    skills_list_string = ", ".join(missing_skills)
    prompt = f"""
    I am applying for a {job_title} role, but I am missing the following technical skills: {skills_list_string}.
    Please act as an expert Career Coach and provide a concise, structured plan to learn these skills.
    
    Crucially, I also want you to analyze this role and suggest 3 crucial SOFT SKILLS I need to develop.
    
    Please Include:
    1. A ranked list of my missing technical skills.
    2. Three critical Soft Skills required for this role and how to demonstrate them.
    3. One learning resource (like a Coursera or YouTube course) for the technical skills.
    4. One portfolio project idea to practice.
    5. A quick 30-day learning roadmap.
    
    Keep the formatting clean, use markdown headers, bullet points, and use emojis!
    """
    
    # 3. Call the Groq API
    print("Calling Groq servers... (This will be lightning fast!)\n")
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
            messages=[
            {"role": "system", "content": "You are an expert career coach."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1024
    )
    
    # 4. RETURN the AI's response to the web server!
    return completion.choices[0].message.content


def recommend_best_roles(resume_skills):
    # Just in case the resume is totally empty
    if len(resume_skills) == 0:
        return "We couldn't find any skills in your resume! Try adding more technical keywords."
        
    print("\n🚀 ASKING GROQ AI FOR BEST CAREER PATHS 🚀\n")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    skills_string = ", ".join(resume_skills)
    
    prompt = f"""
    I am looking for a new job. My resume contains the following skills: {skills_string}.
    Please act as an expert Career Coach and recommend the top 3 best job titles I should apply for.
    
    For each job title, include:
    1. Why I am a good match based on my skills.
    2. What missing skills I should learn to become a perfect candidate for it.
    
    Keep the formatting clean, use markdown headers, bullet points, and use emojis!
    """
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert career coach."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1024
    )
    
    return completion.choices[0].message.content


# --- TEST OUR GROQ CAREER COACH ---
if __name__ == "__main__":
    from parser import extract_text
    
    resume_text = extract_text("sample pdf.pdf")
    my_skills = extract_skills(resume_text)
    
    job_title = "Data Analyst"
    fake_job = """
    We are looking for a Data Analyst to join our team.
    You must have strong skills in Python and SQL (PostgreSQL).
    Experience with data visualization tools like Tableau or Power BI is required.
    You should also be comfortable with Excel, Statistics, and Pandas for data manipulation.
    """
    
    missing = get_missing_skills(my_skills, fake_job)
    generate_advanced_roadmap(missing, job_title)
