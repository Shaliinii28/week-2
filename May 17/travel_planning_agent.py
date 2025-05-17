import asyncio
import os
from typing import List, AsyncGenerator

# AutoGen imports
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

# Message types
from autogen_core.models._types import SystemMessage, UserMessage
from autogen_agentchat.messages import ChatMessage, TextMessage

# Google Gemini API
import google.generativeai as genai

# Custom AssistantAgent to handle responses
class CustomAssistantAgent(AssistantAgent):
    def __init__(self, name: str, model_client, description: str, system_message: str):
        super().__init__(name=name, model_client=model_client, description=description)
        self._system_message = system_message  # Store system message explicitly

    async def on_messages_stream(self, messages: List[ChatMessage], cancellation_token: asyncio.Event = None) -> AsyncGenerator[TextMessage, None]:
        try:
            print(f"\n🔍 {self.name} processing messages: {[type(msg).__name__ for msg in messages]}")
            print(f"\n🔍 {self.name} system message: {self._system_message[:100]}...")
            # Call the model client’s create method with system message
            response = await self._model_client.create(messages, system_message=self._system_message)
            
            # Ensure response is a TextMessage
            if isinstance(response, TextMessage):
                print(f"\n🔄 {self.name} yielding TextMessage: {response.content[:100]}...")
            else:
                content = str(response)
                print(f"\n🔄 {self.name} converting unexpected response type {type(response)} to TextMessage: {content[:100]}...")
                response = TextMessage(content=content, source=self.name)

            yield response

        except Exception as e:
            error_msg = f"Error in on_messages_stream: {str(e)}"
            print(f"\n❌ {self.name} error: {error_msg}")
            yield TextMessage(content=error_msg, source=self.name)

# Custom Gemini client wrapper for AutoGen compatibility
class GeminiChatCompletionClient:
    def __init__(self, model: str):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_info = {
            "vision": False,
            "model_name": model
        }

    async def create(self, messages: List[ChatMessage], system_message: str = None, **kwargs) -> TextMessage:
        prompt_lines = []

        # Include system message if provided
        if system_message:
            prompt_lines.append(f"System: {system_message}")

        print("📥 Incoming Messages:")
        for msg in messages:
            if isinstance(msg, SystemMessage):
                prompt_lines.append(f"System: {msg.content}")
            elif isinstance(msg, UserMessage):
                prompt_lines.append(f"User: {msg.content}")
            elif isinstance(msg, TextMessage):
                prompt_lines.append(f"{msg.source}: {msg.content}")
            else:
                print(f"⚠️ Unhandled message type: {type(msg)}")
                continue

        prompt = "\n".join(prompt_lines)
        print("\n🧠 Final Prompt Sent to Gemini:\n", prompt)

        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            print("\n👀 Gemini Raw Response Type:", type(response))
            print("\n📚 Gemini Raw Attributes:", dir(response))

            # Validate Gemini's response
            content = ""
            try:
                content = response.text.strip()
            except Exception as e:
                print(f"⚠️ Failed to extract .text from Gemini response: {str(e)}")
                content = "⚠️ Gemini did not produce any content."

            if not content:
                print("⚠️ Gemini returned empty content.")
                content = "⚠️ Gemini returned an empty response."

            print("\n✨ Gemini Response:\n", content)
            result = TextMessage(content=content, source="Gemini")
            print("\n📤 Response to AutoGen:\n", result)
            return result

        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            result = TextMessage(content=f"⚠️ Sorry, I couldn't process that request due to an internal error: {str(e)}", source="Gemini")
            print("\n📤 Fallback Response to AutoGen:\n", result)
            return result

    async def close(self):
        pass  # No explicit close needed for Gemini

async def main() -> None:
    # Create a model client for Gemini
    model_client = GeminiChatCompletionClient(model="gemini-1.5-pro")

    # Define agents using CustomAssistantAgent
    planner_agent = CustomAssistantAgent(
        name="planner_agent",
        model_client=model_client,
        description="A helpful assistant that can plan trips.",
        system_message="You are a helpful assistant that can suggest a detailed travel plan for a user based on their request. Assume a mid-range budget, a focus on culture and history, and travel in May 2025 (spring in Nepal). Provide a complete 3-day itinerary focusing on the Kathmandu Valley, with specific activities, locations, and timings. Do not ask for additional user preferences.",
    )

    local_agent = CustomAssistantAgent(
        name="local_agent",
        model_client=model_client,
        description="A local assistant that can suggest local activities or places to visit.",
        system_message="You are a helpful assistant that can suggest authentic and interesting local activities or places to visit in Nepal’s Kathmandu Valley, enhancing the provided travel plan with unique cultural or historical experiences. Focus on activities in Kathmandu, Bhaktapur, and Patan for a 3-day trip, using context from the planner’s itinerary.",
    )

    language_agent = CustomAssistantAgent(
        name="language_agent",
        model_client=model_client,
        description="A helpful assistant that can provide language tips for a given destination.",
        system_message="You are a helpful assistant that can review the provided travel plan for Nepal and offer specific language and communication tips for the Kathmandu Valley. Provide practical advice on common Nepali phrases, greetings, and communication challenges for tourists. If the plan includes language tips, confirm their adequacy with rationale.",
    )

    travel_summary_agent = CustomAssistantAgent(
        name="travel_summary_agent",
        model_client=model_client,
        description="A helpful assistant that can summarize the travel plan.",
        system_message="You are a helpful assistant that integrates suggestions from the planner, local, and language agents into a detailed, cohesive 3-day travel plan for Nepal’s Kathmandu Valley. Ensure the final plan is complete, including specific activities, timings, locations, and language tips. Your response must be the full itinerary, followed by 'TERMINATE' when complete.",
    )

    # Create termination condition
    termination = TextMentionTermination("TERMINATE")

    # Create the team
    group_chat = RoundRobinGroupChat(
        participants=[planner_agent, local_agent, language_agent, travel_summary_agent],
        termination_condition=termination
    )

    # Run the team with the sample task
    task = "Plan a 3-day trip to Nepal."
    result = await Console(group_chat.run_stream(task=task))

    print("✅ Final Result:", result)

    await model_client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print("🔥 Runtime Error:", e)
    except Exception as e:
        print("🔥 Unexpected Error:", e)