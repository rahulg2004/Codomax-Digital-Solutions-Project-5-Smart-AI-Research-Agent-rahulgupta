# 🤖 Smart AI Research Agent

A Python-based AI agent built using the Groq API that can understand natural language instructions, perform calculations, save and recall information, and automatically invoke tools to complete tasks. The project demonstrates the fundamentals of AI agents, Large Language Models (LLMs), function calling, persistent memory, and automation.

Developed as part of **Module 5: AI Agents, Tools & Automation**, this project explores how an LLM can go beyond generating text by interacting with external Python functions and stored information.

## 🚀 Project Overview

The Smart AI Research Agent combines an LLM with custom Python tools to create an interactive command-line assistant. Instead of relying entirely on text generation, the agent can select appropriate tools, execute functions, process their results, and use those results to formulate a response.

The project uses **Groq** for fast LLM inference and the `openai/gpt-oss-120b` model for reasoning and tool calling. A local JSON file stores notes so that saved information can remain available across application restarts.

## ✨ Key Features

- **AI-Powered Conversations:** Interact with the agent using natural language.
- **Automatic Function Calling:** The model can request available tools when they are useful for answering a query.
- **Calculator Tool:** Evaluate mathematical expressions using a restricted Python AST-based evaluator.
- **Persistent Memory:** Save notes in a local JSON file and retrieve them in later conversations.
- **Conversational History:** Maintain recent messages to help the agent understand the current conversation.
- **Tool Execution:** Execute supported Python functions and return their results to the model.
- **API Integration:** Connect to Groq using an API key stored in an environment file.
- **Error Handling:** Handle common API errors, including authentication failures, rate limits, unavailable services, and model errors.
- **Command-Line Interface:** Use the agent directly from a terminal without requiring a separate web interface.
- **Configurable Model:** Change the model through an environment variable rather than editing the main application logic.

## 🛠️ Technologies Used

- **Python:** Core programming language.
- **Groq API:** LLM inference and tool-calling integration.
- **GPT-OSS 120B:** Language model configured for reasoning and supported tool calls.
- **Groq Python SDK:** Communication with the Groq API.
- **python-dotenv:** Loading environment variables from `.env`.
- **JSON:** Local storage for persistent notes.
- **Abstract Syntax Trees (AST):** Restricted parsing of calculator expressions.
- **Git and GitHub:** Version control and project hosting.

## 🏗️ Project Structure

```text
Smart-AI-Research-Agent/
│
├── main.py             # Agent logic, tools, and CLI
├── requirements.txt    # Python dependencies
├── .env                # API key and model configuration
├── .gitignore          # Files excluded from Git
│
└── data/
    └── notes.json      # Persistent notes, created when needed
```

The `data/notes.json` file may be created automatically when the application saves its first note. Its exact creation behaviour depends on the implementation in `main.py`.

## ⚙️ How It Works

The agent follows a tool-calling workflow:

1. **User Input:** The user enters a request through the command-line interface.
2. **Model Request:** The application sends the conversation and available tool definitions to the Groq API.
3. **Tool Selection:** If a tool is needed, the model returns a tool call with the requested function and arguments.
4. **Tool Execution:** Python executes the corresponding function, such as the calculator or note-saving function.
5. **Tool Result:** The function result is returned to the model as part of the conversation.
6. **Final Response:** The model uses the tool output to generate a response for the user.
7. **Memory and History:** Saved notes are stored in JSON, while recent messages help maintain conversational context.

The application supports multiple tool-calling rounds, subject to the limit configured in the code, so the model can use tool results before producing its final response.

## 🔧 Available Tools

### 1. Calculator

The calculator evaluates supported mathematical expressions without using unrestricted Python `eval()`.

Supported operators include:

- Addition (`+`)
- Subtraction (`-`)
- Multiplication (`*`)
- Division (`/`)
- Exponentiation (`**`)
- Unary positive and negative operators

The implementation uses an AST-based allowlist and limits expression length, exponent size, and result magnitude to reduce the risk of unsafe or excessively large calculations.

