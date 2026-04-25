---
name: code-review
description: >
  Perform a thorough pre-commit code review on Python files or diffs. Use this skill
  whenever the user wants to review code before committing or pushing, asks for a
  code review, shares a diff or file and wants feedback, or says things like "review
  my code", "check this before I push", "check this before I commit", "any issues with this?", "pre-commit review", 
  or "is this production-ready?". Also trigger when the user pastes Python code and
  asks for general feedback, even without explicitly using the word "review". Always
  use this skill for any Python code quality, correctness, or style check. For full codebase reviews spanning multiple files, defer to the code-quality-reviewer agent instead.
---

# Code Review Skill (Python)

A skill for performing structured, actionable pre-commit code reviews on Python codebases.

---

## What This Skill Does

Performs a multi-dimensional review of Python code covering correctness, security,
style, performance, and maintainability — and produces a prioritized, actionable report.

---

## Inputs

Accept any of the following:
- Raw Python code pasted inline
- A unified diff / `git diff` output
- A file path (read via bash or view tool)
- A description of what the code is supposed to do (optional but helpful)

If no context is given about the purpose of the code, infer it from the code itself
before reviewing.

---

## Review Dimensions

Work through **all** dimensions below for every review. Skip a dimension only if it is
genuinely not applicable (e.g. no I/O code → skip "Resource Management").

### 1. Correctness
- Logic errors, off-by-one errors, wrong conditionals
- Incorrect handling of edge cases (empty input, None, zero, negative numbers)
- Unhandled exceptions or overly broad `except` clauses
- Incorrect use of mutable default arguments
- Race conditions or incorrect assumptions about execution order

### 2. Security
- Injection risks (SQL, shell, LDAP) — check `subprocess`, `os.system`, raw SQL strings
- Hardcoded secrets, tokens, or credentials
- Insecure use of `eval()`, `exec()`, `pickle`
- Missing input validation or sanitization
- Improper file permissions or path traversal risks
- Exposure of sensitive data in logs or error messages

### 3. Python Style & Idioms (PEP 8 + Pythonic patterns)
- Naming conventions: `snake_case` for variables/functions, `PascalCase` for classes
- Line length (≤ 88 chars recommended, 79 for strict PEP 8)
- Use of list/dict/set comprehensions where appropriate
- Prefer `with` statements for resource management
- Avoid anti-patterns: `range(len(...))`, bare `except`, mutable defaults, `== None`
- Type hints present on public functions/methods (Python 3.5+)
- Docstrings on public modules, classes, and functions (Google or NumPy style)

### 4. Performance
- Unnecessary repeated computation inside loops
- Inefficient data structures (e.g. list where set/dict lookup would be O(1))
- N+1 query patterns or missing batch operations
- Large objects held in memory longer than needed
- Missing use of generators for large sequences

### 5. Maintainability & Readability
- Functions/methods doing too many things (Single Responsibility)
- Magic numbers or strings without named constants
- Dead code, commented-out blocks, TODO/FIXME left in
- Deeply nested logic that could be flattened or extracted
- Missing or misleading comments

### 6. Error Handling & Logging
- Missing error handling for I/O, network, and DB operations
- Swallowing exceptions silently
- Using `print()` instead of `logging` in non-script code
- Logging sensitive data

### 7. Tests (if test files are included or referenced)
- Test coverage for happy path, edge cases, and error paths
- Tests asserting on meaningful output, not just "no exception raised"
- No logic in tests (if/for in test bodies is a smell)
- Fixtures and mocks used appropriately

### 8. Resource Management
- Files, sockets, DB connections opened but not closed
- Missing `finally` or context managers
- Potential memory leaks in long-running processes

---

## Output Format

Always produce a structured review in this format:

```
## Code Review Summary

**File / Scope:** <filename or description>
**Severity Legend:** 🔴 Critical · 🟠 Major · 🟡 Minor · 🔵 Suggestion

---

### 🔴 Critical Issues
<issue title>
- **Location:** line X (or function name)
- **Problem:** <what is wrong and why it matters>
- **Fix:**
  ```python
  # corrected code
  ```

### 🟠 Major Issues
(same structure)

### 🟡 Minor Issues
(same structure)

### 🔵 Suggestions & Best Practices
(same structure — optional improvements, not bugs)

---

### ✅ What Looks Good
- <1–3 things done well — always include this section>

---

### Summary
<2–4 sentence overall assessment. State whether the code is ready to push,
needs minor fixes, or needs significant rework before merging.>
```

---

## Severity Definitions

| Level | When to use |
|---|---|
| 🔴 Critical | Will cause a bug, crash, data loss, or security vulnerability in production |
| 🟠 Major | Likely to cause problems under real load or edge cases; should be fixed before merge |
| 🟡 Minor | Style, readability, or maintainability issue; fix recommended but not blocking |
| 🔵 Suggestion | Optional improvement; idiomatic Python, performance micro-opt, or future-proofing |

---

## Behaviour Guidelines

- **Be specific:** always include the line number or function name.
- **Show the fix:** for every Critical or Major issue, provide a corrected code snippet.
- **Be balanced:** always include the "What Looks Good" section. Don't just list problems.
- **Don't pile on:** if the same pattern is wrong in 10 places, flag it once with a note
  that it appears multiple times rather than listing it 10 times.
- **Respect scope:** if reviewing a diff, focus on changed lines. Mention pre-existing
  issues only if they interact with the new code.
- **Ask if unclear:** if the purpose of a function is ambiguous, say so and ask before
  guessing — don't invent intent.

---

## Example Trigger Phrases

- "Review this before I push"
- "Can you check my code?"
- "Any issues with this Python file?"
- "Pre-push review please"
- "Is this production-ready?"
- "Here's my diff, what do you think?"
- "Code review" + any Python code or file
