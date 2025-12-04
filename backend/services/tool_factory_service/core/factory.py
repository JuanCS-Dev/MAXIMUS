"""
Tool Factory
============

Automatic tool generation using LLM + validation + sandbox testing.

Inspired by AutoTools (arXiv:2405.16533) - LLMs automate tool creation.

Process:
1. LLM generates code from description
2. Validator checks syntax and security
3. Sandbox tests against examples
4. Iterative improvement if needed
5. Registry for reuse

Follows CODE_CONSTITUTION: Safety First, Clarity Over Cleverness
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from config import ToolFactoryConfig
from models.tool_spec import ToolGenerateRequest, ToolSpec

from .prompts import (
    build_generation_prompt,
    build_improvement_prompt,
    build_syntax_fix_prompt,
)
from .sandbox import SandboxExecutor
from .validator import ToolValidator


class ToolGenerationError(Exception):
    """Error during tool generation process."""


class ToolFactory:
    """Automatic tool factory for dynamic tool generation.

    Features:
    - LLM-based code generation
    - Security validation
    - Sandbox testing
    - Iterative improvement
    - Tool registry and persistence

    Follows CODE_CONSTITUTION pillars
    """

    def __init__(self, config: ToolFactoryConfig):
        """Initialize tool factory.

        Args:
            config: Tool factory configuration
        """
        self.config = config
        self.validator = ToolValidator(config)
        self.sandbox = SandboxExecutor(config)

        # Registry
        self.generated_tools: Dict[str, ToolSpec] = {}
        self.generation_history: List[Dict[str, Any]] = []

        # Initialize Gemini
        genai.configure(api_key=config.gemini_api_key)
        self.llm = genai.GenerativeModel(
            model_name=config.gemini_model,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 4096,
            },
        )

    async def generate_tool(
        self,
        request: ToolGenerateRequest,
        max_attempts: int = 3,
    ) -> ToolSpec:
        """Generate a new tool from description and examples.

        Args:
            request: Tool generation request with description and examples
            max_attempts: Maximum improvement attempts

        Returns:
            Generated and validated ToolSpec

        Raises:
            ToolGenerationError: If generation fails after max attempts
        """
        # Generate initial code
        code = await self._generate_code(request)

        # Extract metadata
        name, params, ret_type, doc = self.validator.parse_function_metadata(code)

        # Use requested name if provided
        if request.name and request.name != name:
            code = code.replace(f"def {name}", f"def {request.name}")
            name = request.name

        # Create spec
        spec = ToolSpec(
            name=name,
            description=doc or request.description,
            parameters=params,
            return_type=ret_type,
            code=code,
            examples=request.examples,
        )

        # Test the tool
        test_results = await self._test_tool(spec, request.examples)

        # Check if passes threshold
        if test_results["success_rate"] >= self.config.success_rate_threshold:
            return self._register_tool(spec, test_results)

        # Iterative improvement
        for _ in range(max_attempts - 1):
            improved_code = await self._improve_tool(spec, test_results["failures"], request)

            if improved_code:
                spec.code = improved_code
                spec.version += 1
                test_results = await self._test_tool(spec, request.examples)

                if test_results["success_rate"] >= self.config.success_rate_threshold:
                    return self._register_tool(spec, test_results)

        # Failed after all attempts
        self._log_generation(spec, test_results, success=False)
        raise ToolGenerationError(
            f"Failed after {max_attempts} attempts. "
            f"Rate: {test_results['success_rate']:.2%}"
        )

    async def _generate_code(self, request: ToolGenerateRequest) -> str:
        """Generate Python code using LLM.

        Args:
            request: Tool generation request

        Returns:
            Generated Python code

        Raises:
            ToolGenerationError: If generation or validation fails
        """
        # Build prompt
        examples_text = self._format_examples(request.examples)
        prompt = build_generation_prompt(
            description=request.description,
            function_name=request.name,
            examples_text=examples_text,
            allowed_imports=self.config.allowed_imports,
            max_lines=self.config.max_tool_size_lines,
        )

        # Generate code
        response = await self.llm.generate_content_async(prompt)
        code = self.validator.extract_code_from_markdown(response.text)

        # Validate syntax
        if not self.validator.validate_syntax(code):
            code = await self._fix_syntax_errors(code)

        # Validate security
        security_error = self.validator.validate_security(code)
        if security_error:
            raise ToolGenerationError(f"Security error: {security_error}")

        # Validate line count
        if not self.validator.check_line_count(code):
            raise ToolGenerationError(f"Exceeds {self.config.max_tool_size_lines} lines")

        return code

    async def _test_tool(
        self,
        spec: ToolSpec,
        examples: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Test tool against examples in sandbox.

        Args:
            spec: Tool specification
            examples: Test examples

        Returns:
            Test results with success_rate, passed, failed, failures
        """
        test_cases = [
            {"input": ex.get("input", {}), "expected": ex.get("expected")}
            for ex in examples
        ]

        results = await self.sandbox.test_code(spec.code, test_cases, spec.name)

        return {
            "success_rate": results["success_rate"],
            "passed": results["passed"],
            "failed": results["failed"],
            "total": results["total"],
            "failures": [r for r in results["results"] if not r.get("passed", False)],
        }

    async def _improve_tool(
        self,
        spec: ToolSpec,
        failures: List[Dict[str, Any]],
        request: ToolGenerateRequest,
    ) -> Optional[str]:
        """Improve tool code based on test failures.

        Args:
            spec: Current tool specification
            failures: Failed test cases
            request: Original generation request

        Returns:
            Improved code or None
        """
        # Format failures
        failures_text = "\n".join(
            f"Test {f.get('test_case', '?')}: "
            f"Input={f.get('input')}, Expected={f.get('expected')}, "
            f"Got={f.get('result', 'N/A')}, Error={f.get('error', 'None')}"
            for f in failures[:5]
        )

        # Build prompt
        prompt = build_improvement_prompt(
            code=spec.code,
            function_name=spec.name,
            failures_text=failures_text,
            description=request.description,
            allowed_imports=self.config.allowed_imports,
        )

        try:
            response = await self.llm.generate_content_async(prompt)
            improved_code = self.validator.extract_code_from_markdown(response.text)

            # Validate
            if not self.validator.validate_syntax(improved_code):
                return None
            if self.validator.validate_security(improved_code):
                return None

            return improved_code

        except Exception:
            return None

    async def _fix_syntax_errors(self, code: str) -> str:
        """Fix syntax errors in code.

        Args:
            code: Code with syntax errors

        Returns:
            Fixed code (or original if fix fails)
        """
        import ast

        try:
            ast.parse(code)
            return code
        except SyntaxError as e:
            error_msg = str(e)

        prompt = build_syntax_fix_prompt(code, error_msg)

        try:
            response = await self.llm.generate_content_async(prompt)
            fixed = self.validator.extract_code_from_markdown(response.text)

            if self.validator.validate_syntax(fixed):
                return fixed

        except Exception:
            pass

        return code

    def _register_tool(self, spec: ToolSpec, test_results: Dict[str, Any]) -> ToolSpec:
        """Register successful tool.

        Args:
            spec: Tool specification
            test_results: Test results

        Returns:
            Registered tool spec
        """
        spec.success_rate = test_results["success_rate"]
        self.generated_tools[spec.name] = spec
        self._log_generation(spec, test_results, success=True)
        return spec

    def get_tool_spec(self, name: str) -> Optional[ToolSpec]:
        """Get tool specification by name.

        Args:
            name: Tool name

        Returns:
            Tool spec or None
        """
        return self.generated_tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all generated tools.

        Returns:
            List of tool summaries
        """
        return [
            {
                "name": s.name,
                "description": s.description,
                "success_rate": s.success_rate,
                "usage_count": s.usage_count,
                "version": s.version,
                "parameters": list(s.parameters.keys()),
            }
            for s in self.generated_tools.values()
        ]

    def remove_tool(self, name: str) -> bool:
        """Remove tool from registry.

        Args:
            name: Tool name

        Returns:
            True if removed
        """
        if name in self.generated_tools:
            del self.generated_tools[name]
            return True
        return False

    def export_tools(self) -> Dict[str, Any]:
        """Export all tools.

        Returns:
            Tool data dictionary
        """
        return {
            name: {
                "name": s.name,
                "description": s.description,
                "parameters": s.parameters,
                "return_type": s.return_type,
                "code": s.code,
                "examples": s.examples,
                "success_rate": s.success_rate,
                "usage_count": s.usage_count,
                "version": s.version,
            }
            for name, s in self.generated_tools.items()
        }

    def import_tools(self, data: Dict[str, Any]) -> None:
        """Import exported tools.

        Args:
            data: Exported tool data
        """
        for name, td in data.items():
            spec = ToolSpec(
                name=td["name"],
                description=td["description"],
                parameters=td["parameters"],
                return_type=td["return_type"],
                code=td["code"],
                examples=td.get("examples", []),
                success_rate=td.get("success_rate", 0.0),
                usage_count=td.get("usage_count", 0),
                version=td.get("version", 1),
            )
            self.generated_tools[name] = spec

    def get_stats(self) -> Dict[str, Any]:
        """Get factory statistics.

        Returns:
            Statistics dictionary
        """
        tools = list(self.generated_tools.values())
        return {
            "generated_tools": len(tools),
            "total_generations": len(self.generation_history),
            "successful_generations": sum(1 for h in self.generation_history if h["success"]),
            "total_tool_uses": sum(s.usage_count for s in tools),
            "average_success_rate": sum(s.success_rate for s in tools) / max(len(tools), 1),
        }

    def _format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples for prompt.

        Args:
            examples: Examples list

        Returns:
            Formatted string
        """
        lines = []
        for i, ex in enumerate(examples, 1):
            inp = ex.get("input", {})
            exp = ex.get("expected")
            lines.append(f"  Example {i}: {inp!r} -> {exp!r}")
        return "\n".join(lines)

    def _log_generation(
        self,
        spec: ToolSpec,
        test_results: Dict[str, Any],
        success: bool,
    ) -> None:
        """Log generation attempt.

        Args:
            spec: Tool specification
            test_results: Test results
            success: Success flag
        """
        self.generation_history.append(
            {
                "tool_name": spec.name,
                "success": success,
                "success_rate": test_results.get("success_rate", 0.0),
                "passed": test_results.get("passed", 0),
                "failed": test_results.get("failed", 0),
                "timestamp": datetime.now().isoformat(),
                "version": spec.version,
            }
        )
