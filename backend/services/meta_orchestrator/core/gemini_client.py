"""
Gemini 3 Pro Client - LLM Interface for World Model
====================================================

Async client for Google Gemini 3 Pro API used in SimuRA world model predictions.
Implements Dyna-Think style reasoning with state simulation.

Based on:
- Gemini 3 Pro API (December 2025)
- Dyna-Think: Reasoning + Acting + World Model simulation
- SimuRA: Simulative Reasoning Architecture

Gemini 3 Pro Features:
- 1M token context window
- thinking_level parameter for reasoning depth
- thought_signatures for multi-turn reasoning
- media_resolution for multimodal inputs
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GeminiConfig(BaseModel):
    """Configuration for Gemini 3 Pro client."""

    api_key: str = Field(..., description="Gemini API key from Google AI Studio")
    model: str = Field(
        default="gemini-3-pro-preview",
        description="Model ID (gemini-3-pro-preview or gemini-3-pro-image-preview)"
    )
    thinking_level: str = Field(
        default="high",
        description="Reasoning depth: 'low' for speed, 'high' for complex analysis"
    )
    max_output_tokens: int = Field(default=8192, ge=1, le=65536)
    timeout_seconds: int = Field(default=60, ge=1, le=300)
    use_thought_signatures: bool = Field(
        default=True,
        description="Enable thought signatures for multi-turn reasoning"
    )


class SimulationPrediction(BaseModel):
    """Structured prediction from Gemini 3 Pro."""

    predicted_state: Dict[str, Any] = Field(
        default_factory=dict,
        description="Predicted next state"
    )
    success_probability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Probability of success"
    )
    outcome: str = Field(
        default="unknown",
        description="Predicted outcome type"
    )
    reasoning: str = Field(
        default="",
        description="Chain-of-thought reasoning from Gemini 3"
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence in prediction"
    )
    risk_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Risk assessment"
    )
    side_effects: List[str] = Field(
        default_factory=list,
        description="Potential side effects"
    )
    thought_signature: Optional[str] = Field(
        default=None,
        description="Encrypted thought signature for multi-turn context"
    )


class GeminiClient:
    """
    Async client for Gemini 3 Pro API.

    Implements Dyna-Think style world model predictions using Gemini 3's
    advanced reasoning capabilities with thinking_level control.

    Features:
    - thinking_level: Control reasoning depth (low/high)
    - thought_signatures: Maintain reasoning across turns
    - 1M token context window for complex state analysis
    - JSON mode for structured predictions

    Example:
        >>> config = GeminiConfig(api_key="your-api-key")
        >>> client = GeminiClient(config)
        >>> prediction = await client.simulate_action(
        ...     state={"cpu": 80, "memory": 90},
        ...     action={"type": "scale_up", "replicas": 3}
        ... )
    """

    SIMULATION_PROMPT = """You are a world model that predicts outcomes of infrastructure actions.
Your task is to simulate the effect of an action on a system state and predict the outcome.

Think step by step using your advanced reasoning capabilities:
1. Analyze the current state thoroughly
2. Consider what the action will do to each component
3. Predict cascading effects and side effects
4. Assess risks and failure modes
5. Estimate success probability based on analysis

Current State:
{state}

Proposed Action:
{action}

Additional Context:
{context}

Respond with a JSON object containing:
{{
    "predicted_state": {{...}},
    "success_probability": 0.0-1.0,
    "outcome": "success" | "failure" | "partial" | "unknown",
    "reasoning": "your detailed step-by-step reasoning",
    "confidence": 0.0-1.0,
    "risk_score": 0.0-1.0,
    "side_effects": ["effect1", "effect2"]
}}

IMPORTANT: Respond ONLY with valid JSON, no markdown or extra text."""

    MULTI_STEP_PROMPT = """You are a world model simulating a sequence of actions.

Initial State:
{initial_state}

Action Sequence:
{actions}

For each action, predict:
1. Intermediate state after the action
2. Success probability considering prior actions
3. Cumulative risk assessment
4. Dependencies and interactions between actions

