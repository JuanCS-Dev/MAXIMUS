"""
Tests for SandboxExecutor
=========================

Tests for secure code execution, timeout handling, and test running.

Follows CODE_CONSTITUTION: ≥80% coverage, clear test names.
"""

from __future__ import annotations

import pytest

from config import ToolFactoryConfig
from core.sandbox import SandboxExecutor, SandboxResult


@pytest.fixture
def sandbox():
    """Create SandboxExecutor instance."""
    config = ToolFactoryConfig()
    return SandboxExecutor(config)


@pytest.mark.asyncio
class TestBasicExecution:
    """Tests for basic code execution."""

    async def test_execute_simple_code(self, sandbox):
        """Execute simple Python code."""
        code = "print('Hello, World!')"
        result = await sandbox.execute(code, capture_return=False)

        assert result.success is True
        assert "Hello, World!" in result.stdout
        assert result.stderr == ""

    async def test_execute_with_return_value(self, sandbox):
        """Execute code and capture return value."""
        code = "42"
        result = await sandbox.execute(code, capture_return=True)

        assert result.success is True
        assert result.return_value == 42

    async def test_execute_syntax_error(self, sandbox):
        """Syntax error should be caught."""
        code = "def add(a b):  # Missing comma"
        result = await sandbox.execute(code)

        assert result.success is False
        assert result.error_type == "SecurityError"
        assert "Syntax error" in result.stderr


@pytest.mark.asyncio
class TestSecurity:
    """Tests for security validation."""

    async def test_blocked_import(self, sandbox):
        """Blocked imports should fail."""
        code = """
import subprocess
subprocess.run(['ls'])
"""
        result = await sandbox.execute(code)

        assert result.success is False
        assert result.error_type == "SecurityError"
        assert "Blocked import" in result.stderr

    async def test_dangerous_builtin(self, sandbox):
        """Dangerous builtins should be blocked."""
        code = "eval('1 + 1')"
        result = await sandbox.execute(code)

        assert result.success is False
        assert "Dangerous builtin" in result.stderr

    async def test_file_write_blocked(self, sandbox):
        """File write operations should be blocked."""
        code = """
with open('test.txt', 'w') as f:
    f.write('data')
"""
        result = await sandbox.execute(code)

        assert result.success is False
        assert "write" in result.stderr.lower()


@pytest.mark.asyncio
class TestTimeout:
    """Tests for timeout handling."""

    async def test_timeout_execution(self, sandbox):
        """Long-running code should timeout."""
        code = """
import time
time.sleep(100)
"""
        result = await sandbox.execute(code, timeout=0.5)

        assert result.success is False
        assert result.error_type == "TimeoutError"
        assert "timed out" in result.stderr


@pytest.mark.asyncio
class TestFunctionExecution:
    """Tests for function execution."""

    async def test_execute_function_with_args(self, sandbox):
        """Execute function with positional arguments."""
        code = """
def add(a: int, b: int) -> int:
    return a + b
"""
        result = await sandbox.execute_function(code, "add", args=(2, 3))

        assert result.success is True
        assert result.return_value == 5

    async def test_execute_function_with_kwargs(self, sandbox):
        """Execute function with keyword arguments."""
        code = """
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"
"""
        result = await sandbox.execute_function(
            code,
            "greet",
            kwargs={"name": "Alice", "greeting": "Hi"},
        )

        assert result.success is True
        assert result.return_value == "Hi, Alice!"


@pytest.mark.asyncio
class TestCodeTesting:
    """Tests for test_code functionality."""

    async def test_all_pass(self, sandbox):
        """All tests passing."""
        code = """
def double(x: int) -> int:
    return x * 2
"""
        test_cases = [
            {"input": {"x": 2}, "expected": 4},
            {"input": {"x": 5}, "expected": 10},
            {"input": {"x": 0}, "expected": 0},
        ]

        results = await sandbox.test_code(code, test_cases, "double")

        assert results["passed"] == 3
        assert results["failed"] == 0
        assert results["success_rate"] == 1.0

    async def test_some_fail(self, sandbox):
        """Some tests failing."""
        code = """
def buggy(x: int) -> int:
    if x > 0:
        return x * 2
    return x  # Bug: should be x * 2
"""
        test_cases = [
            {"input": {"x": 2}, "expected": 4},
            {"input": {"x": -1}, "expected": -2},
        ]

        results = await sandbox.test_code(code, test_cases, "buggy")

        assert results["passed"] == 1
        assert results["failed"] == 1
        assert results["success_rate"] == 0.5

    async def test_runtime_error(self, sandbox):
        """Runtime error in test."""
        code = """
def divide(a: int, b: int) -> float:
    return a / b
"""
        test_cases = [
            {"input": {"a": 10, "b": 0}, "expected": None},
        ]

        results = await sandbox.test_code(code, test_cases, "divide")

        assert results["passed"] == 0
        assert results["failed"] == 1
        assert len(results["results"]) == 1
        assert "error" in results["results"][0]


@pytest.mark.asyncio
class TestStats:
    """Tests for execution statistics."""

    async def test_empty_stats(self, sandbox):
        """Stats for empty history."""
        stats = sandbox.get_stats()

        assert stats["total"] == 0
        assert stats["success_rate"] == 0.0

    async def test_stats_tracking(self, sandbox):
        """Stats should track executions."""
        # Execute some code
        await sandbox.execute("print('test')")
        await sandbox.execute("42")

        stats = sandbox.get_stats()

        assert stats["total"] == 2
        assert "success_rate" in stats
        assert "avg_execution_time" in stats
        assert stats["successes"] >= 1

    async def test_clear_history(self, sandbox):
        """Clear history."""
        await sandbox.execute("print('test')")
        sandbox.clear_history()

        stats = sandbox.get_stats()
        assert stats["total"] == 0
