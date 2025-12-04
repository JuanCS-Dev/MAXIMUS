"""
Sandbox Executor
================

Secure Python code execution environment for tool testing.

Follows CODE_CONSTITUTION pillars:
- Safety First: Isolated execution, timeout protection, resource limits
- Clarity Over Cleverness: Simple subprocess-based sandboxing
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from config import ToolFactoryConfig


class SandboxResult(BaseModel):
    """Result of sandbox code execution.

    Attributes:
        success: Whether execution succeeded
        stdout: Standard output captured
        stderr: Standard error captured
        return_value: Captured return value (if any)
        execution_time: Time taken in seconds
        error_type: Type of error if failed
        error_message: Error message if failed
    """

    success: bool = Field(..., description="Whether execution succeeded")
    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error")
    return_value: Optional[Any] = Field(default=None, description="Return value")
    execution_time: float = Field(default=0.0, description="Execution time (seconds)")
    error_type: Optional[str] = Field(default=None, description="Error type")
    error_message: Optional[str] = Field(default=None, description="Error message")

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class SandboxExecutor:
    """Secure Python code execution sandbox.

    Features:
    - Subprocess isolation
    - Timeout protection
    - Output capture and truncation
    - Security validation
    - Return value extraction
    - Test case execution

    Follows CODE_CONSTITUTION: Safety First
    """

    def __init__(self, config: ToolFactoryConfig):
        """Initialize sandbox executor.

        Args:
            config: Tool factory configuration with sandbox settings
        """
        self.config = config
        self.execution_history: List[SandboxResult] = []

    async def execute(
        self,
        code: str,
        timeout: Optional[float] = None,
        capture_return: bool = True,
    ) -> SandboxResult:
        """Execute Python code in isolated sandbox.

        Args:
            code: Python code to execute
            timeout: Execution timeout (uses config default if None)
            capture_return: Whether to capture last expression value

        Returns:
            SandboxResult with execution details
        """
        timeout = timeout or self.config.sandbox_timeout
        start_time = datetime.now()

        # Validate security
        validation_error = self._validate_security(code)
        if validation_error:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=validation_error,
                error_type="SecurityError",
                error_message=validation_error,
            )

        # Wrap code to capture return value
        if capture_return:
            code = self._wrap_for_return(code)

        # Execute in temporary file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tempfile.gettempdir(),
            )

            try:
                # Execute with timeout
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )

                stdout = stdout_bytes.decode("utf-8", errors="replace")
                stderr = stderr_bytes.decode("utf-8", errors="replace")

                # Truncate if too long
                max_size = self.config.max_output_size
                if len(stdout) > max_size:
                    stdout = stdout[:max_size] + "\n...[truncated]"
                if len(stderr) > max_size:
                    stderr = stderr[:max_size] + "\n...[truncated]"

                # Extract return value
                return_value = None
                if capture_return and "__SANDBOX_RETURN__:" in stdout:
                    return_value = self._extract_return_value(stdout)
                    # Remove marker from output
                    stdout = "\n".join(
                        line
                        for line in stdout.split("\n")
                        if "__SANDBOX_RETURN__:" not in line
                    ).strip()

                execution_time = (datetime.now() - start_time).total_seconds()

                result = SandboxResult(
                    success=process.returncode == 0,
                    stdout=stdout,
                    stderr=stderr,
                    return_value=return_value,
                    execution_time=execution_time,
                    error_type="RuntimeError" if process.returncode != 0 else None,
                    error_message=stderr if process.returncode != 0 else None,
                )

            except asyncio.TimeoutError:
                # Kill timed-out process
                process.kill()
                await process.wait()

                result = SandboxResult(
                    success=False,
                    stdout="",
                    stderr=f"Execution timed out after {timeout} seconds",
                    execution_time=timeout,
                    error_type="TimeoutError",
                    error_message=f"Code execution exceeded {timeout}s limit",
                )

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except OSError:
                pass

        self.execution_history.append(result)
        return result

    async def execute_function(
        self,
        func_code: str,
        func_name: str,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> SandboxResult:
        """Execute a specific function with arguments.

        Args:
            func_code: Function definition code
            func_name: Name of function to call
            args: Positional arguments
            kwargs: Keyword arguments
            timeout: Execution timeout

        Returns:
            SandboxResult with function return value
        """
        kwargs = kwargs or {}

        # Build function call
        args_repr = ", ".join(repr(arg) for arg in args)
        kwargs_repr = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
        call_args = ", ".join(filter(None, [args_repr, kwargs_repr]))

        # Build execution code
        execution_code = f"""{func_code}

