# PandeyBot

PandeyBot is a small, local chatbot with a Streamlit web interface. It uses
the `llama3.2:1b` model through Ollama. Once Ollama, the model, and the Python
packages are installed, chat requests are processed on your computer; they
are not sent to the OpenAI API.

## Project layout

```text
LLM/
└── Ollama/
    ├── requirements.txt
    └── Chatbot/
        ├── app.py
        └── README.md
```

The shared `requirements.txt` is one level above this project. It contains
the Python packages needed by the Ollama projects in this repository.

## What you need

- Windows 10 or 11
- Python 3.10 or newer
- Git
- Internet access for the initial clone, installations, and model download
- Enough free disk space for Ollama and the model (the model is a separate
  download)
- Sufficient memory and processing power to run the model

After the initial setup, PandeyBot can run without internet access, provided
Ollama, the model, and the Python packages are already installed.

## Clone and run on Windows

Open PowerShell and clone the repository:

```powershell
git clone https://github.com/viveksirji/LLM.git
```

Enter the cloned repository:

```powershell
Set-Location ".\LLM"
```

Install Ollama if it is not already installed:

```powershell
winget install --id Ollama.Ollama --exact
```

If Ollama was just installed, close and reopen PowerShell so it can find the
`ollama` command. Download the model once:

```powershell
ollama pull llama3.2:1b
```

Create a Python virtual environment in the repository root:

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the shared Python packages from the repository root:

```powershell
python -m pip install -r .\Ollama\requirements.txt
```

Move into the chatbot project:

```powershell
Set-Location ".\Ollama\Chatbot"
```

Start PandeyBot:

```powershell
streamlit run app.py
```

Open the local URL printed by Streamlit, usually
`http://localhost:8501`. Keep the terminal open while chatting. To stop the
server, focus that same terminal and press `Ctrl+C`.

## How to use PandeyBot

1. Type a message in the chat box at the bottom of the page.
2. Press Enter to send it to the local Ollama model.
3. Read the response as it streams into the conversation.
4. Select **New chat** in the sidebar to clear the current conversation.

The app asks the model to keep answers short and limits each generated reply
to 256 tokens. The conversation is kept in Streamlit's session state; it is
not saved to a database or file.

## Control flow: `app.py`, line by line

The line numbers below correspond to the committed `app.py`.

