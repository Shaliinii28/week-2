import fitz
import os

def extract_pdf_text(filepath):
    # Check if file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"PDF file not found at: {filepath}")
    
    # Check if file is a PDF
    if not filepath.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF document")
    
    try:
        # Open the PDF
        pdf_document = fitz.open(filepath)
        text = ""
        
        # Iterate through all pages
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            # Extract text from the page
            text += page.get_text() + "\n"
            
        # Close the document
        pdf_document.close()
        return text.strip()
    
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    try:
        pdf_path = "Book_sample.pdf"
        extracted_text = extract_pdf_text(pdf_path)
        print("Extracted Text:")
        print("-" * 50)
        print(extracted_text)
        print("-" * 50)
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {str(e)}")