# AI Pair Engineer

An AI-powered code review assistant built with Streamlit and the Groq API. Paste any code snippet and receive a structured, LLM-generated analysis covering design flaws, refactoring proposals, unit test generation, and an optional SOLID principles audit.

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
| Configuration | python-dotenv                                                            |

---

## Project Structure

```text
ai-pair-engineer/
├── app.py              # Streamlit UI, layout, and session management
├── analyzer.py         # Prompt construction, Groq API client, analysis logic
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
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

**Option A — Environment variable (recommended for local use):**

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here
```

**Option B — Streamlit secrets (recommended for cloud deployment):**

Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_key_here"
```

Then update `app.py` to read from `st.secrets`:

```python
env_key = st.secrets.get("GROQ_API_KEY", "")
```

**Option C — In-app input:**

Leave the environment variable unset. The sidebar provides a password-type field where users can enter their own key per session. Keys exist only for the duration of the session and are never stored or logged.

---

## Running Locally

```bash
streamlit run app.py
```

The application opens at `http://localhost:8501`.

---

## Deployment

### Streamlit Community Cloud

1. Push the repository to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select the repository and set the main file to `app.py`.
4. Under **Advanced settings > Secrets**, add:
   ```
   GROQ_API_KEY = "your_key_here"
   ```
5. Click **Deploy**.

---

## Security

- API keys accepted via the sidebar exist only for the duration of the browser session. They are never persisted, logged, or transmitted beyond the Groq API call.
- Do not commit `.env` or `.streamlit/secrets.toml` to version control. Both are excluded via `.gitignore`.
- For multi-user or shared deployments, configure the API key server-side via Streamlit secrets.

---

## License

MIT
