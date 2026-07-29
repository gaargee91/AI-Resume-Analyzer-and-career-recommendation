import spacy
import pandas as pd
import re

nlp = spacy.load("en_core_web_sm")

def extract_skills(resume_text):
    doc = nlp(resume_text)
    cleaned_text = resume_text.lower()
    cleaned_text = cleaned_text.replace("p r o j e c t", "project")

    # Pandas to easily read CSV files
    skills_database = pd.read_csv("master_skills.csv") 
    known_skills = skills_database['Skill'].str.lower().tolist()

    
    # to store the skills we find in the resume
    found_skills = []
    
    #  for every known skill in our cleaned resume text
    for skill in known_skills:
        if str(skill) != "nan":
            
            if len(skill) <= 1:
                continue
            
            search_rule = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'
            if re.search(search_rule, cleaned_text):
                            found_skills.append(skill)

    return found_skills

#  Extract Phone Number
def extract_phone(text):
    phone_pattern = re.compile(r'(?:(?:\+?\d{1,3}\W{1,3})?\d{3}\W{1,3}\d{3}\W{1,3}\d{4}|(?:\+91\W{1,2})?[6-9]\d{9})')

    match = phone_pattern.search(text)
    if match:
        return match.group() 
    return None             

# Extract Email
def extract_email(text):
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    match = email_pattern.search(text)
    if match:
        return match.group()
    return None

# Extract LinkedIn URL
def extract_linkedin(text):
    linkedin_pattern = re.compile(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[\w\-]+')
    match = linkedin_pattern.search(text)
    if match:
        return match.group()
    return None

# Extract Address
def extract_address(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
    
    if locations:
        unique_locs = list(dict.fromkeys(locations))
        return ", ".join(unique_locs[:2])
    return None


# --- TEST OUR CODE ---
if __name__ == "__main__":
    # We will import the Parser we built in Phase 1!
    from parser import extract_text
    
    print("1. Reading the document...")
    # Change this to your sample resume file name!
    resume_text = extract_text("sample_resume.pdf") 
    
    print("2. Giving text to the AI...")
    found_skills = extract_skills(resume_text)
    
    print("--- SKILLS FOUND BY AI ---")
    # This will print the skills nicely, one by one
    for skill in found_skills:
        print(f"✅ {skill.title()}")
