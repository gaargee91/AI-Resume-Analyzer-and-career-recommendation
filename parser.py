import PyPDF2
import docx

def read_pdf(file_path):
    resume_text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Loop through every page in the PDF one by one
        for page in pdf_reader.pages:
            # Extract the text from the current page and add it to our string
            resume_text = resume_text + page.extract_text()
    return resume_text

def read_docx(file_path):
    resume_text = ""
    # Open the Word document
    doc = docx.Document(file_path)
    
    # Loop through every paragraph in the document from top to bottom
    for paragraph in doc.paragraphs:
        # Add the paragraph text and a new line (\n) so it doesn't merge together
        resume_text = resume_text + paragraph.text + "\n"
        
    return resume_text

def extract_text(file_path):
    # Check if the file is a PDF
    if file_path.lower().endswith('.pdf'):
        return read_pdf(file_path)
        
    # Check if the file is a DOCX
    elif file_path.lower().endswith('.docx'):
        return read_docx(file_path)
        
    # If it's something else, give an error
    else:
        return "Error: Unsupported file format. Please upload PDF or DOCX."

# --- TEST OUR CODE ---

# This line just means "Only run this test if I run this file directly"
if __name__ == "__main__":
    
        my_test_file = "sample.docx" 
        
        print(f"Asking the assistant to read: {my_test_file}")
        
        # We call our function and give it the file path!
        extracted_text = extract_text(my_test_file)
        
        print("--- HERE IS WHAT THE ASSISTANT FOUND ---")
        print(extracted_text)