**Example prompt:**

```text
Calculate 125 * 48
```

**Expected result:**

```text
6000
```

Only the operations implemented in the calculator are supported. This is not a general-purpose Python execution tool.

### 2. Save Notes

The note-saving tool stores information in a local JSON file.

**Example prompt:**

```text
Remember that my project is Smart AI Research Agent.
```

The agent can use the note-saving function to store this information for future recall.

### 3. Recall Notes

The recall tool retrieves previously stored notes from the JSON file.

**Example prompt:**

```text
What project name did I ask you to remember?
```

The agent can retrieve the saved note and use it to answer the question.

**Important:** Persistent notes and conversational history are different. Notes saved to the JSON file can survive application restarts, whereas in-memory chat history may reset when the application is restarted.

## 📋 Prerequisites

Before running the project, make sure you have:

- Python 3.10 or a compatible version supported by your installed dependencies.
- A working internet connection.
- A Groq account with API access.
- A valid Groq API key.
- Visual Studio Code or another Python editor.
- Git, if you want to publish the project on GitHub.

## 📥 Installation and Setup

### Step 1: Clone the Repository

Replace the example URL with your actual GitHub repository URL.

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Alternatively, download the project and open its folder in VS Code.

### Step 2: Create a Virtual Environment

On Windows:

```bash
python -m venv .venv
```

Activate it in Command Prompt:

```bash
.venv\Scripts\activate
```

For PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

Ensure that `requirements.txt` contains the packages used by the project. For the current Groq implementation, it can contain:

```text
groq
python-dotenv
requests
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

The `requests` package is optional if your code does not use it directly or through another dependency.

### Step 4: Configure the Environment

Create a file named `.env` in the same directory as `main.py`.

Add the following configuration:

```dotenv
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

Replace the placeholder with your actual API key. Obtain or manage API keys through the official Groq Console:

https://console.groq.com/

Keep the key private. Do not paste it into source code, screenshots, public issues, or GitHub commits.

### Step 5: Verify the Model Configuration

The application reads the model name from `GROQ_MODEL`. The selected model must be available to your account and support the tool-calling features used by the application.

The currently configured model is:

```text
openai/gpt-oss-120b
```

If you change the model, verify its availability and tool-calling support in the Groq documentation.

### Step 6: Run the Application

Start the agent using:

```bash
python main.py
```

Enter requests in the terminal and inspect the returned responses. Use `Ctrl + C` to stop the application if it does not provide its own exit command.

## 🧪 Testing the Project

Try the following test cases after starting the application.

| Test | Example input | What to verify |
|---|---|---|
| Calculator | `Calculate 125 * 48` | The result is 6000. |
| Save memory | `Remember that my project is Smart AI Research Agent.` | The note is saved. |
| Recall memory | `What project name did I ask you to remember?` | The agent retrieves the saved information. |
| Persistence | Restart the application and recall the note. | The saved note remains available. |
| Natural language | Ask a question that requires calculation. | The model selects the calculator when appropriate. |
| Tool calling | Give a request that requires saving or recalling information. | The agent uses the appropriate available tool. |

Exact wording and output formatting may differ depending on the model response and the implementation.

## 🧠 Memory and Conversation Management

The project uses two forms of information management:

**Persistent memory**

Notes are stored locally in `data/notes.json`. They are intended to remain available across application sessions. Anyone with access to the local file may be able to read its contents, so do not store passwords, API keys, or other sensitive information in notes.

**Conversational history**

Recent messages are maintained to provide context during the conversation. The application limits the history to a configured number of messages to control request size and keep the interaction manageable.

Persistent notes should not be confused with the model's own training data. The application retrieves saved information from its local storage and supplies relevant tool results to the model during a conversation.

## 🔐 Security Considerations

- Store the Groq API key in `.env`.
- Add `.env` to `.gitignore`.
- Never commit real API keys or private credentials.
- Avoid storing sensitive personal information in JSON notes.
- Keep calculator operations restricted to explicitly supported AST nodes and operators.
- Do not add unrestricted shell execution or arbitrary Python execution to the agent.
- Validate tool arguments before using them.
- Review tool calls and outputs when extending the project with external services.

