"""
LLM Prompts for Tool Generation
================================

Prompt templates for code generation, improvement, and fixing.

Follows CODE_CONSTITUTION: Clarity Over Cleverness
"""

from __future__ import annotations

from typing import List


def build_generation_prompt(
    description: str,
    function_name: str,
    examples_text: str,
    allowed_imports: List[str],
    max_lines: int,
) -> str:
    """Build prompt for initial code generation.

    Args:
        description: Tool description
        function_name: Desired function name
        examples_text: Formatted examples
        allowed_imports: List of allowed imports
        max_lines: Maximum code lines

    Returns:
        Generation prompt
    """
    return f"""Generate a Python function that does the following:

DESCRIPTION:
{description}

INPUT/OUTPUT EXAMPLES:
{examples_text}

REQUIREMENTS:
1. Function name: {function_name}
2. Type hints for ALL parameters and return value
3. Google-style docstring with Args and Returns
4. Self-contained (only stdlib imports allowed)
5. Handle edge cases gracefully
6. Efficient implementation
7. Maximum {max_lines} lines

ALLOWED IMPORTS:
{', '.join(allowed_imports)}

Output ONLY the function code in a Python code block:

```python
def {function_name}(...):
    \"\"\"Docstring.\"\"\"
    ...
```"""


def build_improvement_prompt(
    code: str,
    function_name: str,
    failures_text: str,
    description: str,
    allowed_imports: List[str],
) -> str:
    """Build prompt for code improvement.

    Args:
        code: Current code with bugs
        function_name: Function name to maintain
        failures_text: Formatted test failures
        description: Original requirements
        allowed_imports: List of allowed imports

    Returns:
        Improvement prompt
    """
    return f"""The following Python function has bugs. Fix them.

ORIGINAL CODE:
```python
{code}
```

TEST FAILURES:
{failures_text}

ORIGINAL REQUIREMENTS:
{description}

CONSTRAINTS:
- Keep the function name: {function_name}
- Maintain all type hints
- Keep docstring
- Only use allowed imports: {', '.join(allowed_imports)}

Output ONLY the corrected code:

```python
def {function_name}(...):
    ...
```"""


def build_syntax_fix_prompt(
    code: str,
    error_message: str,
) -> str:
    """Build prompt for fixing syntax errors.

    Args:
        code: Code with syntax errors
        error_message: Syntax error message

    Returns:
        Fix prompt
    """
    return f"""Fix the syntax error in this Python code:

```python
{code}
```

ERROR: {error_message}

Output only the corrected code in a Python code block."""
