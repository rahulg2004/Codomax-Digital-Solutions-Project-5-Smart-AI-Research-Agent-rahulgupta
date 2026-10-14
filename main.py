import ast
import json
import operator
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Add it to your .env file."
    )

client = Groq(api_key=API_KEY)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
MEMORY_FILE = DATA_DIR / "notes.json"

MAX_HISTORY_MESSAGES = 20
MAX_TOOL_ROUNDS = 5

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def evaluate(node):
    if isinstance(node, ast.Expression):
        return evaluate(node.body)

    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float):
            return node.value
        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.BinOp):
        if type(node.op) not in OPERATORS:
            raise ValueError("Unsupported operation.")

        left = evaluate(node.left)
        right = evaluate(node.right)

        if isinstance(node.op, ast.Pow):
            if abs(right) > 10:
                raise ValueError("Exponent is too large.")

        result = OPERATORS[type(node.op)](left, right)

        if isinstance(result, complex) or abs(result) > 1e100:
            raise ValueError("Result is too large.")

        return result

    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in OPERATORS:
            raise ValueError("Unsupported operation.")

        return OPERATORS[type(node.op)](evaluate(node.operand))

    raise ValueError("Invalid mathematical expression.")


def calculate(expression: str) -> dict:
    try:
        if len(expression) > 200:
            return {"error": "Expression is too long."}

        tree = ast.parse(expression, mode="eval")
        result = evaluate(tree)

        return {
            "expression": expression,
            "result": result,
        }

    except Exception as exc:
        return {"error": str(exc)}


def load_notes():
    if not MEMORY_FILE.exists():
        return []

    try:
        notes = json.loads(
            MEMORY_FILE.read_text(encoding="utf-8")
        )

        if isinstance(notes, list):
            return [
                note for note in notes
                if isinstance(note, str)
            ]

        return []

    except (json.JSONDecodeError, OSError):
        return []


def save_note(note: str) -> dict:
    if not note.strip():
        return {"error": "Note cannot be empty."}

    if len(note) > 2000:
        return {"error": "Note cannot exceed 2000 characters."}

    notes = load_notes()
    notes.append(note.strip())

    try:
        MEMORY_FILE.write_text(
            json.dumps(
                notes,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return {
            "success": True,
            "message": "Note saved successfully.",
            "note": note.strip(),
        }

    except OSError:
        return {"error": "Unable to save the note."}


def recall_notes() -> dict:
    return {"notes": load_notes()}


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Calculate a mathematical expression using "
                "basic arithmetic. Use this tool for calculations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A mathematical expression, such as "
                            "(250 + 150) / 8"
                        ),
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": (
                "Save information when the user explicitly asks "
                "to remember or save a note."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "note": {
                        "type": "string",
                        "description": "The note to save.",
                    }
                },
                "required": ["note"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_notes",
            "description": (
                "Retrieve notes saved in previous sessions "
                "when the user asks about saved information."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


def execute_tool(name, arguments):
    try:
        if name == "calculate":
            if not isinstance(arguments.get("expression"), str):
                return {"error": "Invalid expression argument."}

            return calculate(arguments["expression"])

        if name == "save_note":
            if not isinstance(arguments.get("note"), str):
                return {"error": "Invalid note argument."}

            return save_note(arguments["note"])

        if name == "recall_notes":
            return recall_notes()

        return {"error": "Unknown tool."}

    except Exception:
        return {"error": "The tool could not be executed."}


SYSTEM_PROMPT = """
You are Smart AI Research Agent, a helpful AI assistant.

You can use three tools:
1. calculate: perform supported mathematical calculations.
2. save_note: save notes when the user asks you to remember something.
3. recall_notes: retrieve previously saved notes.

Use the calculator for arithmetic instead of guessing.
Use the memory tools when appropriate.
Never claim a note was saved unless the tool confirms success.
Only describe actions that were actually completed.
Explain tool results clearly and honestly.
Do not invent information from notes that were not retrieved.
Do not claim to have live web access.
Ask for clarification if a request is ambiguous.
"""


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }
]


def ask_agent(user_input):
    messages.append({
        "role": "user",
        "content": user_input,
    })

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            temperature=0.2,
            max_completion_tokens=2048,
        )

        assistant_message = response.choices[0].message
        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        if not assistant_message.tool_calls:
            answer = assistant_message.content or (
                "The model returned an empty response."
            )

            if len(messages) > MAX_HISTORY_MESSAGES + 1:
                messages[:] = [messages[0]] + messages[
                    -(MAX_HISTORY_MESSAGES):
                ]

            return answer

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name

            try:
                arguments = json.loads(
                    tool_call.function.arguments or "{}"
                )

                if not isinstance(arguments, dict):
                    raise ValueError("Arguments must be an object.")

                result = execute_tool(tool_name, arguments)

            except (ValueError, TypeError, json.JSONDecodeError):
                result = {"error": "Invalid tool arguments."}

            print(f"[Tool used: {tool_name}]")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    result,
                    ensure_ascii=False,
                ),
            })

    messages.append({
        "role": "user",
        "content": (
            "Please provide a concise response using the results "
            "already available. Do not initiate additional tool calls."
        ),
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tool_choice="none",
        temperature=0.2,
        max_completion_tokens=2048,
    )

    answer = response.choices[0].message.content or (
        "The agent could not produce a final response."
    )

    messages.append({
        "role": "assistant",
        "content": answer,
    })

    if len(messages) > MAX_HISTORY_MESSAGES + 1:
        messages[:] = [messages[0]] + messages[
            -(MAX_HISTORY_MESSAGES):
        ]

    return answer


def main():
    print("=" * 48)
    print("       SMART AI RESEARCH AGENT")
    print("=" * 48)
    print(f"Provider: Groq")
    print(f"Model: {MODEL}")
    print("Tools: Calculator, Save Note, Recall Notes")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 48)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in {"exit", "quit"}:
                print("\nAgent: Goodbye!")
                break

            if not user_input:
                continue

            if len(user_input) > 10000:
                print("Agent: Please keep your message shorter.")
                continue

            answer = ask_agent(user_input)
            print(f"\nAgent: {answer}")

        except KeyboardInterrupt:
            print("\n\nAgent: Goodbye!")
            break

        except Exception as exc:
            status_code = getattr(exc, "status_code", None)

            if status_code == 429:
                print(
                    "\nAgent: Groq rate limit reached. "
                    "Check your API usage and try again later."
                )
            elif status_code in (401, 403):
                print(
                    "\nAgent: Authentication or access error. "
                    "Check your API key and model permissions."
                )
            elif status_code == 503:
                print(
                    "\nAgent: The service is temporarily unavailable. "
                    "Please try again later."
                )
            else:
                print(f"\nAgent: Request failed: {exc}")


if __name__ == "__main__":
    main()
