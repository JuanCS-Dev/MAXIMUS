"""
Tests for ToolFactory
=====================

Scientific tests validating real-world usage patterns.

Test Philosophy:
- Arrange-Act-Assert pattern
- Each test has explicit hypothesis
- Focus on integration over mocking
- Test edge cases and failure modes

Follows CODE_CONSTITUTION: ≥80% coverage, realistic scenarios
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import ToolFactoryConfig
from core.factory import ToolFactory, ToolGenerationError
from models.tool_spec import ToolGenerateRequest, ToolSpec


@pytest.fixture
def config():
    """Create test configuration."""
    return ToolFactoryConfig(
        gemini_api_key="test-key",
        gemini_model="gemini-3-pro-preview",
        sandbox_timeout=5.0,
        success_rate_threshold=0.8,
    )


@pytest.fixture
def mock_llm_response():
    """Create mock LLM response with valid code."""
    mock_response = MagicMock()
    mock_response.text = """
Here's the function:

```python
def double(x: int) -> int:
    \"\"\"Double a number.

    Args:
        x: Number to double

    Returns:
        Doubled number
    \"\"\"
    return x * 2
```
"""
    return mock_response


@pytest.fixture
def mock_llm_buggy_response():
    """Create mock LLM response with buggy code."""
    mock_response = MagicMock()
    mock_response.text = """
```python
def buggy_double(x: int) -> int:
    \"\"\"Double a number (but has bug).\"\"\"
    if x > 0:
        return x * 2
    return x  # BUG: should be x * 2
```
"""
    return mock_response


@pytest.fixture
def mock_llm_fixed_response():
    """Create mock LLM response with fixed code."""
    mock_response = MagicMock()
    mock_response.text = """
```python
def buggy_double(x: int) -> int:
    \"\"\"Double a number (fixed).\"\"\"
    return x * 2
```
"""
    return mock_response


@pytest.mark.asyncio
class TestToolGenerationEndToEnd:
    """Test complete tool generation flow (most critical path)."""

    async def test_generate_simple_tool_success(
        self, config, mock_llm_response
    ):
        """
        HYPOTHESIS: Factory can generate a working tool from description.

        This is the PRIMARY use case - user describes what they want,
        system generates working code.
        """
        # Arrange: Create factory and request
        factory = ToolFactory(config)
        request = ToolGenerateRequest(
            name="double",
            description="Double a number",
            examples=[
                {"input": {"x": 2}, "expected": 4},
                {"input": {"x": 5}, "expected": 10},
                {"input": {"x": 0}, "expected": 0},
            ],
        )

        # Mock LLM
        with patch.object(
            factory.llm, "generate_content_async", return_value=mock_llm_response
        ):
            # Act: Generate tool
            result = await factory.generate_tool(request)

        # Assert: Tool generated successfully
        assert isinstance(result, ToolSpec)
        assert result.name == "double"
        assert result.success_rate >= 0.8
        assert "def double" in result.code
        assert result.version == 1

        # Verify tool registered
        assert factory.get_tool_spec("double") == result

    async def test_generate_tool_with_iterative_improvement(
        self, config, mock_llm_buggy_response, mock_llm_fixed_response
    ):
        """
        HYPOTHESIS: Factory can fix buggy tools through iteration.

        Real scenario: LLM generates buggy code initially,
        system detects failures and improves it.
        """
        # Arrange
        factory = ToolFactory(config)
        request = ToolGenerateRequest(
            name="buggy_double",
            description="Double a number",
            examples=[
                {"input": {"x": 2}, "expected": 4},
                {"input": {"x": -1}, "expected": -2},  # Will fail initially
            ],
        )

        # Mock LLM: first buggy, then fixed
        with patch.object(
            factory.llm,
            "generate_content_async",
            side_effect=[mock_llm_buggy_response, mock_llm_fixed_response],
        ):
            # Act: Generate (should trigger improvement)
            result = await factory.generate_tool(request, max_attempts=2)

        # Assert: Tool fixed after iteration
        assert result.success_rate >= 0.8
        assert result.version == 2  # Version incremented
        assert "return x * 2" in result.code

    async def test_generate_fails_after_max_attempts(
        self, config, mock_llm_buggy_response
    ):
        """
        HYPOTHESIS: Factory fails gracefully when unable to fix bugs.

        Edge case: LLM keeps generating broken code.
        System should raise clear error, not hang.
        """
        # Arrange
        factory = ToolFactory(config)
        request = ToolGenerateRequest(
            name="always_buggy",
            description="Double a number",
            examples=[
                {"input": {"x": -1}, "expected": -2},
            ],
        )

        # Mock LLM: always returns buggy code
        with patch.object(
            factory.llm,
            "generate_content_async",
            return_value=mock_llm_buggy_response,
        ):
            # Act & Assert: Should raise after max attempts
            with pytest.raises(
                ToolGenerationError, match="Failed after .* attempts"
            ):
                await factory.generate_tool(request, max_attempts=2)


@pytest.mark.asyncio
class TestSecurityValidation:
    """Test security enforcement (critical for safety)."""

    async def test_blocks_dangerous_imports(self, config):
        """
        HYPOTHESIS: System blocks tools with dangerous imports.

        Security test: subprocess import should be blocked.
        """
        # Arrange
        factory = ToolFactory(config)
        mock_response = MagicMock()
        mock_response.text = """
