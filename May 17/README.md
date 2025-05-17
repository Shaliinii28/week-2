# AI Travel Planner – Multi-Agent Conversational System

This project is a **multi-agent AI travel planner** that simulates a group conversation between AI agents. Each agent has a unique role—planning, suggesting local activities, giving language tips, and summarizing the final plan. The conversation is conducted in a **round-robin** fashion until the final travel plan is ready and one agent says **TERMINATE**.

---

## ✨ Features

- Multiple AI agents collaborating via round-robin communication
- Agents:
  - `Planner Agent`: Plans the itinerary
  - `Local Expert Agent`: Recommends local attractions
  - `Language Tips Agent`: Offers language and communication advice
  - `Summary Agent`: Integrates and finalizes the travel plan
- Terminates automatically when a complete plan is reached
- Console-based interactive simulation

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-travel-planner.git
cd ai-travel-planner
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Add Your API Key

Edit the `main()` function in your Python script and replace:

```python
api_key="your_api_key_here"
```

with your actual key for OpenAI or Gemini (depending on how `OpenAIChatCompletionClient` is implemented).

---

## 🧠 Run the Application

```bash
travel_planner_final.py
```

---

## 📦 Requirements

See `requirements.txt` for the full dependency list.

---

## 💡 Notes

- The `autogen_agentchat` and `autogen_ext` modules are assumed to be part of your local/custom package or cloned repo.
- The termination is triggered when the `travel_summary_agent` returns a message containing `TERMINATE`.

---