| Line | What it does |
|---:|---|
| 1 | Imports `httpx`, used to catch connection errors when the app cannot reach the local Ollama service. |
| 2 | Imports the Ollama Python client, which sends chat requests to Ollama. |
| 3 | Imports Streamlit as `st`, providing the web UI and session state. |
| 4 | Blank line separating imports from configuration. |
| 5 | Blank line separating imports from configuration. |
| 6 | Sets the model name used for chat. The model must already be available in Ollama. |
| 7 | Starts a multi-line system-prompt string. |
| 8 | Begins the instruction that the assistant should be helpful and concise. |
| 9 | Continues the instruction with a usual answer length and when to provide more detail. |
| 10 | Closes the multi-line system-prompt string. |
| 11 | Blank line separating configuration from page setup. |
| 12 | Configures the browser tab title and chat emoji. This must run before other Streamlit UI commands. |
| 13 | Renders the PandeyBot page heading. |
| 14 | Displays a caption identifying the local model and Ollama. |
| 15 | Blank line separating page setup from session initialization. |
| 16 | Checks whether the current Streamlit browser session has a `messages` history yet. |
| 17 | If no history exists, initializes it as an empty list. |
| 18 | Blank line separating session initialization from the sidebar. |
| 19 | Starts a Streamlit sidebar layout block. |
| 20 | Displays the sidebar heading `Local model`. |
| 21 | Shows the configured model name in code styling. |
| 22 | Tells the user that prompts are processed on this computer. |
| 23 | Renders a full-width **New chat** button and checks whether it was clicked. |
| 24 | Clears the current session's message history when the button is clicked. |
| 25 | Reruns the Streamlit script so the cleared conversation appears immediately. |
| 26 | Blank line separating the sidebar from conversation rendering. |
| 27 | Loops through the messages currently stored in session state. |
| 28 | Opens a chat bubble using each message's role, such as `user` or `assistant`. |
| 29 | Renders that message's text as Markdown inside the bubble. |
| 30 | Blank line separating history rendering from user input handling. |
| 31 | Displays the chat input and runs the block when the user submits a non-empty prompt. |
| 32 | Adds the user's prompt to session history so it is included in later turns. |
| 33 | Opens a user chat bubble for the newly submitted prompt. |
| 34 | Displays the user's submitted text in that bubble. |
| 35 | Blank line separating prompt display from request construction. |
| 36 | Begins building the message list that will be sent to Ollama. |
| 37 | Opens the list literal. |
| 38 | Adds the system instruction that guides the assistant's behavior. |
| 39 | Adds all messages from this session, preserving conversation context. |
| 40 | Closes the list literal. |
| 41 | Blank line separating the conversation from response rendering. |
| 42 | Opens an assistant chat bubble for the response. |
| 43 | Starts error handling around the Ollama request and response stream. |
| 44 | Calls Ollama's chat API for the configured model, with streaming enabled. |
| 45 | Passes the model name to Ollama. |
| 46 | Passes the system instruction and conversation history. |
| 47 | Requests streamed chunks rather than waiting for the entire response. |
| 48 | Limits the generated answer to at most 256 tokens. |
| 49 | Closes the Ollama chat call. |
| 50 | Defines a generator that converts Ollama response chunks into text pieces. |
| 51 | Loops over each chunk as it arrives from Ollama. |
| 52 | Gets the text content from the current chunk's assistant message. |
| 53 | Checks that the chunk contains text before yielding it. |
| 54 | Sends that text piece to Streamlit's stream renderer. |
| 55 | Blank line separating the generator from rendering. |
| 56 | Streams the pieces to the page and collects the completed answer text. |
| 57 | Handles an Ollama model/server error response. |
| 58 | Shows the Ollama error in the assistant chat bubble. |
| 59 | Handles HTTP/network errors when connecting to the local Ollama service. |
| 60 | Starts a multi-line Streamlit error message. |
| 61 | Begins the message explaining the connection problem. |
| 62 | Continues the message telling the user to check Ollama and retry. |
| 63 | Closes the error display call. |
| 64 | Displays the underlying connection error details for troubleshooting. |
| 65 | Runs only if neither of the preceding exception handlers handled an error. |
| 66 | Checks whether the model returned non-empty answer text. |
| 67 | Adds the completed assistant answer to session history. |
| 68 | Creates the assistant message record with its role and content. |
| 69 | Closes the append call. |
| 70 | Handles the case where the model returned no text. |
| 71 | Displays a warning and asks the user to try again. |

### Overall request flow

1. Streamlit starts the script and initializes page settings and session state.
2. The app renders previous messages and the sidebar controls.
3. The user submits a prompt in the chat box.
4. The app adds that prompt to the conversation and prepends the system instruction.
5. The Ollama Python client sends the conversation to the local Ollama service.
6. Ollama runs `llama3.2:1b` and returns response chunks.
7. Streamlit displays each chunk as it arrives, then saves the completed answer in session history.
8. If Ollama is unavailable or returns an error, the app displays an explicit error instead.

## Troubleshooting

- **`ollama` is not recognized:** Open a new terminal after installing Ollama. If needed, add the Ollama install folder to the current PowerShell session's `PATH`.
- **The page refuses to connect:** Start Streamlit with `streamlit run app.py` and keep that terminal open.
- **Ollama connection error in the app:** Make sure the Ollama application/service is running.
- **Model not found:** Download it with `ollama pull llama3.2:1b`.
- **Slow or memory-heavy responses:** Local generation speed depends on the computer's hardware and available memory.

## Project command log

See [TERMINAL_COMMANDS.md](./TERMINAL_COMMANDS.md) for the chronological
PowerShell command log and setup notes.
