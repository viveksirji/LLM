# Local LLM Projects

This repository is a growing collection of projects for exploring and building
applications powered by large language models (LLMs). The primary goal is to
run models locally whenever practical, so that inference can take place on a
personal computer rather than relying on a hosted model API.

## Project goals

- Build practical, approachable applications with LLMs.
- Learn how models connect to user interfaces and application code.
- Prefer local inference where it fits the project's requirements.
- Document setup, usage, and implementation decisions for each project.
- Keep projects modular so they can be explored and improved independently.

## Projects

### PandeyBot

PandeyBot is a local, browser-based chatbot built with Streamlit. It uses
Ollama to run the `llama3.2:1b` model on the user's computer, streams replies,
and maintains conversation history for the current browser session.

- [PandeyBot overview, setup, and usage](./Ollama/Chatbot/README.md)
- [PandeyBot application source](./Ollama/Chatbot/app.py)

## Local model use

Local inference keeps prompts on the computer while the model is running
locally. Initial setup still requires internet access to download Ollama,
models, and software dependencies. Model files use disk space, and generating
responses requires available memory and processor or graphics resources. Once
the required software and model are installed, local inference can work
without an internet connection.

Each project may have different requirements. Check that project's README for
its model, dependencies, and instructions before running it.

## Repository structure

```text
LLM/
├── Ollama/
│   ├── requirements.txt
│   └── Chatbot/
│       ├── app.py
│       ├── README.md
│       └── TERMINAL_COMMANDS.md
├── .gitignore
└── README.md
```

## Getting started

Choose a project from the list above and follow its README. For PandeyBot,
the project guide explains how to install Ollama, download the model, install
the Python dependencies, and launch the Streamlit interface.

## Security and privacy

- Never commit API keys, passwords, or other credentials.
- Review a project's data flow before entering sensitive information.
- Local inference processes prompts on the computer, but initial downloads
  and any optional online integrations may contact external services.

## Status

This repository is under active development. Projects, documentation, and
setup instructions may evolve as new experiments are added.
