"""
analyzer.py
Core analysis logic for the AI Pair Engineer.
Handles prompt construction and Groq API interaction.
"""

from groq import Groq
from dataclasses import dataclass


SUPPORTED_LANGUAGES = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "Go",
    "C++",
    "Rust",
]

GROQ_MODELS = {
    "llama-3.3-70b-versatile": "Llama 3.3 70B (Recommended)",
    "llama-3.1-8b-instant": "Llama 3.1 8B (Fastest)",
    "mixtral-8x7b-32768": "Mixtral 8x7B",
}

DEFAULT_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a principal software engineer acting as an AI pair programmer. \
Your role is to provide thorough, constructive, and technically precise code reviews. \
You prioritize correctness, maintainability, and idiomatic code over stylistic preferences. \
You respond only in well-structured Markdown. All code examples must be inside fenced code blocks \
with the appropriate language identifier. Be direct and specific — avoid vague generalisations."""


@dataclass
class AnalysisOptions:
    detect_design_flaws: bool = True
    suggest_refactoring: bool = True
    propose_tests: bool = True
    audit_solid: bool = False
    language: str = "Python"
    model: str = DEFAULT_MODEL


def build_prompt(code: str, options: AnalysisOptions) -> str:
    """Construct the user prompt based on selected analysis options."""

    lang = options.language
    test_framework = _test_framework_for(lang)

    sections = []

    if options.detect_design_flaws:
        sections.append(
            "### 1. Design Flaws\n"
            "Identify architectural issues, anti-patterns, poor separation of concerns, "
            "security vulnerabilities, and any violations of sound engineering principles. "
            "For each issue, explain the problem and its potential impact."
        )

    if options.suggest_refactoring:
        sections.append(
            "### 2. Refactoring Suggestions\n"
            "Provide concrete, ready-to-use refactored code snippets. "
            "Each suggestion must include the original code, the improved version in a fenced code block, "
            f"and a concise explanation of the improvement. Use idiomatic {lang}."
        )

    if options.propose_tests:
        sections.append(
            f"### 3. Unit Test Proposals\n"
            f"Write complete, runnable unit tests using {test_framework}. "
            "Cover at minimum: the happy path, at least two edge cases, and one failure/exception case. "
            "Tests must be self-contained and require no modification to run."
        )

    if options.audit_solid:
        sections.append(
            "### 4. SOLID Principles Audit\n"
            "Evaluate the code against each of the five SOLID principles. "
            "For each principle, state whether it is satisfied or violated, and if violated, "
            "provide a targeted fix or refactored snippet."
        )

    sections_text = "\n\n".join(sections)

    return f"""Review the following {lang} code and produce a structured analysis covering each section below.

{sections_text}

### Overall Assessment
Conclude with a brief paragraph (3–5 sentences) summarising the overall code quality, \
the single most critical issue to address, and the highest-priority next step.

---

**Code under review:**

```{lang.lower()}
{code}
```"""


def run_analysis(code: str, api_key: str, options: AnalysisOptions) -> str:
    """
    Send the code to the Groq API and return the analysis as a Markdown string.
    Raises groq.AuthenticationError, groq.RateLimitError, or generic exceptions on failure.
    """
    client = Groq(api_key=api_key)
    prompt = build_prompt(code, options)

    response = client.chat.completions.create(
        model=options.model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    return response.choices[0].message.content


def _test_framework_for(language: str) -> str:
    mapping = {
        "Python": "pytest",
        "JavaScript": "Jest",
        "TypeScript": "Jest with ts-jest",
        "Java": "JUnit 5",
        "Go": "the standard testing package",
        "C++": "Google Test",
        "Rust": "Rust's built-in #[cfg(test)] module",
    }
    return mapping.get(language, "an appropriate testing framework")