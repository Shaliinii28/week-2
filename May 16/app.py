# Import required libraries
import autogen
import os

# Set up the configuration list for AutoGen using Gemini API directly
config_list = [
    {
        "model": "models/gemini-2.0-flash-001",  
        "api_key": os.getenv("API Key"),  
        "api_type": "google"  
    }
]

# Set up the Language Model (LLM) configuration object
llm_config = {
    "seed": 42,
    "config_list": config_list,
    "temperature": 0  # temperature at 0 for less creative responses
}

# Create the Assistant Agent
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config=llm_config
)

# Create the User Proxy Agent
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "working_directory": "web",
        "llm_config": llm_config
    },
    system_message="""A useful user proxy agent that can execute code and terminate the conversation when the task is done.
    You should terminate the conversation with the keyword 'TERMINATE' at the end of the message when the task is done.
    """
)

# Define the task
task = """Write Python code to output numbers 1 to 100 and then store it in a file"""

# Initiate the chat between the user proxy and the assistant
user_proxy.initiate_chat(
    assistant,
    message=task
)