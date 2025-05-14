import fitz 
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
import os
import re
import argparse
from typing import List
import uuid

def chunk_pdf_text(pdf_path: str, max_tokens: int = 512, min_chunk_size: int = 50) -> List[str]:
    """Extracts and chunks text from a PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        if doc.page_count == 0:
            doc.close()
            raise ValueError("PDF is empty or contains no pages.")
        
        text = ""
        for page in doc:
            page_text = page.get_text("text") or ""
            text += page_text + "\n\n"
        
        doc.close()
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF.")
        
        text = re.sub(r'\n\s*\n+', '\n\n', text.strip())
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        current_token_count = 0
        words_per_token = 0.75
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            word_count = len(para.split())
            token_count = word_count / words_per_token
            
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
            
            if current_token_count + token_count > max_tokens:
                if len(current_chunk) >= min_chunk_size:
                    chunks.append(current_chunk.strip())
                current_chunk = para
                current_token_count = token_count
            else:
                current_chunk += "\n\n" + para if current_chunk else para
                current_token_count += token_count
        
        if len(current_chunk.strip()) >= min_chunk_size:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else ["No valid chunks created."]
    
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")

def store_chunks_in_chromadb(chunks: List[str], collection_name: str, persist_dir: str = "./chroma_db"):
    """Stores chunks in ChromaDB with embeddings."""
    try:
        client = chromadb.PersistentClient(path=persist_dir)
        collection = client.get_or_create_collection(name=collection_name)
        
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = embedder.encode(chunks, show_progress_bar=False)
        
        ids = [str(uuid.uuid4()) for _ in chunks]
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids
        )
        return collection
    
    except Exception as e:
        raise ValueError(f"Error storing chunks in ChromaDB: {str(e)}")

def retrieve_relevant_chunks(query: str, collection, top_k: int = 3) -> List[str]:
    """Retrieves relevant chunks from ChromaDB based on query."""
    try:
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = embedder.encode([query], show_progress_bar=False)[0]
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return results['documents'][0] if results['documents'] else []
    
    except Exception as e:
        raise ValueError(f"Error retrieving chunks from ChromaDB: {str(e)}")

def call_gemini_api(prompt: str, context: List[str], api_key: str, model_name: str = "gemini-1.5-flash") -> str:
    """Calls Gemini API with prompt and context."""
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")
    if not api_key:
        raise ValueError("API key cannot be empty.")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        context_text = "\n\n".join(context) if context else "No context provided."
        full_prompt = f"Context:\n{context_text}\n\nQuestion: {prompt}\nAnswer concisely based on the context."
        
        response = model.generate_content(full_prompt)
        return response.text.strip() if response.text else "No valid response received."
    
    except GoogleAPIError as e:
        raise GoogleAPIError(f"Error calling Gemini API: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def get_pdf_filename() -> str:
    """Prompts user for a PDF file name and validates it."""
    while True:
        pdf_path = input("Enter the PDF file name (e.g., sample.pdf): ").strip()
        if not pdf_path.lower().endswith('.pdf'):
            print("Error: File must have a .pdf extension.")
            continue
        if not os.path.isfile(pdf_path):
            print(f"Error: File '{pdf_path}' not found in the current directory.")
            continue
        return pdf_path

def get_user_query() -> str:
    """Prompts user for a query."""
    while True:
        query = input("Enter your question about the PDF content: ").strip()
        if not query:
            print("Error: Query cannot be empty.")
            continue
        return query

def main():
    parser = argparse.ArgumentParser(description="PDF Query Tool: Extract, chunk, store, and query PDF content.")
    parser.add_argument("--collection", help="ChromaDB collection name", default="pdf_chunks")
    args = parser.parse_args()
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        print("Please provide the PDF file to process.")
        pdf_path = get_pdf_filename()
        
        print("Extracting and chunking PDF...")
        chunks = chunk_pdf_text(pdf_path)
        print(f"Extracted {len(chunks)} chunks.")
        
        print("Storing chunks in ChromaDB...")
        collection = store_chunks_in_chromadb(chunks, args.collection)
        print("Chunks stored successfully.")
        
        print("\nNow you can ask a question about the PDF content.")
        query = get_user_query()
        
        print("Retrieving relevant chunks...")
        relevant_chunks = retrieve_relevant_chunks(query, collection)
        if not relevant_chunks:
            print("No relevant chunks found for the query.")
            return
        
        print("Calling Gemini API to answer query...")
        response = call_gemini_api(query, relevant_chunks, api_key)
        print("\nAnswer:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    
    except FileNotFoundError as fnf:
        print(f"Error: {str(fnf)}")
    except ValueError as ve:
        print(f"Error: {str(ve)}")
    except GoogleAPIError as gae:
        print(f"API Error: {str(gae)}")
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")

if __name__ == "__main__":
    main()