```python
import subprocess

def dangerous():
    subprocess.run(['ls'])
```
"""
        request = ToolGenerateRequest(
            name="dangerous",
            description="Dangerous function",
            examples=[{"input": {}, "expected": None}],
        )

        # Act & Assert
        with patch.object(
            factory.llm, "generate_content_async", return_value=mock_response
        ):
            with pytest.raises(ToolGenerationError, match="Security"):
                await factory.generate_tool(request)

    async def test_blocks_eval_builtin(self, config):
        """
        HYPOTHESIS: System blocks tools using eval().

        Security test: eval() is dangerous and should be blocked.
        """
        # Arrange
        factory = ToolFactory(config)
        mock_response = MagicMock()
        mock_response.text = """
```python
def evil():
    eval("1 + 1")
```
"""
        request = ToolGenerateRequest(
            name="evil",
            description="Evil function",
            examples=[{"input": {}, "expected": None}],
        )

        # Act & Assert
        with patch.object(
            factory.llm, "generate_content_async", return_value=mock_response
        ):
            with pytest.raises(ToolGenerationError, match="Security"):
                await factory.generate_tool(request)

    async def test_allows_safe_imports(self, config, mock_llm_response):
        """
        HYPOTHESIS: System allows safe stdlib imports (json, re, etc).

        Positive test: json import should work.
        """
        # Arrange
        factory = ToolFactory(config)
        safe_response = MagicMock()
        safe_response.text = """