Respond with a JSON array of predictions, one per action:
[
    {{"predicted_state": ..., "success_probability": ..., "outcome": ..., "reasoning": ..., "confidence": ..., "risk_score": ..., "side_effects": [...]}},
    ...
]"""

    def __init__(self, config: GeminiConfig):
        """Initialize Gemini 3 Pro client."""
        self.config = config
        self._base_url = "https://generativelanguage.googleapis.com/v1beta"
        self._client: Optional[httpx.AsyncClient] = None
        self._thought_signature: Optional[str] = None

        logger.info(
            "gemini_client_initialized",
            extra={
                "model": config.model,
                "thinking_level": config.thinking_level
            }
        )

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout_seconds)
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def simulate_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> SimulationPrediction:
        """
        Simulate an action and predict outcome using Gemini 3 Pro.

        Args:
            state: Current system state
            action: Action to simulate
            context: Additional context (history, constraints, etc.)

        Returns:
            SimulationPrediction with predicted outcome and thought signature
        """
        prompt = self.SIMULATION_PROMPT.format(
            state=json.dumps(state, indent=2),
            action=json.dumps(action, indent=2),
            context=json.dumps(context or {}, indent=2)
        )

        try:
            response, thought_sig = await self._call_gemini(prompt)
            prediction = self._parse_prediction(response)
            prediction.thought_signature = thought_sig

            logger.info(
                "simulation_complete",
                extra={
                    "action_type": action.get("type"),
                    "success_prob": prediction.success_probability,
                    "outcome": prediction.outcome,
                    "thinking_level": self.config.thinking_level
                }
            )

            return prediction

        except Exception as e:
            logger.error("simulation_failed", extra={"error": str(e)})
            return self._fallback_prediction(state, action, str(e))

    async def simulate_sequence(
        self,
        initial_state: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> List[SimulationPrediction]:
        """
        Simulate a sequence of actions (multi-step lookahead).

        Uses Gemini 3's extended reasoning for complex multi-step planning.

        Args:
            initial_state: Starting state
            actions: List of actions to simulate in order

        Returns:
            List of predictions for each action
        """
        prompt = self.MULTI_STEP_PROMPT.format(
            initial_state=json.dumps(initial_state, indent=2),
            actions=json.dumps(actions, indent=2)
        )

        try:
            response, _ = await self._call_gemini(prompt, thinking_level="high")
            predictions = self._parse_sequence(response, len(actions))
            return predictions

        except Exception as e:
            logger.error("sequence_simulation_failed", extra={"error": str(e)})
            return [
                self._fallback_prediction(initial_state, action, str(e))
                for action in actions
            ]

    async def _call_gemini(
        self,
        prompt: str,
        thinking_level: Optional[str] = None
    ) -> tuple[str, Optional[str]]:
        """
        Call Gemini 3 Pro API.

        Args:
            prompt: Text prompt
            thinking_level: Override default thinking level

        Returns:
            Tuple of (response text, thought signature)
        """
        client = await self._get_client()

        url = (
            f"{self._base_url}/models/{self.config.model}:generateContent"
        )

        # Build request payload for Gemini 3 Pro
        contents = [{"parts": [{"text": prompt}]}]

        # Include thought signature if available for continuity
        if self.config.use_thought_signatures and self._thought_signature:
            contents[0]["parts"].append({
                "thoughtSignature": self._thought_signature
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": self.config.max_output_tokens,
                "responseMimeType": "application/json",
                "temperature": 1.0,  # Gemini 3 recommends keeping at 1.0
            },
            "thinkingConfig": {
                "thinkingLevel": thinking_level or self.config.thinking_level
            }
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.config.api_key
        }

        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Extract text and thought signature from response
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates in response")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise ValueError("No parts in response")

        response_text = ""
        thought_signature = None

        for part in parts:
            if "text" in part:
                response_text = part["text"]
            if "thoughtSignature" in part:
                thought_signature = part["thoughtSignature"]
                # Store for next call
                self._thought_signature = thought_signature

        return response_text, thought_signature

    def _parse_prediction(self, response: str) -> SimulationPrediction:
        """Parse Gemini 3 response into SimulationPrediction."""
        try:
            # Clean response (remove markdown if present)
            text = response.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                # Remove first and last lines (```json and ```)
                text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            data = json.loads(text)
            return SimulationPrediction(**data)

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("parse_failed", extra={"error": str(e)})
            return SimulationPrediction(
                reasoning=f"Parse error: {response[:200]}",
                outcome="unknown"
            )

    def _parse_sequence(
        self,
        response: str,
        expected_count: int
    ) -> List[SimulationPrediction]:
        """Parse sequence response."""
        try:
            text = response.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            data = json.loads(text)
            if isinstance(data, list):
                return [SimulationPrediction(**item) for item in data]

            return [SimulationPrediction(**data)]

        except (json.JSONDecodeError, ValueError):
            return [
                SimulationPrediction(reasoning="Parse error", outcome="unknown")
                for _ in range(expected_count)
            ]

    def _fallback_prediction(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        error: str
    ) -> SimulationPrediction:
        """Generate fallback prediction using heuristics when API fails."""
        action_type = action.get("type", "unknown")

        # Heuristic-based predictions as fallback
        heuristics = {
            "restart": {
                "success_probability": 0.7,
                "outcome": "success",
                "risk_score": 0.3,
                "reasoning": "Fallback: Restart typically resolves transient issues"
            },
            "scale_up": {
                "success_probability": 0.8,
                "outcome": "success",
                "risk_score": 0.2,
                "reasoning": "Fallback: Scaling up increases capacity"
            },
            "scale_down": {
                "success_probability": 0.75,
                "outcome": "success",
                "risk_score": 0.4,
                "reasoning": "Fallback: Scaling down may impact performance"
            },
            "rollback": {
                "success_probability": 0.85,
                "outcome": "success",
                "risk_score": 0.15,
                "reasoning": "Fallback: Rollback to known-good state is safe"
            },
            "deploy": {
                "success_probability": 0.6,
                "outcome": "partial",
                "risk_score": 0.5,
                "reasoning": "Fallback: Deployments carry moderate risk"
            }
        }

        defaults = heuristics.get(action_type, {
            "success_probability": 0.4,
            "outcome": "unknown",
            "risk_score": 0.6,
            "reasoning": f"Fallback prediction for {action_type}: {error}"
        })

        return SimulationPrediction(
            predicted_state={**state, "action_applied": action_type},
            **defaults
        )

    def reset_thought_context(self) -> None:
        """Reset thought signature for new conversation."""
        self._thought_signature = None
        logger.info("thought_context_reset")

    async def health_check(self) -> Dict[str, Any]:
        """Check if Gemini 3 Pro API is accessible."""
        try:
            client = await self._get_client()

            # Use models.list endpoint to verify API access
            url = f"{self._base_url}/models"
            headers = {"x-goog-api-key": self.config.api_key}

            response = await client.get(url, headers=headers)

            # Check if our model is available
            models = response.json().get("models", [])
            model_available = any(
                self.config.model in m.get("name", "")
                for m in models
            )

            return {
                "healthy": response.status_code == 200 and model_available,
                "model": self.config.model,
                "thinking_level": self.config.thinking_level,
                "status_code": response.status_code,
                "model_available": model_available
            }

        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "model": self.config.model
            }
