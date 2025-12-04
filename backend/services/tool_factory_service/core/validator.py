"""
Tool Code Validator
===================

AST-based validation for generated tool code following security best practices.
"""

from __future__ import annotations

import ast
from typing import Dict, List, Optional, Tuple

from config import ToolFactoryConfig


class ToolValidator:
    """Validates generated tool code for syntax and security.

    Follows CODE_CONSTITUTION pillar: Safety First
    """

    def __init__(self, config: ToolFactoryConfig):
        """Initialize validator.

        Args:
            config: Tool factory configuration with allowed/blocked imports
        """
        self.config = config

    def validate_syntax(self, code: str) -> bool:
        """Check if code has valid Python syntax.

        Args:
            code: Python code to validate

        Returns:
            True if syntax is valid, False otherwise
        """
        if not code or not code.strip():
            return False
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def validate_security(self, code: str) -> Optional[str]:
        """Validate code for security issues.

        Args:
            code: Python code to validate

        Returns:
            Error message if validation fails, None if OK

        Raises:
            ValueError: If code cannot be parsed
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Syntax error: {e}")

        # Check for blocked imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split(".")[0]
                    if module in self.config.blocked_imports:
                        return f"Blocked import: {module}"

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split(".")[0]
                    if module in self.config.blocked_imports:
                        return f"Blocked import: {module}"

            # Check for dangerous builtins
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in [
                        "eval",
                        "exec",
                        "compile",
                        "__import__",
                    ]:
                        return f"Dangerous builtin: {node.func.id}"

                    # Special handling for open()
                    if node.func.id == "open":
                        if len(node.args) >= 2:
                            mode_arg = node.args[1]
                            if isinstance(mode_arg, ast.Constant):
                                mode_value = str(mode_arg.value)
                                if "w" in mode_value or "a" in mode_value:
                                    return "File write operations not allowed"

        return None

    def parse_function_metadata(
        self, code: str
    ) -> Tuple[str, Dict[str, Dict[str, str]], str, Optional[str]]:
        """Extract function metadata from code using AST.

        Args:
            code: Python function code

        Returns:
            Tuple of (function_name, parameters, return_type, docstring)
            Parameters format: {param_name: {"type": str, "required": bool, "default": str}}

        Raises:
            ValueError: If code cannot be parsed or no function found
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Syntax error: {e}")

        # Find first function definition
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                name = node.name

                # Parse parameters
                params: Dict[str, Dict[str, str]] = {}
                for arg in node.args.args:
                    param_name = arg.arg
                    param_type = "Any"

                    if arg.annotation:
                        try:
                            param_type = ast.unparse(arg.annotation)
                        except Exception:
                            param_type = "Any"

                    params[param_name] = {
                        "type": param_type,
                        "required": "True",
                    }

                # Handle defaults
                defaults = node.args.defaults
                num_defaults = len(defaults)
                param_names = list(params.keys())

                for i, default in enumerate(defaults):
                    param_idx = len(param_names) - num_defaults + i
                    if param_idx < len(param_names):
                        params[param_names[param_idx]]["required"] = "False"
                        try:
                            params[param_names[param_idx]]["default"] = ast.unparse(
                                default
                            )
                        except Exception:
                            pass

                # Parse return type
                return_type = "Any"
                if node.returns:
                    try:
                        return_type = ast.unparse(node.returns)
                    except Exception:
                        return_type = "Any"

                # Parse docstring
                docstring = ast.get_docstring(node)

                return name, params, return_type, docstring

        raise ValueError("No function definition found in code")

    def extract_code_from_markdown(self, text: str) -> str:
        """Extract Python code from markdown code blocks.

        Handles both ```python and ``` code blocks.

        Args:
            text: Text potentially containing markdown code blocks

        Returns:
            Extracted code or original text if no code block found
        """
        import re

        # Try Python code block
        match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Try generic code block
        match = re.search(r"```\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Return as-is if no code block
        return text.strip()

    def check_line_count(self, code: str) -> bool:
        """Check if code is within line limit.

        Args:
            code: Python code to check

        Returns:
            True if within limit, False otherwise
        """
        line_count = len(code.split("\n"))
        return line_count <= self.config.max_tool_size_lines
