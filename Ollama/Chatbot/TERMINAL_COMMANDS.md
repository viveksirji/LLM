# PandeyBot - Terminal Command Log

This document records the PowerShell commands used to set up and run the
local chatbot project in `E:\LLM\Ollama\Chatbot`, along with their status.
Commands that have not been run yet are marked pending. Never put passwords,
API keys, or other secrets in this log.

### Command formatting

Each command is shown in its own code block, separate from explanations and
status notes. Only copy the contents of the code block into the terminal.

## Model setup

Projects under `E:\LLM\Ollama` can use the **shared Ollama installation and
downloaded models**. The model runs on this computer instead of using the
OpenAI API, so it does not require OpenAI credits or incur a per-request
OpenAI API charge. Downloading Ollama, models, and Python packages initially
requires internet access; after setup, local model use can work offline.
Downloaded models use disk space, and running them uses the computer's memory
and processing resources.

For this workspace, the user chose one shared Python environment at
`E:\LLM\Ollama\.venv` for Python projects under `E:\LLM\Ollama`. This makes
installed Python packages available to those projects when they use that
environment. Package versions are shared too, so a version change for one
project can affect another; projects with conflicting dependencies may need
separate environments. The Ollama service and model downloads are shared
independently of Python environments.

## Folder structure

```text
E:\LLM\Ollama\
├── .venv\
├── requirements.txt
└── Chatbot\
    ├── app.py
    ├── README.md
    └── TERMINAL_COMMANDS.md
```

## Setup commands

### 1. Create the parent folder and move the existing chatbot project

```powershell
$source = 'E:\LLM\Chatbot'
$target = 'E:\LLM\Ollama\Chatbot'
if (-not (Test-Path -LiteralPath $source)) { throw "Source folder not found: $source" }
if (Test-Path -LiteralPath $target) { throw "Destination already exists; refusing to overwrite: $target" }
New-Item -ItemType Directory -Path 'E:\LLM\Ollama' -ErrorAction Stop | Out-Null
Move-Item -LiteralPath $source -Destination $target -ErrorAction Stop
Get-ChildItem -Force $target | Select-Object Name, Mode
```

Status: Completed. The existing `E:\LLM\Chatbot` folder was moved to
`E:\LLM\Ollama\Chatbot`; the original path no longer exists. The destination
was checked to avoid overwriting an existing folder.

### 2. Create the shared virtual environment

Run this from `E:\LLM\Ollama`:

```powershell
python -m venv .venv
```

Status: Completed. The user reports that `E:\LLM\Ollama\.venv` was created.

### 3. Activate the shared virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

Run from `E:\LLM\Ollama`.

Status: Completed. The user reports that the shared environment is active.
The terminal prompt should show `(.venv)`. To work on projects in another
terminal, activate this same environment from the parent folder.

### 4. Install shared Python libraries

The shared `requirements.txt` is stored in `E:\LLM\Ollama` so projects under
this parent can use the same Python environment and common packages. It
currently includes `streamlit` for browser interfaces and `ollama` for Python
communication with the Ollama service. With the shared environment active,
run this from `E:\LLM\Ollama`:

```powershell
python -m pip install -r .\requirements.txt
```

Status: Completed. The user reports that the packages finished installing.
The shared requirements include Streamlit, the Ollama Python client, and
httpx for reporting local connection errors. This installs Python libraries
only; it does not install the Ollama application or download a model.

### 5. Check whether Ollama is installed

```powershell
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollama) { ollama --version } else { Write-Output 'Ollama is not available on PATH' }
```

Status: Checked before installation; Ollama was not available on PATH.

### 6. Install Ollama on Windows

The command below is the command that installs the **Ollama application** on
Windows. It uses **WinGet**, Microsoft's Windows Package Manager. Run it in
PowerShell:

- `winget` runs the package manager from PowerShell.
- `install` tells it to install a package.
- `--id Ollama.Ollama` selects the package whose identifier is `Ollama.Ollama`.
- `--exact` requires an exact identifier match, rather than a partial match.

WinGet downloads and installs the Ollama program so the computer can run a
local model and provide a local service for applications to connect to. It
requires internet access for installation and may ask for confirmation or
administrator approval. This is separate from the Python `ollama` library in
`requirements.txt`: that library lets Python applications communicate with
the Ollama program. Installing Ollama does not download a language model; a
model must be downloaded separately.

### How local Ollama differs from an online API

- **Where it runs:** Ollama runs the downloaded model on this computer. An API
  sends your prompt over the internet to a provider's servers, which run the
  model and return a response.
- **Internet use:** Internet is needed initially to install Ollama and
  download a model. Afterward, local inference can work offline. An online API
  needs an internet connection for each request.
- **Cost:** Local Ollama does not charge a provider per request, though
  downloading and running models uses disk space, electricity, and computer
  resources. An API may charge based on usage and account terms.
- **Data path:** With local inference, prompts are processed by the model on
  your computer. With an API, prompts are sent to the provider; review its
  privacy and data policies before sending sensitive text.
- **Resources and model choice:** Local speed and quality depend on the
  downloaded model and this computer's memory and processor or graphics
  hardware. An API provider hosts the model and computing resources.

```powershell
winget install --id Ollama.Ollama --exact
```

In short: running `winget install --id Ollama.Ollama --exact` tells WinGet to
install Ollama using its exact package identifier, `Ollama.Ollama`.

Status: Completed. The user reports that Ollama installed successfully. This
requires internet access and may ask for confirmation during installation. If
WinGet is unavailable, the official Windows installer is at
https://ollama.com/download/windows

