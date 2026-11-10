# Gemini Streamlit Chatbot

A conversational AI chatbot built with Python, Streamlit, and the Google Gemini API. Chat with Google's Gemini 2.5 Flash model through a clean browser-based interface with session-based chat history.

## Prerequisites

- [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- A [Google Gemini API key](https://aistudio.google.com/apikey)

## Setup

### 1. Create the Anaconda environment

```bash
conda create -n kiro_env python=3.11
```

### 2. Activate the environment

```bash
conda activate kiro_env
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Copy the example environment file and add your Gemini API key:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your actual key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

> **Note:** The `.env` file is git-ignored and will not be committed to version control.

## Running the Application

```bash
streamlit run app.py
```

The app will open in your default browser. Type a message in the input box to start chatting with Gemini.

## Project Structure

```
├── app.py                  # Streamlit chat UI and application entry point
├── utils/
│   ├── __init__.py         # Makes utils a Python package
│   └── gemini_client.py    # Gemini API client (load_api_key, send_message)
├── tests/
│   ├── test_gemini_client.py   # Unit and property tests for the API client
│   └── test_app.py             # Streamlit UI tests
├── requirements.txt        # Python dependencies
├── .env.example            # Template for environment variables
├── .env                    # Your API key (git-ignored)
└── .gitignore              # Files excluded from version control
```

## Running Tests

```bash
pytest -q
```
