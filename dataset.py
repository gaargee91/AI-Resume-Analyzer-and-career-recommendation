import pandas as pd

print("1. Loading the small dataset...")
# Load the small dataset and get the 'Skill' column
small_df = pd.read_csv("skills.csv")
small_skills = small_df['Skill'].dropna().str.lower().tolist()

print("2. Loading the MASSIVE dataset (this might take a few seconds)...")
# Load the massive dataset
huge_df = pd.read_csv("skills_en.csv")

# Extract ONLY the 'preferredLabel' column (which holds the skill names)
# dropna() removes any blank rows
# str.lower() makes everything lowercase
huge_skills = huge_df['preferredLabel'].dropna().str.lower().tolist()

print("3. Merging and Cleaning...")
# Combine both lists together using the + operator
all_skills = small_skills + huge_skills

# A lot of the skills in the big dataset are actually long sentences!
# Let's clean the data: Only keep skills that are less than 8 words long.
cleaned_skills = []
for skill in all_skills:
    # If the skill has 8 or fewer words, we keep it!
    if len(str(skill).split()) <= 8 :
        cleaned_skills.append(skill)

# Remove all duplicates (if a skill was in both files, we only want it once)
# set() automatically removes duplicates in Python!
final_unique_skills = list(set(cleaned_skills))

# Sort them alphabetically
final_unique_skills.sort()

print(f"4. We narrowed it down to {len(final_unique_skills)} perfectly clean skills!")

print("5. Saving to master_skills.csv...")
# Convert our list back into a Pandas DataFrame
final_df = pd.DataFrame(final_unique_skills, columns=["Skill"])

# Save it to a brand new CSV file! (index=False means we don't save the row numbers)
final_df.to_csv("master_skills.csv", index=False)

print("✅ DONE! You now have a custom master dataset!")