### 7. Verify the Ollama installation

```powershell
ollama --version
```

Status: The existing terminal did not recognize `ollama`. Verified the
installation directly using
`"$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" --version`, which returned
`ollama version is 0.40.7`. The Ollama install directory is on the Windows
user PATH, but not in the current terminal's PATH.

The error `ollama : The term 'ollama' is not recognized...` means PowerShell
could not find a command named `ollama` in the PATH available to that terminal.
It does not by itself mean Ollama failed to install. In this case, the
executable was installed and worked when run by its full path, while the
terminal's PATH did not include its install directory.

The user tried a new terminal, but it still did not recognize `ollama`.

Add the known installation directory to this PowerShell session's PATH
temporarily:

```powershell
$env:Path = "$env:LOCALAPPDATA\Programs\Ollama;$env:Path"
```

Then verify the installation:

```powershell
ollama --version
```

Status: Completed successfully according to the user. Adding the directory to
`$env:Path` lets PowerShell find `ollama`. This changes PATH only in the
current PowerShell session; it does not modify the persistent Windows PATH.
When a new terminal is opened, this temporary change may need to be repeated
unless the persistent PATH is refreshed or corrected.

For this terminal only, the executable can also be run directly:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" --version
```

This full-path command bypasses PATH lookup and can help distinguish a PATH
problem from an installation problem.

### 8. Download a small chat model

Use Ollama to download the `llama3.2:1b` model:

```powershell
ollama pull llama3.2:1b
```

This downloads the model to Ollama's local model storage. It needs internet
access and free disk space. After the download, the model can run locally
without sending prompts to an online API. Running it still uses computer
memory and processing resources.

Status: Completed. The user reports that the model download finished. The
user previously reported about 1.6 GB for the Ollama application and about
1.5 GB for the model; model storage is separate from the Ollama application.

### 9. Test the model in an interactive chat

```powershell
ollama run llama3.2:1b
```

This starts a terminal chat with the downloaded model. Type a short message
and press Enter to test it. To exit the chat, enter `/bye`.

Status: Completed successfully. The user confirms the model works in
interactive chat.

If the model is generating a reply that is too long, press `Ctrl+C` once to
interrupt the current response. To encourage shorter answers in later turns,
ask explicitly, for example: `Answer in no more than two short sentences.`
This is text to type into the Ollama chat, not a PowerShell command. Enter
`/bye` to exit the interactive chat.

### 10. Run the Streamlit chatbot

The interactive web interface is named **PandeyBot** and is in
`E:\LLM\Ollama\Chatbot\app.py`. It keeps
the conversation in the current browser session, streams replies, offers a
**New chat** button, and asks the model to be concise. The response length is
also capped to help prevent overly long replies.

To launch PandeyBot from any PowerShell folder using the shared environment:

```powershell
& "E:\LLM\Ollama\.venv\Scripts\python.exe" -m streamlit run "E:\LLM\Ollama\Chatbot\app.py"
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.
Keep the terminal that ran the launch command open while using the app. To
stop Streamlit, focus that same terminal and press `Ctrl+C`. Pressing `Ctrl+C`
in a different terminal will not stop the server.

Status: Created and verified. Python syntax passed, and Streamlit's app test
confirmed the title and chat input render without startup errors. The shared
environment already has `httpx`, used to display local connection errors.
Ready to run. If the Ollama service is unavailable, start or reopen the Ollama
application and retry. The app displays a connection error rather than
silently substituting another model.

Troubleshooting: The browser initially reported that `localhost` refused to
connect because the Streamlit server was not running. Started the app with the
launch command above; Streamlit printed `http://localhost:8501`, and an HTTP
check returned status 200. That server session was later stopped. Start a new
server with the launch command above when you want to use the app.

## Next steps

Further commands will be added here as the setup proceeds, with completion
status and relevant output or errors. Use the shared `.venv` from
`E:\LLM\Ollama` when installing and running Python projects that are intended
to share dependencies. The shared dependency list is
`E:\LLM\Ollama\requirements.txt`; changes to it affect all projects that use
this environment.

## GitHub upload

The repository root is `E:\LLM`, with repository name `LLM`. Only the
Ollama chatbot project and `Ollama\requirements.txt` should be committed, so
the GitHub file tree shows `Ollama\Chatbot`. The unrelated `Text_Summerizer`
project and `LLM_GUIDE.md` are excluded by the root `.gitignore`.

The root `.gitignore` excludes Python virtual environments, generated Python
files, `.env` files, and every `secrets.toml` file. Never commit API keys or
other credentials.

The user reports that a GitHub repository named `LLM` already exists.
Visibility was not specified. The repository URL is still needed to connect
the local repository and upload.

Local Git setup commands:

```powershell
git -C "E:\LLM" init --initial-branch=main
```

Status: Completed. Initialized a local Git repository at `E:\LLM` with the
`main` branch.

Stage only the chatbot project and its shared requirements:

```powershell
git -C "E:\LLM" add -- .gitignore Ollama/requirements.txt Ollama/Chatbot
```

Status: Completed. Staged files:

- `.gitignore`
- `Ollama/requirements.txt`
- `Ollama/Chatbot/TERMINAL_COMMANDS.md`
- `Ollama/Chatbot/app.py`

The initial push to `https://github.com/viveksirji/LLM` completed on the
`main` branch. A project README is maintained at `Ollama\Chatbot\README.md`.

No commit or upload has been made yet. The GitHub repository URL must be
added as the `origin` remote before pushing. Check staged files with:

```powershell
git -C "E:\LLM" status --short
```