```python
import json

def safe_json(data: dict) -> str:
    \"\"\"Convert dict to JSON.\"\"\"
    return json.dumps(data)
```
"""
        request = ToolGenerateRequest(
            name="safe_json",
            description="Convert to JSON",
            examples=[
                {"input": {"data": {"a": 1}}, "expected": '{"a": 1}'},
            ],
        )

        # Act
        with patch.object(
            factory.llm, "generate_content_async", return_value=safe_response
        ):
            result = await factory.generate_tool(request)

        # Assert: Should succeed
        assert result.name == "safe_json"
        assert "import json" in result.code


@pytest.mark.asyncio
class TestRegistryOperations:
    """Test tool registry management."""

    async def test_list_tools_empty(self, config):
        """
        HYPOTHESIS: Empty registry returns empty list.
        """
        # Arrange
        factory = ToolFactory(config)

        # Act
        tools = factory.list_tools()

        # Assert
        assert tools == []

    async def test_list_tools_after_generation(
        self, config, mock_llm_response
    ):
        """
        HYPOTHESIS: Generated tools appear in registry listing.
        """
        # Arrange
        factory = ToolFactory(config)
        request = ToolGenerateRequest(
            name="test_tool",
            description="Test tool",
            examples=[{"input": {"x": 1}, "expected": 2}],
        )

        with patch.object(
            factory.llm, "generate_content_async", return_value=mock_llm_response
        ):
            await factory.generate_tool(request)

        # Act
        tools = factory.list_tools()

        # Assert
        assert len(tools) == 1
        assert tools[0]["name"] == "double"  # Name from mock_llm_response

    async def test_get_tool_spec_not_found(self, config):
        """
        HYPOTHESIS: Getting non-existent tool returns None.
        """
        # Arrange
        factory = ToolFactory(config)

        # Act
        spec = factory.get_tool_spec("nonexistent")

        # Assert
        assert spec is None

    async def test_remove_tool(self, config, mock_llm_response):
        """
        HYPOTHESIS: Removed tools no longer in registry.
        """
        # Arrange
        factory = ToolFactory(config)
        request = ToolGenerateRequest(
            name="to_remove",
            description="Tool to remove",
            examples=[{"input": {"x": 1}, "expected": 2}],
        )

        with patch.object(
            factory.llm, "generate_content_async", return_value=mock_llm_response
        ):
            result = await factory.generate_tool(request)

        tool_name = result.name

        # Act
        removed = factory.remove_tool(tool_name)

        # Assert
        assert removed is True
        assert factory.get_tool_spec(tool_name) is None
        assert len(factory.list_tools()) == 0

    async def test_remove_nonexistent_tool(self, config):
        """
        HYPOTHESIS: Removing non-existent tool returns False.
        """
        # Arrange
        factory = ToolFactory(config)

        # Act
        removed = factory.remove_tool("nonexistent")

        # Assert
        assert removed is False


@pytest.mark.asyncio
class TestExportImport:
    """Test tool persistence (export/import)."""

    async def test_export_empty(self, config):
        """
        HYPOTHESIS: Exporting empty registry returns empty dict.
        """
        # Arrange
        factory = ToolFactory(config)

        # Act
        exported = factory.export_tools()

        # Assert
        assert exported == {}

    async def test_export_import_roundtrip(
        self, config, mock_llm_response
    ):
        """
        HYPOTHESIS: Exported tools can be imported back exactly.

        Real scenario: Save tools to disk, restart service,
        load tools back.
        """
        # Arrange: Generate tool
        factory1 = ToolFactory(config)
        request = ToolGenerateRequest(
            name="export_test",
            description="Test export",
            examples=[{"input": {"x": 1}, "expected": 2}],
        )

        with patch.object(
            factory1.llm, "generate_content_async", return_value=mock_llm_response
        ):
            original = await factory1.generate_tool(request)

        # Act: Export
        exported = factory1.export_tools()

        # Create new factory and import
        factory2 = ToolFactory(config)
        factory2.import_tools(exported)

        # Assert: Tool preserved
        imported = factory2.get_tool_spec(original.name)
        assert imported is not None
        assert imported.name == original.name
        assert imported.code == original.code
        assert imported.success_rate == original.success_rate


@pytest.mark.asyncio
class TestStatistics:
    """Test statistics tracking."""

    async def test_stats_empty_factory(self, config):
        """
        HYPOTHESIS: New factory has zero stats.
        """
        # Arrange
        factory = ToolFactory(config)

        # Act
        stats = factory.get_stats()

        # Assert
        assert stats["generated_tools"] == 0
        assert stats["total_generations"] == 0
        assert stats["successful_generations"] == 0
        assert stats["total_tool_uses"] == 0

    async def test_stats_after_successful_generation(
        self, config, mock_llm_response
    ):
        """
        HYPOTHESIS: Stats track successful generations.
        """
        # Arrange
        factory = ToolFactory(config)
        request = ToolGenerateRequest(
            name="stats_test",
            description="Test stats",
            examples=[{"input": {"x": 1}, "expected": 2}],
        )

        with patch.object(
            factory.llm, "generate_content_async", return_value=mock_llm_response
        ):
            await factory.generate_tool(request)

        # Act
        stats = factory.get_stats()

        # Assert
        assert stats["generated_tools"] == 1
        assert stats["total_generations"] == 1
        assert stats["successful_generations"] == 1
        assert stats["average_success_rate"] > 0

    async def test_stats_after_failed_generation(
        self, config, mock_llm_buggy_response
    ):
        """
        HYPOTHESIS: Stats track failed generation attempts.
        """
        # Arrange
        factory = ToolFactory(config)
        request = ToolGenerateRequest(
            name="fail_test",
            description="Test failure",
            examples=[{"input": {"x": -1}, "expected": -2}],
        )

        # Act: Try to generate (will fail)
        with patch.object(
            factory.llm,
            "generate_content_async",
            return_value=mock_llm_buggy_response,
        ):
            try:
                await factory.generate_tool(request, max_attempts=1)
            except ToolGenerationError:
                pass  # Expected

        # Assert: Failed attempt logged
        stats = factory.get_stats()
        assert stats["total_generations"] == 1
        assert stats["successful_generations"] == 0


@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    async def test_tool_exceeds_line_limit(self, config):
        """
        HYPOTHESIS: System rejects tools exceeding line limit.
        """
        # Arrange
        factory = ToolFactory(config)
        huge_response = MagicMock()
        # Generate code with 150 lines (exceeds 100 line limit)
        huge_code = "\n".join([f"    # Line {i}" for i in range(150)])
        huge_response.text = f"""
```python
def huge():
    \"\"\"Huge function.\"\"\"
{huge_code}
    return None
```
"""
        request = ToolGenerateRequest(
            name="huge",
            description="Huge function",
            examples=[{"input": {}, "expected": None}],
        )

        # Act & Assert
        with patch.object(
            factory.llm, "generate_content_async", return_value=huge_response
        ):
            with pytest.raises(ToolGenerationError, match="exceeds.*lines"):
                await factory.generate_tool(request)

    async def test_syntax_error_in_generated_code(self, config):
        """
        HYPOTHESIS: System attempts to fix syntax errors.
        """
        # Arrange
        factory = ToolFactory(config)
        syntax_error_response = MagicMock()
        syntax_error_response.text = """
```python
def broken(a b):  # Missing comma
    return a + b
```
"""
        fixed_response = MagicMock()
        fixed_response.text = """
```python
def broken(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b
```
"""
        request = ToolGenerateRequest(
            name="broken",
            description="Add two numbers",
            examples=[{"input": {"a": 1, "b": 2}, "expected": 3}],
        )

        # Act: First returns syntax error, then fix
        with patch.object(
            factory.llm,
            "generate_content_async",
            side_effect=[syntax_error_response, fixed_response],
        ):
            result = await factory.generate_tool(request)

        # Assert: Fixed version used
        assert "def broken(a: int, b: int)" in result.code