# Execute function
import json as _json
__result__ = {func_name}({call_args})
print(f"__SANDBOX_RETURN__:{{_json.dumps(__result__)}}")
"""

        return await self.execute(
            execution_code,
            timeout=timeout,
            capture_return=True,
        )

    async def test_code(
        self,
        code: str,
        test_cases: List[Dict[str, Any]],
        function_name: str = "test_function",
    ) -> Dict[str, Any]:
        """Test code against multiple test cases.

        Args:
            code: Function code to test
            test_cases: List of test cases with "input" and "expected" keys
            function_name: Name of function to test

        Returns:
            Dictionary with pass/fail statistics and detailed results
        """
        results = []
        passed = 0
        failed = 0

        for i, test in enumerate(test_cases):
            test_input = test.get("input", {})
            expected = test.get("expected")

            # Build test code
            test_code = f"""{code}

# Test case {i + 1}
import json as _json
__input__ = {repr(test_input)}
__expected__ = {repr(expected)}

# Call function
if isinstance(__input__, dict):
    __result__ = {function_name}(**__input__)
else:
    __result__ = {function_name}(__input__)

# Check result
__passed__ = __result__ == __expected__
print(f"__SANDBOX_RETURN__:{{_json.dumps({{'passed': __passed__, 'result': __result__, 'expected': __expected__}})}}")
"""

            result = await self.execute(test_code, capture_return=True)

            if result.success and result.return_value:
                test_passed = result.return_value.get("passed", False)
                if test_passed:
                    passed += 1
                else:
                    failed += 1

                results.append(
                    {
                        "test_case": i + 1,
                        "passed": test_passed,
                        "result": result.return_value.get("result"),
                        "expected": result.return_value.get("expected"),
                    }
                )
            else:
                failed += 1
                results.append(
                    {
                        "test_case": i + 1,
                        "passed": False,
                        "error": result.stderr or result.error_message,
                    }
                )

        total = len(test_cases)
        return {
            "passed": passed,
            "failed": failed,
            "total": total,
            "success_rate": passed / max(total, 1),
            "results": results,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics.

        Returns:
            Dictionary with execution statistics
        """
        if not self.execution_history:
            return {
                "total": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
            }

        total = len(self.execution_history)
        successes = sum(1 for r in self.execution_history if r.success)
        avg_time = sum(r.execution_time for r in self.execution_history) / total

        return {
            "total": total,
            "successes": successes,
            "failures": total - successes,
            "success_rate": successes / total,
            "avg_execution_time": avg_time,
        }

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()

    def _validate_security(self, code: str) -> Optional[str]:
        """Validate code for security issues.

        Args:
            code: Python code to validate

        Returns:
            Error message if validation fails, None if OK
        """
        import ast

        # Parse code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return f"Syntax error: {e}"

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
                    if node.func.id in ["eval", "exec", "compile", "__import__"]:
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

    def _wrap_for_return(self, code: str) -> str:
        """Wrap code to capture last expression value.

        Args:
            code: Python code

        Returns:
            Wrapped code with return value capture
        """
        import ast

        # Already wrapped
        if "__SANDBOX_RETURN__" in code:
            return code

        # Parse code
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code  # Will fail during execution

        # Check if last statement is an expression
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last_expr = ast.unparse(tree.body[-1].value)
            code_without_last = "\n".join(code.rsplit("\n", 1)[:-1])

            wrapped = f"""{code_without_last}

__result__ = {last_expr}
import json as _json
print(f"__SANDBOX_RETURN__:{{_json.dumps(__result__)}}")
"""
            return wrapped

        return code

    def _extract_return_value(self, stdout: str) -> Optional[Any]:
        """Extract return value from stdout.

        Args:
            stdout: Standard output containing __SANDBOX_RETURN__ marker

        Returns:
            Extracted return value or None
        """
        try:
            # Find marker line
            for line in stdout.split("\n"):
                if "__SANDBOX_RETURN__:" in line:
                    json_str = line.split("__SANDBOX_RETURN__:")[1].strip()
                    return json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            pass

        return None
