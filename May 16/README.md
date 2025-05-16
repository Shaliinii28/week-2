# AutoGen with Gemini API Project

## Overview
This project uses the AutoGen framework to create an assistant that can execute tasks such as writing Python code and summarizing articles. The original implementation in the video used an Open AI API key to interact with Open AI models. However, due to the exhaustion of the free quota for the Open AI API, this project has been modified to use the Google Gemini API instead. Specifically, it leverages the `google-generativeai` package to interact with the Gemini model (`models/gemini-2.0-flash-001`).

## Requirements

- **Python 3.8+**: Ensure Python is installed on your system.
- **Virtual Environment**: Recommended for isolating dependencies.
- **Required Python Packages**:
  - `pyautogen`: The AutoGen framework for creating conversational agents.
  - `google-generativeai`: The package to interact with the Gemini API.
  Install these packages using:
  ```bash
  pip install pyautogen google-generativeai
  ```
- **Google Gemini API Key**:
  - Obtain an API key from the Google Cloud Console:
    1. Go to [console.cloud.google.com](https://console.cloud.google.com/).
    2. Create or select a project.
    3. Navigate to "APIs & Services" > "Library".
    4. Search for "Generative Language API" and enable it.
    5. Go to "APIs & Services" > "Credentials".
    6. Create an API key and copy it.
  - Set the API key as an environment variable named `GOOGLE_API_KEY`:
    ```bash
    set GOOGLE_API_KEY=your-actual-gemini-api-key
    ```
    Replace `your-actual-gemini-api-key` with your actual API key.
- **Billing Enabled**: Ensure your Google Cloud project has billing enabled, as the Generative Language API requires it.
- **Working Directory**:
  - The script uses a `web` directory for code execution. Ensure this directory exists:
    ```bash
    mkdir web
    ```

## Workflow
Follow these steps to set up and run the script:

1. **Clone or Create the Project Directory**:
   - Ensure you’re in the project directory (e.g., `F:\Week 2\May 16`):
     ```bash
     cd F:\Week 2\May 16
     ```

2. **Set Up a Virtual Environment** (if not already set up):
   - Create a virtual environment:
     ```bash
     python -m venv autogen_env
     ```
   - Activate the virtual environment:
     ```bash
     autogen_env\Scripts\activate
     ```

3. **Install Dependencies**:
   - Install the required packages:
     ```bash
     pip install pyautogen google-generativeai
     ```

4. **Set the API Key**:
   - Set the `GOOGLE_API_KEY` environment variable:
     ```bash
     set GOOGLE_API_KEY=your-actual-gemini-api-key
     ```
   - Verify it’s set:
     ```bash
     echo %GOOGLE_API_KEY%
     ```

5. **Create the Working Directory**:
   - Ensure the `web` directory exists for code execution:
     ```bash
     mkdir web
     ```

6. **Run the Script**:
   - Execute the `app.py` script:
     ```bash
     python app.py
     ```
   - The script will:
     - Use the Gemini API to generate Python code that outputs numbers 1 to 100 and stores them in a file.
     - Execute the generated code in the `web` directory.
     - Terminate with a message ending in `TERMINATE`.

## Notes
- The original video used the Open AI API, but this implementation uses the Gemini API due to quota limitations.
- If you encounter errors related to the Gemini API (e.g., quota exceeded), check your API quota in the Google Cloud Console under "APIs & Services" > "Quotas".
- If the model `models/gemini-2.0-flash-001` is not available, you can try `models/gemini-1.5-flash` by updating the `config_list` in `app.py`.

## Troubleshooting
- **API Key Errors**: Ensure the `GOOGLE_API_KEY` is set correctly and the Generative Language API is enabled.
- **Model Not Found**: Verify the model name in `config_list`. Use `models/gemini-1.5-flash` if `models/gemini-2.0-flash-001` is unavailable.
- **Billing Issues**: Ensure billing is enabled for your Google Cloud project.