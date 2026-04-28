---
description: "Create a robust Python factorial method for non-negative numbers with return-value error handling, docs, and tests"
name: "Create Factorial Method"
argument-hint: "Target file and optional method name"
agent: "agent"
---
Create a factorial method using these requirements:
- Language: Python only.
- Purpose: compute the factorial of non-negative numbers.
- Input rules:
  - Accept non-negative integers only.
  - Reject negative values.
  - Reject non-integer values.
- Behavior:
  - Return 1 for input 0.
  - Return correct results for common values like 1, 5, and 10.
  - Return a clear error value for invalid inputs (do not raise exceptions).
- Code quality:
  - Use clear names and concise documentation.
  - Avoid magic numbers.
  - Match existing conventions in this workspace.
- Testing:
  - Add or update pytest tests for valid and invalid inputs.
  - Include at least one parameterized test.

Expected output format:
1. Short implementation summary.
2. Exact file changes made.
3. Test results.
4. Any assumptions made.
