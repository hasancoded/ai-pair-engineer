# AI Pair Engineer

An AI-powered code review assistant built with Streamlit and the Groq API. Paste any code snippet and receive a structured, LLM-generated analysis covering design flaws, refactoring proposals, unit test generation, and an optional SOLID principles audit.

Live demo: [ai-pair-engineer.streamlit.app](https://ai-pair-engineer-5wmztwspncpzfj2xykbpsa.streamlit.app/)

---

## Features

| Module                  | Description                                                                    |
| ----------------------- | ------------------------------------------------------------------------------ |
| Design Flaw Detection   | Identifies anti-patterns, security vulnerabilities, and architectural problems |
| Refactoring Suggestions | Produces concrete, ready-to-use improved code with explanations                |
| Unit Test Proposals     | Generates complete, runnable tests covering happy paths and edge cases         |
| SOLID Principles Audit  | Evaluates each principle individually with targeted refactoring fixes          |

- Multi-language support: Python, JavaScript, TypeScript, Java, Go, C++, Rust
- Model selection: Llama 3.3 70B, Llama 3.1 8B, Mixtral 8x7B via Groq
- Downloadable Markdown reports

---

## Tech Stack

| Layer         | Technology                                                               |
| ------------- | ------------------------------------------------------------------------ |
| UI            | Streamlit                                                                |
| LLM API       | Groq (llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768) |
| Language      | Python 3.9+                                                              |
| Configuration | python-dotenv / Streamlit secrets                                        |

---

## Project Structure

```text
ai-pair-engineer/
├── app.py                    # Streamlit UI, layout, and session management
├── analyzer.py               # Prompt construction, Groq API client, analysis logic
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── .streamlit/
│   └── config.toml           # Streamlit configuration (toolbar, telemetry)
├── .gitignore
└── README.md
```

---

## Prerequisites

- Python 3.9 or higher
- A Groq API key — obtain one free at [console.groq.com](https://console.groq.com)

---

## Installation

```bash
git clone https://github.com/hasancoded/ai-pair-engineer.git
cd ai-pair-engineer
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Configuration

The application resolves the API key in the following priority order:

| Priority | Source                       | Scenario                   |
| -------- | ---------------------------- | -------------------------- |
| 1        | `st.secrets["GROQ_API_KEY"]` | Streamlit Cloud deployment |
| 2        | `GROQ_API_KEY` in `.env`     | Local development          |
| 3        | Sidebar input field          | Per-session manual entry   |

**Local development:**

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here
```

**Streamlit Cloud deployment:**

In the Streamlit Cloud dashboard under **Advanced settings > Secrets**, add:

```toml
GROQ_API_KEY = "your_key_here"
```

No code changes are needed between environments — `app.py` handles both automatically.

---

## Running Locally

```bash
streamlit run app.py
```

The application opens at `http://localhost:8501`.

---

## Deployment

This project is deployed on Streamlit Community Cloud:

[ai-pair-engineer-5wmztwspncpzfj2xykbpsa.streamlit.app](https://ai-pair-engineer-5wmztwspncpzfj2xykbpsa.streamlit.app/)

To deploy your own instance:

1. Fork this repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **Create app**.
3. Select your fork, branch `main`, and main file `app.py`.
4. Under **Advanced settings > Secrets**, add your `GROQ_API_KEY` in TOML format.
5. Click **Deploy**.

---

## Security

- API keys accepted via the sidebar exist only for the duration of the browser session. They are never persisted, logged, or transmitted beyond the Groq API call.
- Do not commit `.env` or `.streamlit/secrets.toml` to version control. Both are excluded via `.gitignore`.
- For shared or multi-user deployments, configure the API key server-side via Streamlit secrets.

---

## License

MIT
