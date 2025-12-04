"""
Tests for ToolValidator
=======================

Tests for code validation, security checks, and metadata parsing.

Follows CODE_CONSTITUTION: ≥80% coverage, clear test names.
"""

from __future__ import annotations

import pytest

from config import ToolFactoryConfig
from core.validator import ToolValidator


@pytest.fixture
def validator():
    """Create ToolValidator instance."""
    config = ToolFactoryConfig()
    return ToolValidator(config)


class TestSyntaxValidation:
    """Tests for syntax validation."""

    def test_validate_valid_syntax(self, validator):
        """Valid Python syntax should pass."""
        code = """
def add(a: int, b: int) -> int:
    return a + b
"""
        assert validator.validate_syntax(code) is True

    def test_validate_invalid_syntax(self, validator):
        """Invalid syntax should fail."""
        code = "def add(a b):  # Missing comma"
        assert validator.validate_syntax(code) is False

    def test_validate_empty_code(self, validator):
        """Empty code should fail."""
        assert validator.validate_syntax("") is False


class TestSecurityValidation:
    """Tests for security validation."""

    def test_allowed_imports(self, validator):
        """Allowed imports should pass."""
        code = """
import json
import re
from datetime import datetime

def process():
    pass
"""
        assert validator.validate_security(code) is None

    def test_blocked_import_subprocess(self, validator):
        """Blocked import should fail."""
        code = """
import subprocess

def execute_command():
    subprocess.run(['ls'])
"""
        error = validator.validate_security(code)
        assert error is not None
        assert "subprocess" in error

    def test_blocked_import_socket(self, validator):
        """Socket import should be blocked."""
        code = """
import socket

def connect():
    pass
"""
        error = validator.validate_security(code)
        assert error is not None
        assert "socket" in error

    def test_dangerous_builtin_eval(self, validator):
        """eval() should be blocked."""
        code = """
def dangerous():
    eval("1 + 1")
"""
        error = validator.validate_security(code)
        assert error is not None
        assert "eval" in error

    def test_dangerous_builtin_exec(self, validator):
        """exec() should be blocked."""
        code = """
def dangerous():
    exec("print('hello')")
"""
        error = validator.validate_security(code)
        assert error is not None
        assert "exec" in error

    def test_file_read_allowed(self, validator):
        """Reading files should be allowed."""
        code = """
def read_file():
    with open('test.txt', 'r') as f:
        return f.read()
"""
        assert validator.validate_security(code) is None

    def test_file_write_blocked(self, validator):
        """Writing files should be blocked."""
        code = """
def write_file():
    with open('test.txt', 'w') as f:
        f.write('data')
"""
        error = validator.validate_security(code)
        assert error is not None
        assert "write" in error.lower()


class TestMetadataParsing:
    """Tests for function metadata extraction."""

    def test_parse_simple_function(self, validator):
        """Parse simple function metadata."""
        code = """
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b
"""
        name, params, return_type, docstring = validator.parse_function_metadata(code)

        assert name == "add"
        assert "a" in params
        assert "b" in params
        assert params["a"]["type"] == "int"
        assert params["b"]["type"] == "int"
        assert return_type == "int"
        assert docstring == "Add two numbers."

    def test_parse_function_with_defaults(self, validator):
        """Parse function with default arguments."""
        code = """
def greet(name: str, greeting: str = "Hello") -> str:
    \"\"\"Greet someone.\"\"\"
    return f"{greeting}, {name}!"
"""
        name, params, return_type, docstring = validator.parse_function_metadata(code)

        assert name == "greet"
        assert params["name"]["required"] == "True"
        assert params["greeting"]["required"] == "False"
        assert params["greeting"]["default"] in ('"Hello"', "'Hello'")

    def test_parse_function_no_types(self, validator):
        """Parse function without type hints."""
        code = """
def process(data):
    \"\"\"Process data.\"\"\"
    return data
"""
        name, params, return_type, docstring = validator.parse_function_metadata(code)

        assert name == "process"
        assert params["data"]["type"] == "Any"
        assert return_type == "Any"

    def test_parse_no_function(self, validator):
        """No function definition should raise error."""
        code = "x = 42"

        with pytest.raises(ValueError, match="No function definition found"):
            validator.parse_function_metadata(code)

    def test_parse_syntax_error(self, validator):
        """Syntax error should raise ValueError."""
        code = "def add(a b):  # Invalid"

        with pytest.raises(ValueError, match="Syntax error"):
            validator.parse_function_metadata(code)


class TestCodeExtraction:
    """Tests for markdown code extraction."""

    def test_extract_python_block(self, validator):
        """Extract code from ```python block."""
        text = """
Here is some code:

```python
def hello():
    print("Hello")
```

That's it!
"""
        code = validator.extract_code_from_markdown(text)
        assert "def hello():" in code
        assert "print(" in code

    def test_extract_generic_block(self, validator):
        """Extract code from generic ``` block."""
        text = """
```
def hello():
    print("Hello")
```
"""
        code = validator.extract_code_from_markdown(text)
        assert "def hello():" in code

    def test_extract_no_block(self, validator):
        """No code block should return original text."""
        text = "Just plain text"
        code = validator.extract_code_from_markdown(text)
        assert code == "Just plain text"


class TestLineCount:
    """Tests for line count validation."""

    def test_within_limit(self, validator):
        """Code within limit should pass."""
        code = "\n".join(f"# Line {i}" for i in range(50))
        assert validator.check_line_count(code) is True

    def test_exceeds_limit(self, validator):
        """Code exceeding limit should fail."""
        # Default max is 100 lines
        code = "\n".join(f"# Line {i}" for i in range(150))
        assert validator.check_line_count(code) is False

    def test_exact_limit(self, validator):
        """Code at exact limit should pass."""
        # Generate exactly 100 lines (0-99 produces 100 items)
        lines = [f"# Line {i}" for i in range(100)]
        code = "\n".join(lines)
        # Should be exactly at limit (100 lines)
        assert len(code.split("\n")) == 100
        assert validator.check_line_count(code) is True
