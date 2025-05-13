import os
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

def call_gemini_api(prompt: str, api_key: str, model_name: str = "gemini-1.5-flash") -> str:
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")
    if not api_key:
        raise ValueError("API key cannot be empty.")
    
    try:
        # Configure the API with the key
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model = genai.GenerativeModel(model_name)
        
        # Send the prompt and get the response
        response = model.generate_content(prompt)
        
        # Extract the text from the response
        if response.text:
            return response.text.strip()
        else:
            return "No valid response received from the Gemini API."
    
    except GoogleAPIError as e:
        raise GoogleAPIError(f"Error calling Gemini API: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def main():
    """Main function to get user input and call the Gemini API."""
    try:
        # Load API key from environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        # Get prompt from user
        prompt = input("Enter your prompt for the Gemini API: ")
        
        # Call the API
        response = call_gemini_api(prompt, api_key)
        
        # Display the response
        print("\nGemini API Response:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    
    except ValueError as ve:
        print(f"Error: {str(ve)}")
    except GoogleAPIError as gae:
        print(f"API Error: {str(gae)}")
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")

if __name__ == "__main__":
    main()