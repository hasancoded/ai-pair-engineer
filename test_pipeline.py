"""
test_pipeline.py
End-to-end test for the AI Pair Engineer analysis pipeline.

Usage (with venv active):
    python test_pipeline.py

The script tests three things:
    1. Prompt construction (no API call required)
    2. A live Groq API call with a deliberately flawed code snippet
    3. Validation that the response is non-empty and contains expected sections

Set GROQ_API_KEY in your .env file or as an environment variable before running.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

from analyzer import (
    AnalysisOptions,
    build_prompt,
    run_analysis,
    GROQ_MODELS,
    DEFAULT_MODEL,
    SUPPORTED_LANGUAGES,
)

# ---------------------------------------------------------------------------
# Sample code with intentional issues for testing
# ---------------------------------------------------------------------------

SAMPLE_CODE = """
def get_user(id):
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + str(id)
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PASS = "PASS"
FAIL = "FAIL"


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def result(label: str, passed: bool, detail: str = "") -> None:
    status = PASS if passed else FAIL
    symbol = "+" if passed else "x"
    print(f"  [{symbol}] {status}  {label}")
    if detail:
        print(f"       {detail}")


# ---------------------------------------------------------------------------
# Test 1: Module constants
# ---------------------------------------------------------------------------

def test_constants() -> bool:
    section("Test 1: Module constants")
    ok = True

    valid_langs = isinstance(SUPPORTED_LANGUAGES, list) and len(SUPPORTED_LANGUAGES) > 0
    result("SUPPORTED_LANGUAGES is a non-empty list", valid_langs)
    ok = ok and valid_langs

    valid_models = isinstance(GROQ_MODELS, dict) and len(GROQ_MODELS) > 0
    result("GROQ_MODELS is a non-empty dict", valid_models)
    ok = ok and valid_models

    default_present = DEFAULT_MODEL in GROQ_MODELS
    result(f"DEFAULT_MODEL '{DEFAULT_MODEL}' is in GROQ_MODELS", default_present)
    ok = ok and default_present

    return ok


# ---------------------------------------------------------------------------
# Test 2: Prompt construction (offline)
# ---------------------------------------------------------------------------

def test_prompt_construction() -> bool:
    section("Test 2: Prompt construction (no API call)")
    ok = True

    options = AnalysisOptions(
        detect_design_flaws=True,
        suggest_refactoring=True,
        propose_tests=True,
        audit_solid=False,
        language="Python",
        model=DEFAULT_MODEL,
    )
    prompt = build_prompt(SAMPLE_CODE, options)

    has_code = SAMPLE_CODE.strip() in prompt
    result("Sample code is embedded in the prompt", has_code)
    ok = ok and has_code

    has_design = "Design Flaws" in prompt
    result("Design Flaw section present", has_design)
    ok = ok and has_design

    has_refactor = "Refactoring" in prompt
    result("Refactoring section present", has_refactor)
    ok = ok and has_refactor

    has_tests = "Unit Test" in prompt
    result("Unit Test section present", has_tests)
    ok = ok and has_tests

    no_solid = "SOLID" not in prompt
    result("SOLID section absent when not requested", no_solid)
    ok = ok and no_solid

    has_assessment = "Overall Assessment" in prompt
    result("Overall Assessment section always present", has_assessment)
    ok = ok and has_assessment

    return ok


# ---------------------------------------------------------------------------
# Test 3: Live API call
# ---------------------------------------------------------------------------

def test_live_api(api_key: str) -> bool:
    section("Test 3: Live Groq API call")

    options = AnalysisOptions(
        detect_design_flaws=True,
        suggest_refactoring=False,
        propose_tests=False,
        audit_solid=False,
        language="Python",
        model=DEFAULT_MODEL,
    )

    print(f"  Model : {DEFAULT_MODEL}")
    print(f"  Code  : {len(SAMPLE_CODE.strip())} chars")
    print("  Calling Groq API...", flush=True)

    try:
        response = run_analysis(SAMPLE_CODE, api_key, options)
    except Exception as exc:
        result("API call succeeded", False, str(exc))
        return False

    ok = True

    non_empty = bool(response and response.strip())
    result("Response is non-empty", non_empty)
    ok = ok and non_empty

    reasonable_length = len(response) > 100
    result(f"Response length > 100 chars ({len(response)} chars received)", reasonable_length)
    ok = ok and reasonable_length

    is_markdown = "#" in response or "**" in response or "```" in response
    result("Response contains Markdown formatting", is_markdown)
    ok = ok and is_markdown

    mentions_sql = "SQL" in response.upper() or "injection" in response.lower() or "query" in response.lower()
    result("Response identifies the SQL injection vulnerability", mentions_sql)
    ok = ok and mentions_sql

    if response:
        preview = response.strip()[:200].replace("\n", " ")
        print(f"\n  Preview: {preview}...")

    return ok


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nAI Pair Engineer — Pipeline Test")
    print("=" * 60)

    results = []

    results.append(test_constants())
    results.append(test_prompt_construction())

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        section("Test 3: Live Groq API call")
        print("  [SKIP] GROQ_API_KEY not set. Set it in .env to run the live test.")
        results.append(None)
    else:
        results.append(test_live_api(api_key))

    # Summary
    section("Summary")
    passed = sum(1 for r in results if r is True)
    skipped = sum(1 for r in results if r is None)
    failed = sum(1 for r in results if r is False)
    total = len(results)

    print(f"  Passed : {passed}/{total}")
    if skipped:
        print(f"  Skipped: {skipped}/{total}")
    if failed:
        print(f"  Failed : {failed}/{total}")

    print()
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
