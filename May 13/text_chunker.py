import fitz
from typing import List
import re

def chunk_pdf_text(pdf_path: str, max_tokens: int = 256, min_chunk_size: int = 25) -> List[str]:
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        if doc.page_count == 0:
            doc.close()
            raise ValueError("PDF is empty or contains no pages.")
        
        # Extract text from all pages
        text = ""
        for page in doc:
            page_text = page.get_text("text") or ""
            text += page_text + "\n\n"
        
        doc.close()
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF.")
        
        # Clean text: replace multiple newlines with double newlines for paragraph detection
        text = re.sub(r'\n\s*\n+', '\n\n', text.strip())
        
        # Split into paragraphs based on double newlines
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        current_token_count = 0
        words_per_token = 0.75  # Approximate: 1 token ≈ 0.75 words
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # Estimate token count for the paragraph (word count / words_per_token)
            word_count = len(para.split())
            token_count = word_count / words_per_token
            
            # If paragraph is too large, split into smaller chunks
            if token_count > max_tokens:
                words = para.split()
                temp_chunk = ""
                temp_token_count = 0
                
                for word in words:
                    word_token_count = 1 / words_per_token
                    if temp_token_count + word_token_count > max_tokens:
                        if len(temp_chunk) >= min_chunk_size:
                            chunks.append(temp_chunk.strip())
                        temp_chunk = word
                        temp_token_count = word_token_count
                    else:
                        temp_chunk += " " + word
                        temp_token_count += word_token_count
                
                if len(temp_chunk.strip()) >= min_chunk_size:
                    chunks.append(temp_chunk.strip())
                continue
            
            # If adding paragraph exceeds max_tokens, save current chunk and start new one
            if current_token_count + token_count > max_tokens:
                if len(current_chunk) >= min_chunk_size:
                    chunks.append(current_chunk.strip())
                current_chunk = para
                current_token_count = token_count
            else:
                current_chunk += "\n\n" + para if current_chunk else para
                current_token_count += token_count
        
        # Add the final chunk if it meets the minimum size
        if len(current_chunk.strip()) >= min_chunk_size:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else ["No valid chunks created."]
    
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    try:
        chunks = chunk_pdf_text("Book_sample.pdf", max_tokens=256, min_chunk_size=25)
        for i, chunk in enumerate(chunks, 1):
            print(f"Chunk {i}:\n{chunk}\n{'-'*50}")
    except Exception as e:
        print(f"Error: {str(e)}")