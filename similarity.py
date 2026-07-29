import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Compare resumes with job descriptions
def calculate_match_score(resume_text, job_description):
    vectorizer = TfidfVectorizer(stop_words='english')
    text_list = [resume_text, job_description]
    matrix = vectorizer.fit_transform(text_list)
    match_math = cosine_similarity(matrix[0:1], matrix[1:2])
    
    # Calculate percentage
    percentage_score = round(match_math[0][0] * 100, 2)
    return percentage_score

# Professional ATS Structure & Parseability Score
def calculate_ats_score(resume_text, found_skills):
    score = 0
    text_lower = resume_text.lower()
    
    # 1. SECTION DETECTION (Parseability) - 50 points
    standard_sections = ['education', 'experience', 'skills', 'projects', 'summary', 'objective']
    found_sections = 0
    
    for section in standard_sections:
        if section in text_lower:
            found_sections += 1
            
    # Give 10 points for every standard section found
    section_points = found_sections * 10
    if section_points > 50:
        section_points = 50
    score += section_points
    
    # 2. SKILL DENSITY - 30 points
    skill_points = len(found_skills) * 3
    if skill_points > 30:
        skill_points = 30
    score += skill_points
    
    # 3. MEASURABLE IMPACT (Metrics) - 20 points
    if re.search(r'\d', text_lower):  # Regex to check if ANY numbers (digits) exist
        score += 10
    if "%" in text_lower:             # Checks for percentages
        score += 10
        
    return score

# --- TEST OUR CODE ---
if __name__ == "__main__":
    from parser import extract_text
    from nlp_clean import extract_skills
    
    print("Reading resume and finding skills...")
    # Make sure this matches the name of your test PDF!
    resume_text = extract_text("sample pdf.pdf") 
    skills = extract_skills(resume_text)
    
    # A fake Job Description to test against
    fake_job = """
    We are looking for a Software Engineer who knows Python, Java, and MySQL. 
    You must have great Problem Solving skills and Team Collaboration.
    """
    
    print("\n--- CALCULATING SCORES ---")
    
    match_score = calculate_match_score(resume_text, fake_job)
    print(f"🎯 Job Match Score: {match_score}%")
    
    ats_score = calculate_ats_score(resume_text, skills)
    print(f"⭐ Overall ATS Quality Score: {ats_score} / 100")