A suitable `.gitignore` file is:

```gitignore
.env
.venv/
__pycache__/
*.pyc
data/
```

This configuration excludes local note data from Git. If you want to provide an example memory file, create a separate sample file with fictional, non-sensitive content.

## 🛠️ Troubleshooting

### 1. API Key Error (401 or 403)

**Possible causes:**
- The API key is incorrect, revoked, or unavailable.
- The `.env` file is missing or not being loaded.
- The key is not being passed to the Groq client.

**Solutions:**
- Verify the spelling of `GROQ_API_KEY`.
- Confirm that `.env` is in the same project directory as `main.py`.
- Ensure the key has not been exposed or revoked.
- Restart the application after changing environment settings.

### 2. Model Not Found (404)

**Possible causes:**
- The model name is incorrect.
- The model has been deprecated or is unavailable to your account.
- The application is reading an old model name.

**Solutions:**
- Check `GROQ_MODEL` in `.env`.
- Use a model ID listed as available to your account in the Groq Console or API.
- Verify that the model supports tool calling.
- Restart the application after changing the configuration.

### 3. Rate Limit Error (429)

You may have reached a request, token, or usage limit.

**Solutions:**
- Review your usage and rate limits.
- Wait before retrying.
- Avoid repeated requests in rapid succession.
- Reduce unnecessary model calls or shorten conversation history where appropriate.

### 4. Service Unavailable (503)

The model service may be temporarily overloaded or unavailable.

**Solutions:**
- Retry after a short wait.
- Check the Groq service status.
- If the issue persists, check the available models and select another supported model that offers tool calling.

### 5. Notes Are Not Being Recalled

**Possible causes:**
- The note was not successfully saved.
- The application is running from a different working directory.
- The JSON file was removed or is malformed.
- The recall tool is not being invoked.

**Solutions:**
- Check whether `data/notes.json` exists.
- Verify that the note is present in the file.
- Confirm that the save and recall tools use the same file path.
- Check terminal output for JSON or file-handling errors.

## 🚀 Future Enhancements

Possible extensions for the project include:

- Web search integration for current information retrieval.
- File reading and document summarisation.
- PDF and research-paper analysis.
- A Streamlit or Flask user interface.
- More specialised tools for data analysis and research.
- Structured conversation storage and memory search.
- Configurable tool permissions and execution logs.
- Unit tests for the calculator and memory functions.
- Better retry logic and handling for transient API failures.
- Optional export of research results into Markdown or PDF reports.

These are potential improvements, not features claimed to be implemented in the current version.

## 📚 Learning Outcomes

Through this project, I gained practical experience with:

- Building an LLM-powered Python application.
- Integrating an external AI API.
- Understanding function calling and tool execution.
- Designing a tool-enabled agent workflow.
- Evaluating mathematical expressions with a restricted AST.
- Implementing JSON-based persistent storage.
- Maintaining conversational context.
- Managing environment variables and API credentials.
- Handling API errors and model availability issues.
- Structuring a project for testing, documentation, and version control.

## 📌 Project Details

**Project Name:** Smart AI Research Agent

**Module:** Module 5: AI Agents, Tools & Automation

**Language:** Python

**AI Provider:** Groq

**Configured Model:** `openai/gpt-oss-120b`

**Interface:** Command-line interface (CLI)

**Storage:** Local JSON file

**Project Type:** AI Agent / LLM Tool Calling / Automation

## 👨‍💻 Author

**Rahul Gupta**

GitHub: https://github.com/rahulg2004

LinkedIn: https://linkedin.com/in/rg-rr2004

🔗 GitHub🚀 : [Add your repository link]

## 📄 License

This project is intended for educational and learning purposes. If you want others to reuse or distribute it, consider adding a `LICENSE` file and selecting a licence appropriate for your goals.

---

⭐ If you find this project useful, consider starring the repository and sharing your feedback.