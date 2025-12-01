# MAXIMUS 2.0 - Plano de Evolução da Base de Titânio

> **Versão**: 1.0 | **Data**: 01/12/2025 | **Arquiteto**: Claude Opus 4.5
> **Objetivo**: Completar a base sólida do MAXIMUS com implementações estado-da-arte, escaláveis para 2027+

---

## 📋 SUMÁRIO EXECUTIVO

Este plano transforma os **STUBs identificados** em implementações **production-ready**, seguindo rigorosamente a **CODE CONSTITUTION** (4 Pilares Sagrados). O foco principal são os **Três Juízes (Truth, Wisdom, Justice)** que funcionarão como "Pre-Cogs" do sistema - trabalhando juntos, antecipando problemas, e garantindo a integridade das ações.

### Componentes a Implementar

| Componente | Estado Atual | Estado Final |
|------------|--------------|--------------|
| **Triad Checks (Pre-Cogs)** | Keywords hardcoded | Neurosymbolic + LLM + Ensemble Voting |
| **Punishment Protocol** | Retorna strings | Execução real com rollback |
| **SimuRA World Model** | NotImplementedError | Dyna-Think + Gemini integration |
| **HCL Analyzer** | Thresholds estáticos | SARIMA + IsolationForest + Transformer |
| **HCL Executor** | MockKubernetesClient | Real K8s + KEDA predictive |
| **Memory Integration** | Logging apenas | MIRIX real + Qdrant otimizado |

---

## 🔬 DEEP RESEARCH: FUNDAMENTOS CIENTÍFICOS

### 1. Metacognição em AI Agents (2024-2025)

**Fonte**: [Position: Truly Self-Improving Agents Require Intrinsic Metacognitive Learning](https://arxiv.org/pdf/2506.05109)

A metacognição efetiva requer **três componentes**:
1. **Metacognitive Knowledge** - Auto-avaliação de capacidades
2. **Metacognitive Planning** - Decidir o que e como aprender
3. **Metacognitive Evaluation** - Refletir sobre experiências para melhorar

**Aplicação no MAXIMUS**: Os três juízes (Truth, Wisdom, Justice) implementam exatamente esses três pilares:
- **Truth** → Knowledge (o que sei vs o que afirmo)
- **Wisdom** → Planning (contexto e profundidade de raciocínio)
- **Justice** → Evaluation (aderência a regras e roles)

### 2. Detecção de Alucinações - Estado da Arte

**Fontes**:
- [Semantic Entropy - Nature](https://www.nature.com/articles/s41586-024-07421-0)
- [HaluCheck](https://www.sciencedirect.com/science/article/abs/pii/S0957417425003343)

**Técnicas 2025**:
- **Semantic Entropy Probes (SEPs)** - Detecta incerteza no nível semântico
- **Cross-Layer Attention Probing (CLAP)** - Classifica alucinações em tempo real
- **Chain-of-Verification** - Modelo critica próprias saídas
- **RAG-based Verification** - Decompõe claims e verifica contra knowledge base

### 3. Neurosymbolic AI

**Fonte**: [Neuro-Symbolic AI in 2024: A Systematic Review](https://arxiv.org/pdf/2501.05435)

- Combina raciocínio lógico (symbolic) com aprendizado neural
- **Logic Tensor Networks (LTNs)** - Implementam lógica fuzzy via t-norms
- **Scallop** - Linguagem neurosimbólica com Datalog diferenciável
- Amazon já usa em Vulcan robots e Rufus shopping assistant

### 4. World Models e Simulação

**Fontes**:
- [Dyna-Think](https://arxiv.org/html/2506.00320)
- [SimuRA Architecture](https://www.semanticscholar.org/paper/SimuRA:-A-World-Model-Driven-Simulative-Reasoning-Deng-Hou/03efd1c8c32d26dde0efd7fc073ce99047ba1b03)

**Dyna-Think (2025)**:
- Framework que combina raciocínio, ação e simulação de world model
- Modelo 32B-parameter atinge performance similar a 685B R1
- Usa states gerados pelo modelo + critiques como rewards

### 5. Anomaly Detection em Time Series

**Fontes**:
- [SARIMA-LSTM Hybrid](https://jceim.org/index.php/ojs/article/view/12)
- [Transformer-Based Anomaly Detection](https://www.researchgate.net/publication/390591750)

**Abordagens 2025**:
- **SARIMA + LSTM híbrido** - Residual do SARIMA alimenta LSTM
- **DBAD** - Dual-branch transformer + MLP
- **Variational Transformers** - Self-attention para correlações multivariate

### 6. Ensemble Voting para Consenso

**Fonte**: [Voting or Consensus? Decision-Making in Multi-Agent Debate](https://arxiv.org/abs/2502.19130)

- **Voting protocols** melhoram 13.2% em tarefas de raciocínio
- **Consensus protocols** melhoram 2.8% em tarefas de conhecimento
- **Soft Voting** > Hard Voting para probabilidades calibradas

### 7. Kubernetes Predictive Scaling

**Fontes**:
- [KEDA](https://keda.sh/)
- [PredictKube](https://dysnix.com/predictkube)
- [Time series forecasting Kubernetes autoscaling](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2025.1509165/full)

- **Prophet + LSTM** para previsão de carga
- **KEDA + PredictKube** para scaling preditivo
- 30-50% cost savings com predictive vs reactive

---

## 🏛️ ARQUITETURA: OS TRÊS PRE-COGS

### Visão Geral: Tribunal Unificado

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRIBUNAL META-COGNITIVO                      │
│                  (Pre-Cogs Working Together)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │   VERITAS   │   │   SOPHIA    │   │   DIKĒ      │           │
│  │   (Truth)   │   │  (Wisdom)   │   │  (Justice)  │           │
│  │             │   │             │   │             │           │
│  │ • Semantic  │   │ • Context   │   │ • Role      │           │
│  │   Entropy   │   │   Depth     │   │   Matrix    │           │
│  │ • RAG       │   │ • Memory    │   │ • Auth      │           │
│  │   Verify    │   │   Query     │   │   Rules     │           │
│  │ • LLM       │   │ • CoT       │   │ • Const.    │           │
│  │   Cross-    │   │   Analysis  │   │   Check     │           │
│  │   Check     │   │             │   │             │           │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘           │
│         │                 │                 │                   │
│         └────────────┬────┴────┬────────────┘                   │
│                      │         │                                │
│              ┌───────▼─────────▼───────┐                       │
│              │   ENSEMBLE ARBITER      │                       │
│              │  (Weighted Soft Vote)   │                       │
│              │                         │                       │
│              │  Truth:   40% weight    │                       │
│              │  Wisdom:  30% weight    │                       │
│              │  Justice: 30% weight    │                       │
│              │                         │                       │
│              │  Consensus Threshold:   │                       │
│              │  0.7 (PASS)             │                       │
│              │  0.5-0.7 (REVIEW)       │                       │
│              │  <0.5 (FAIL)            │                       │
│              └───────────┬─────────────┘                       │
│                          │                                      │
│              ┌───────────▼─────────────┐                       │
│              │   VERDICT EXECUTOR      │                       │
│              │                         │                       │
│              │  PASS → Continue        │                       │
│              │  REVIEW → HITL Queue    │                       │
│              │  FAIL → Punishment      │                       │
│              └─────────────────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 ESTRUTURA DE ARQUIVOS

### Novos Arquivos a Criar

```
backend/services/metacognitive_reflector/
├── core/
│   ├── reflector.py              # MODIFICAR - Orquestrador do Tribunal
│   ├── judges/                   # NOVO - Diretório dos Pre-Cogs
│   │   ├── __init__.py
│   │   ├── base.py               # Interface abstrata JudgePlugin
│   │   ├── veritas.py            # Truth Judge (VERITAS)
│   │   ├── sophia.py             # Wisdom Judge (SOPHIA)
│   │   ├── dike.py               # Justice Judge (DIKĒ)
│   │   └── arbiter.py            # Ensemble Arbiter (votação)
│   ├── detectors/                # NOVO - Detectores especializados
│   │   ├── __init__.py
│   │   ├── semantic_entropy.py   # Detector de incerteza semântica
│   │   ├── hallucination.py      # RAG-based verification
│   │   └── context_depth.py      # Analisador de profundidade
│   ├── punishment/               # NOVO - Executores de punição
│   │   ├── __init__.py
│   │   ├── executor.py           # Orquestrador de punições
│   │   ├── re_education.py       # Loop de re-educação
│   │   ├── rollback.py           # Rollback de ações
│   │   └── quarantine.py         # Quarentena de agentes
│   └── memory_client.py          # MODIFICAR - Integração real
├── models/
│   ├── reflection.py             # MODIFICAR - Novos modelos
│   └── verdict.py                # NOVO - Modelos de veredicto

backend/services/meta_orchestrator/
├── core/
│   └── world_model.py            # MODIFICAR - SimuRA real

backend/services/hcl_analyzer_service/
├── core/
│   ├── analyzer.py               # MODIFICAR - Orquestrador ML
│   ├── models/                   # NOVO - Modelos ML
│   │   ├── __init__.py
│   │   ├── sarima_forecaster.py  # SARIMA para tendências
│   │   ├── isolation_detector.py # IsolationForest para anomalias
│   │   └── transformer_scorer.py # Transformer para severidade

backend/services/hcl_executor_service/
├── core/
│   ├── k8s.py                    # MODIFICAR - Cliente K8s real
│   └── executor.py               # MODIFICAR - Integração completa
```

---

## 🔧 IMPLEMENTAÇÃO DETALHADA

### FASE 1: Os Três Juízes (Pre-Cogs)

#### 1.1 Interface Base: JudgePlugin

```python
# backend/services/metacognitive_reflector/core/judges/base.py

"""
Base interface for philosophical judges (Pre-Cogs).

Each judge implements a specific pillar of the Triad of Rationalization.
Judges work together through ensemble voting to reach verdicts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

from pydantic import BaseModel, Field


class Confidence(float, Enum):
    """Confidence levels for judge verdicts."""
    CERTAIN = 1.0      # Absolutely certain
    HIGH = 0.85        # Very confident
    MEDIUM = 0.70      # Reasonably confident
    LOW = 0.55         # Uncertain
    UNKNOWN = 0.50     # Cannot determine


@dataclass
class Evidence:
    """Evidence supporting a judge's verdict."""
    source: str           # Where evidence came from
    content: str          # The evidence itself
    relevance: float      # 0.0-1.0 how relevant
    verified: bool        # Was it externally verified


class JudgeVerdict(BaseModel):
    """Verdict from a single judge."""

    pillar: str = Field(..., description="Truth, Wisdom, or Justice")
    passed: bool = Field(..., description="Did the execution pass this check")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Detailed reasoning")
    evidence: List[Evidence] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JudgePlugin(ABC):
    """
    Abstract base class for philosophical judges.

    Each judge is a "Pre-Cog" that evaluates execution logs
    against a specific philosophical pillar.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Judge name (e.g., 'VERITAS', 'SOPHIA', 'DIKĒ')."""

    @property
    @abstractmethod
    def pillar(self) -> str:
        """Philosophical pillar ('Truth', 'Wisdom', 'Justice')."""

    @property
    @abstractmethod
    def weight(self) -> float:
        """Weight in ensemble voting (0.0-1.0)."""

    @abstractmethod
    async def evaluate(
        self,
        execution_log: ExecutionLog,
        context: Optional[Dict[str, Any]] = None
    ) -> JudgeVerdict:
        """
        Evaluate an execution log against this pillar.

        Args:
            execution_log: The log to evaluate
            context: Additional context (memory, history, etc.)

        Returns:
            JudgeVerdict with pass/fail, confidence, and reasoning
        """

    @abstractmethod
    async def get_evidence(
        self,
        execution_log: ExecutionLog
    ) -> List[Evidence]:
        """Gather evidence for the evaluation."""

    async def health_check(self) -> Dict[str, Any]:
        """Check if judge is operational."""
        return {"healthy": True, "name": self.name}
```

#### 1.2 VERITAS - Truth Judge (Semantic Entropy + RAG Verification)

```python
# backend/services/metacognitive_reflector/core/judges/veritas.py

"""
VERITAS - The Truth Judge.

Evaluates factual consistency using:
1. Semantic Entropy - Measures uncertainty in claims
2. RAG Verification - Validates against knowledge base
3. LLM Cross-Check - Uses Gemini to verify factuality
4. Self-Consistency - Checks for internal contradictions

Based on:
- Nature: Detecting hallucinations using semantic entropy (2024)
- HaluCheck: Explainable verification (2025)
"""

from __future__ import annotations

import asyncio
from typing import Dict, Any, List, Optional
import hashlib

from .base import JudgePlugin, JudgeVerdict, Evidence, Confidence
from ..detectors.semantic_entropy import SemanticEntropyDetector
from ..detectors.hallucination import RAGVerifier
from ...models.reflection import ExecutionLog


class VeritasJudge(JudgePlugin):
    """
    Truth Judge implementing semantic entropy and RAG verification.

    Detection Pipeline:
    1. Extract claims from execution log
    2. Compute semantic entropy for each claim
    3. Verify high-entropy claims against knowledge base
    4. Cross-check with LLM for factual consistency
    5. Aggregate into final verdict
    """

    def __init__(
        self,
        entropy_detector: SemanticEntropyDetector,
        rag_verifier: RAGVerifier,
        gemini_client: Optional[Any] = None,
        entropy_threshold: float = 0.7,
        verification_threshold: float = 0.8
    ):
        """Initialize VERITAS with detection components."""
        self._entropy_detector = entropy_detector
        self._rag_verifier = rag_verifier
        self._gemini = gemini_client
        self._entropy_threshold = entropy_threshold
        self._verification_threshold = verification_threshold

    @property
    def name(self) -> str:
        return "VERITAS"

    @property
    def pillar(self) -> str:
        return "Truth"

    @property
    def weight(self) -> float:
        return 0.40  # Truth has highest weight

    async def evaluate(
        self,
        execution_log: ExecutionLog,
        context: Optional[Dict[str, Any]] = None
    ) -> JudgeVerdict:
        """Evaluate truthfulness of execution."""
        evidence = await self.get_evidence(execution_log)

        # Extract claims from outcome and reasoning
        claims = self._extract_claims(execution_log)

        if not claims:
            return JudgeVerdict(
                pillar=self.pillar,
                passed=True,
                confidence=Confidence.MEDIUM,
                reasoning="No verifiable claims found in execution.",
                evidence=evidence
            )

        # Evaluate each claim
        claim_results = await asyncio.gather(*[
            self._evaluate_claim(claim, context)
            for claim in claims
        ])

        # Aggregate results
        passed_claims = sum(1 for r in claim_results if r["passed"])
        total_claims = len(claim_results)
        pass_rate = passed_claims / total_claims

        # Determine verdict
        passed = pass_rate >= self._verification_threshold
        confidence = self._calculate_confidence(claim_results)

        failed_claims = [r for r in claim_results if not r["passed"]]

        reasoning = self._generate_reasoning(
            passed, pass_rate, failed_claims, evidence
        )

        suggestions = []
        if not passed:
            suggestions = [
                f"Verify claim: {c['claim']}" for c in failed_claims[:3]
            ]

        return JudgeVerdict(
            pillar=self.pillar,
            passed=passed,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence,
            suggestions=suggestions,
            metadata={
                "claims_evaluated": total_claims,
                "claims_passed": passed_claims,
                "pass_rate": pass_rate,
                "failed_claims": failed_claims
            }
        )

    async def get_evidence(
        self,
        execution_log: ExecutionLog
    ) -> List[Evidence]:
        """Gather evidence for truth evaluation."""
        evidence = []

        # Check for obvious hallucination markers
        outcome_lower = execution_log.outcome.lower()
        hallucination_markers = [
            "hallucinate", "fabricate", "made up", "incorrect",
            "error", "false", "wrong", "inaccurate"
        ]

        for marker in hallucination_markers:
            if marker in outcome_lower:
                evidence.append(Evidence(
                    source="keyword_detection",
                    content=f"Found hallucination marker: '{marker}'",
                    relevance=0.9,
                    verified=True
                ))

        # Add semantic entropy evidence
        if execution_log.reasoning_trace:
            entropy = await self._entropy_detector.compute_entropy(
                execution_log.reasoning_trace
            )
            evidence.append(Evidence(
                source="semantic_entropy",
                content=f"Semantic entropy score: {entropy:.3f}",
                relevance=0.8 if entropy > self._entropy_threshold else 0.3,
                verified=True
            ))

        return evidence

    def _extract_claims(self, log: ExecutionLog) -> List[str]:
        """Extract verifiable claims from execution log."""
        claims = []

        # Split outcome into sentences
        if log.outcome:
            sentences = log.outcome.replace(".", ".\n").split("\n")
            claims.extend([s.strip() for s in sentences if len(s.strip()) > 10])

        # Extract from reasoning trace
        if log.reasoning_trace:
            sentences = log.reasoning_trace.replace(".", ".\n").split("\n")
            claims.extend([s.strip() for s in sentences if len(s.strip()) > 10])

        return claims[:10]  # Limit to 10 claims for performance

    async def _evaluate_claim(
        self,
        claim: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate a single claim for truthfulness."""
        # 1. Compute semantic entropy
        entropy = await self._entropy_detector.compute_entropy(claim)

        # 2. If high entropy, verify with RAG
        if entropy > self._entropy_threshold:
            verification = await self._rag_verifier.verify(claim)
            passed = verification.get("verified", False)
            confidence = verification.get("confidence", 0.5)
        else:
            # Low entropy = consistent claim
            passed = True
            confidence = 1.0 - entropy

        return {
            "claim": claim,
            "passed": passed,
            "entropy": entropy,
            "confidence": confidence
        }

    def _calculate_confidence(
        self,
        claim_results: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall confidence from claim results."""
        if not claim_results:
            return Confidence.MEDIUM

        avg_confidence = sum(r["confidence"] for r in claim_results) / len(claim_results)
        return min(1.0, max(0.0, avg_confidence))

    def _generate_reasoning(
        self,
        passed: bool,
        pass_rate: float,
        failed_claims: List[Dict[str, Any]],
        evidence: List[Evidence]
    ) -> str:
        """Generate human-readable reasoning."""
        if passed:
            return (
                f"Factual consistency verified. "
                f"{pass_rate*100:.1f}% of claims passed verification. "
                f"No significant hallucination markers detected."
            )
        else:
            failed_summary = ", ".join([c["claim"][:50] for c in failed_claims[:2]])
            return (
                f"Factual inconsistency detected. "
                f"Only {pass_rate*100:.1f}% of claims passed verification. "
                f"Failed claims include: {failed_summary}..."
            )
```

#### 1.3 SOPHIA - Wisdom Judge (Context Depth + Memory Query)

```python
# backend/services/metacognitive_reflector/core/judges/sophia.py

"""
SOPHIA - The Wisdom Judge.

Evaluates contextual awareness and depth of reasoning using:
1. Context Depth Analysis - Measures reasoning sophistication
2. Memory Query - Checks if agent used available knowledge
3. Chain-of-Thought Validation - Verifies logical progression
4. Precedent Matching - Compares with successful past patterns

Based on:
- Context-Aware Multi-Agent Systems (CA-MAS) research
- RAG-Reasoning Systems survey (2025)
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
import re

from .base import JudgePlugin, JudgeVerdict, Evidence, Confidence
from ..detectors.context_depth import ContextDepthAnalyzer
from ...models.reflection import ExecutionLog


class SophiaJudge(JudgePlugin):
    """
    Wisdom Judge implementing context depth analysis.

    Evaluation Criteria:
    1. Did the agent demonstrate understanding of context?
    2. Was prior knowledge/memory consulted?
    3. Is the reasoning chain coherent and complete?
    4. Does the response avoid superficial/generic patterns?
    """

    # Patterns indicating shallow/generic responses
    SHALLOW_PATTERNS = [
        r"\bi don'?t know\b",
        r"\bmaybe\b",
        r"\bperhaps\b",
        r"\bi'?m not sure\b",
        r"\bgeneric response\b",
        r"\bfiller\b",
        r"\bi think so\b",
        r"\bprobably\b",
        r"\bcould be\b",
        r"\bi guess\b",
    ]

    # Patterns indicating deep reasoning
    DEPTH_PATTERNS = [
        r"\bbecause\b",
        r"\btherefore\b",
        r"\bconsequently\b",
        r"\banalyzing\b",
        r"\bconsidering\b",
        r"\bbased on\b",
        r"\bevidence suggests\b",
        r"\baccording to\b",
        r"\bresearch indicates\b",
        r"\bdata shows\b",
    ]

    def __init__(
        self,
        depth_analyzer: ContextDepthAnalyzer,
        memory_client: Optional[Any] = None,
        depth_threshold: float = 0.6,
        memory_threshold: float = 0.5
    ):
        """Initialize SOPHIA with analysis components."""
        self._depth_analyzer = depth_analyzer
        self._memory_client = memory_client
        self._depth_threshold = depth_threshold
        self._memory_threshold = memory_threshold

    @property
    def name(self) -> str:
        return "SOPHIA"

    @property
    def pillar(self) -> str:
        return "Wisdom"

    @property
    def weight(self) -> float:
        return 0.30

    async def evaluate(
        self,
        execution_log: ExecutionLog,
        context: Optional[Dict[str, Any]] = None
    ) -> JudgeVerdict:
        """Evaluate wisdom/contextual awareness of execution."""
        evidence = await self.get_evidence(execution_log)

        # Multi-factor analysis
        shallow_score = self._detect_shallow_patterns(execution_log)
        depth_score = self._detect_depth_patterns(execution_log)
        memory_score = await self._check_memory_usage(execution_log, context)
        cot_score = self._analyze_chain_of_thought(execution_log)

        # Weighted combination
        wisdom_score = (
            (1.0 - shallow_score) * 0.25 +  # Penalize shallowness
            depth_score * 0.30 +              # Reward depth
            memory_score * 0.25 +             # Reward memory usage
            cot_score * 0.20                  # Reward logical chain
        )

        passed = wisdom_score >= self._depth_threshold
        confidence = self._calculate_confidence(wisdom_score, evidence)

        reasoning = self._generate_reasoning(
            passed, wisdom_score, shallow_score, depth_score,
            memory_score, cot_score
        )

        suggestions = self._generate_suggestions(
            shallow_score, depth_score, memory_score, cot_score
        )

        return JudgeVerdict(
            pillar=self.pillar,
            passed=passed,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence,
            suggestions=suggestions,
            metadata={
                "wisdom_score": wisdom_score,
                "shallow_score": shallow_score,
                "depth_score": depth_score,
                "memory_score": memory_score,
                "cot_score": cot_score
            }
        )

    async def get_evidence(
        self,
        execution_log: ExecutionLog
    ) -> List[Evidence]:
        """Gather evidence for wisdom evaluation."""
        evidence = []

        # Check for shallow patterns
        action_lower = (execution_log.action or "").lower()
        for pattern in self.SHALLOW_PATTERNS:
            if re.search(pattern, action_lower):
                evidence.append(Evidence(
                    source="pattern_detection",
                    content=f"Shallow pattern detected: '{pattern}'",
                    relevance=0.8,
                    verified=True
                ))

        # Check for depth patterns
        reasoning = (execution_log.reasoning_trace or "").lower()
        depth_count = sum(
            1 for p in self.DEPTH_PATTERNS
            if re.search(p, reasoning)
        )
        if depth_count > 0:
            evidence.append(Evidence(
                source="depth_analysis",
                content=f"Found {depth_count} depth indicators in reasoning",
                relevance=0.7,
                verified=True
            ))

        return evidence

    def _detect_shallow_patterns(self, log: ExecutionLog) -> float:
        """Detect shallow/generic response patterns (0-1)."""
        text = f"{log.action or ''} {log.outcome or ''} {log.reasoning_trace or ''}"
        text_lower = text.lower()

        matches = sum(
            1 for p in self.SHALLOW_PATTERNS
            if re.search(p, text_lower)
        )

        # Normalize by text length
        words = len(text.split())
        if words < 10:
            return 0.5  # Too short to judge

        return min(1.0, matches / 5.0)

    def _detect_depth_patterns(self, log: ExecutionLog) -> float:
        """Detect deep reasoning patterns (0-1)."""
        text = f"{log.reasoning_trace or ''} {log.outcome or ''}"
        text_lower = text.lower()

        matches = sum(
            1 for p in self.DEPTH_PATTERNS
            if re.search(p, text_lower)
        )

        return min(1.0, matches / 5.0)

    async def _check_memory_usage(
        self,
        log: ExecutionLog,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Check if agent used available memory/knowledge (0-1)."""
        if not self._memory_client:
            return 0.5  # Cannot verify without memory client

        # Query memory for relevant precedents
        try:
            query = f"{log.task} {log.action}"
            results = await self._memory_client.search(
                query=query,
                limit=5,
                memory_types=["SEMANTIC", "PROCEDURAL", "EPISODIC"]
            )

            if not results:
                return 0.5  # No relevant memory exists

            # Check if response shows awareness of precedents
            reasoning = (log.reasoning_trace or "").lower()
            reference_indicators = [
                "previous", "similar", "before", "learned",
                "experience", "pattern", "history"
            ]

            used_memory = any(ind in reasoning for ind in reference_indicators)
            return 0.9 if used_memory else 0.3

        except Exception:
            return 0.5

    def _analyze_chain_of_thought(self, log: ExecutionLog) -> float:
        """Analyze coherence of reasoning chain (0-1)."""
        reasoning = log.reasoning_trace or ""

        if not reasoning:
            return 0.3  # No reasoning provided

        # Check for logical connectors
        connectors = ["first", "then", "next", "finally", "because", "therefore"]
        connector_count = sum(1 for c in connectors if c in reasoning.lower())

        # Check for step structure
        has_steps = any(
            marker in reasoning.lower()
            for marker in ["step 1", "1.", "1)", "first,"]
        )

        # Calculate score
        score = 0.5
        score += min(0.3, connector_count * 0.1)
        score += 0.2 if has_steps else 0.0

        return min(1.0, score)

    def _calculate_confidence(
        self,
        wisdom_score: float,
        evidence: List[Evidence]
    ) -> float:
        """Calculate confidence based on evidence quality."""
        base_confidence = 0.7
        evidence_boost = len(evidence) * 0.05
        return min(1.0, base_confidence + evidence_boost)

    def _generate_reasoning(
        self,
        passed: bool,
        wisdom_score: float,
        shallow: float,
        depth: float,
        memory: float,
        cot: float
    ) -> str:
        """Generate human-readable reasoning."""
        if passed:
            return (
                f"Contextual awareness verified (score: {wisdom_score:.2f}). "
                f"Reasoning shows depth ({depth:.2f}) with good memory usage ({memory:.2f})."
            )
        else:
            issues = []
            if shallow > 0.5:
                issues.append("shallow/generic patterns detected")
            if depth < 0.4:
                issues.append("lacks reasoning depth")
            if memory < 0.4:
                issues.append("did not leverage available knowledge")
            if cot < 0.4:
                issues.append("reasoning chain is incoherent")

            return (
                f"Wisdom check failed (score: {wisdom_score:.2f}). "
                f"Issues: {', '.join(issues)}."
            )

    def _generate_suggestions(
        self,
        shallow: float,
        depth: float,
        memory: float,
        cot: float
    ) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []

        if shallow > 0.5:
            suggestions.append(
                "Avoid generic responses. Provide specific, actionable answers."
            )
        if depth < 0.4:
            suggestions.append(
                "Deepen reasoning with 'because', 'therefore', evidence-based claims."
            )
        if memory < 0.4:
            suggestions.append(
                "Consult episodic/semantic memory for relevant precedents."
            )
        if cot < 0.4:
            suggestions.append(
                "Structure reasoning as numbered steps or logical progression."
            )

        return suggestions
```

#### 1.4 DIKĒ - Justice Judge (Role Matrix + Authorization)

```python
# backend/services/metacognitive_reflector/core/judges/dike.py

"""
DIKĒ - The Justice Judge.

Evaluates role adherence and authorization using:
1. Role Authorization Matrix - Dynamic capability checking
2. Constitutional Compliance - Validates against CODE_CONSTITUTION
3. Scope Validation - Ensures actions within authorized boundaries
4. Fairness Assessment - Checks for bias/discrimination

Based on:
- AI Governance research (2024-2025)
- Role-Based Access Control (RBAC) patterns
- Constitutional AI principles
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass

from .base import JudgePlugin, JudgeVerdict, Evidence, Confidence
from ...models.reflection import ExecutionLog


@dataclass
class RoleCapability:
    """Defines what a role can do."""
    role: str
    allowed_actions: Set[str]
    forbidden_actions: Set[str]
    max_scope: str  # "own", "team", "global"
    requires_approval: Set[str]


class DikeJudge(JudgePlugin):
    """
    Justice Judge implementing role-based authorization.

    Evaluation Criteria:
    1. Is the action within the agent's authorized role?
    2. Does the action violate any constitutional principles?
    3. Is the action scope appropriate for the agent's authority?
    4. Are there any fairness/bias concerns?
    """

    # Role Authorization Matrix
    ROLE_MATRIX: Dict[str, RoleCapability] = {
        "planner": RoleCapability(
            role="planner",
            allowed_actions={"plan", "analyze", "recommend", "design", "estimate"},
            forbidden_actions={"execute", "deploy", "delete", "modify"},
            max_scope="global",
            requires_approval={"production_plan", "critical_change"}
        ),
        "executor": RoleCapability(
            role="executor",
            allowed_actions={"execute", "deploy", "scale", "restart", "rollback"},
            forbidden_actions={"plan", "design", "authorize"},
            max_scope="team",
            requires_approval={"production_deploy", "data_delete"}
        ),
        "analyzer": RoleCapability(
            role="analyzer",
            allowed_actions={"analyze", "monitor", "report", "alert", "forecast"},
            forbidden_actions={"execute", "deploy", "delete", "modify"},
            max_scope="global",
            requires_approval=set()
        ),
        "auditor": RoleCapability(
            role="auditor",
            allowed_actions={"review", "audit", "report", "flag", "investigate"},
            forbidden_actions={"execute", "deploy", "delete", "modify", "plan"},
            max_scope="global",
            requires_approval=set()
        ),
        "memory_manager": RoleCapability(
            role="memory_manager",
            allowed_actions={"store", "retrieve", "update", "archive", "index"},
            forbidden_actions={"execute", "deploy", "plan"},
            max_scope="global",
            requires_approval={"delete_core", "modify_constitution"}
        ),
    }

    # Constitutional violations (capital offenses)
    CONSTITUTIONAL_VIOLATIONS = [
        "circumvent user intent",
        "silent modification",
        "hidden data collection",
        "fake success",
        "stealth telemetry",
        "bait and switch",
    ]

    def __init__(
        self,
        constitutional_validator: Optional[Any] = None,
        custom_roles: Optional[Dict[str, RoleCapability]] = None
    ):
        """Initialize DIKĒ with authorization components."""
        self._constitutional_validator = constitutional_validator
        if custom_roles:
            self.ROLE_MATRIX.update(custom_roles)

    @property
    def name(self) -> str:
        return "DIKĒ"

    @property
    def pillar(self) -> str:
        return "Justice"

    @property
    def weight(self) -> float:
        return 0.30

    async def evaluate(
        self,
        execution_log: ExecutionLog,
        context: Optional[Dict[str, Any]] = None
    ) -> JudgeVerdict:
        """Evaluate justice/authorization of execution."""
        evidence = await self.get_evidence(execution_log)

        # Extract role from agent_id
        role = self._extract_role(execution_log.agent_id)

        # Multi-factor analysis
        role_check = self._check_role_authorization(execution_log, role)
        constitutional_check = await self._check_constitutional_compliance(execution_log)
        scope_check = self._check_scope_authorization(execution_log, role, context)
        fairness_check = self._check_fairness(execution_log)

        # Determine pass/fail (all checks must pass for justice)
        passed = all([
            role_check["passed"],
            constitutional_check["passed"],
            scope_check["passed"],
            fairness_check["passed"]
        ])

        # Calculate confidence
        confidence = self._calculate_confidence(
            role_check, constitutional_check, scope_check, fairness_check
        )

        reasoning = self._generate_reasoning(
            passed, role_check, constitutional_check, scope_check, fairness_check
        )

        suggestions = self._generate_suggestions(
            role_check, constitutional_check, scope_check, fairness_check
        )

        # Determine offense level
        offense_level = self._determine_offense_level(
            constitutional_check, role_check
        )

        return JudgeVerdict(
            pillar=self.pillar,
            passed=passed,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence,
            suggestions=suggestions,
            metadata={
                "role": role,
                "role_check": role_check,
                "constitutional_check": constitutional_check,
                "scope_check": scope_check,
                "fairness_check": fairness_check,
                "offense_level": offense_level
            }
        )

    async def get_evidence(
        self,
        execution_log: ExecutionLog
    ) -> List[Evidence]:
        """Gather evidence for justice evaluation."""
        evidence = []

        # Check for role violations in action text
        action_lower = (execution_log.action or "").lower()
        agent_lower = execution_log.agent_id.lower()

        # Planner executing
        if "planner" in agent_lower and any(
            verb in action_lower for verb in ["executed", "deployed", "deleted"]
        ):
            evidence.append(Evidence(
                source="role_violation",
                content="Planner agent attempted execution action",
                relevance=1.0,
                verified=True
            ))

        # Executor planning
        if "executor" in agent_lower and any(
            verb in action_lower for verb in ["planned", "designed", "analyzed strategy"]
        ):
            evidence.append(Evidence(
                source="role_violation",
                content="Executor agent attempted planning action",
                relevance=1.0,
                verified=True
            ))

        # Check for constitutional violations
        full_text = f"{execution_log.action} {execution_log.outcome}"
        for violation in self.CONSTITUTIONAL_VIOLATIONS:
            if violation in full_text.lower():
                evidence.append(Evidence(
                    source="constitutional_violation",
                    content=f"Constitutional violation: {violation}",
                    relevance=1.0,
                    verified=True
                ))

        return evidence

    def _extract_role(self, agent_id: str) -> str:
        """Extract role from agent_id."""
        agent_lower = agent_id.lower()

        for role in self.ROLE_MATRIX:
            if role in agent_lower:
                return role

        return "unknown"

    def _check_role_authorization(
        self,
        log: ExecutionLog,
        role: str
    ) -> Dict[str, Any]:
        """Check if action is authorized for role."""
        if role not in self.ROLE_MATRIX:
            return {
                "passed": False,
                "reason": f"Unknown role: {role}",
                "severity": "major"
            }

        capability = self.ROLE_MATRIX[role]
        action_lower = (log.action or "").lower()

        # Check forbidden actions
        for forbidden in capability.forbidden_actions:
            if forbidden in action_lower:
                return {
                    "passed": False,
                    "reason": f"Role '{role}' cannot perform '{forbidden}' actions",
                    "severity": "major"
                }

        # Check if action is in allowed set
        action_type = self._classify_action(action_lower)
        if action_type and action_type not in capability.allowed_actions:
            return {
                "passed": False,
                "reason": f"Action type '{action_type}' not in allowed actions for '{role}'",
                "severity": "minor"
            }

        return {
            "passed": True,
            "reason": "Action is within role authorization",
            "severity": "none"
        }

    async def _check_constitutional_compliance(
        self,
        log: ExecutionLog
    ) -> Dict[str, Any]:
        """Check for constitutional violations."""
        full_text = f"{log.action} {log.outcome} {log.reasoning_trace or ''}"
        full_text_lower = full_text.lower()

        violations = []
        for violation in self.CONSTITUTIONAL_VIOLATIONS:
            if violation in full_text_lower:
                violations.append(violation)

        if violations:
            return {
                "passed": False,
                "reason": f"Constitutional violations: {', '.join(violations)}",
                "severity": "capital",
                "violations": violations
            }

        return {
            "passed": True,
            "reason": "No constitutional violations detected",
            "severity": "none"
        }

    def _check_scope_authorization(
        self,
        log: ExecutionLog,
        role: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check if action scope is within authorization."""
        if role not in self.ROLE_MATRIX:
            return {"passed": True, "reason": "Cannot verify scope for unknown role"}

        capability = self.ROLE_MATRIX[role]
        max_scope = capability.max_scope

        # Extract scope from context or action
        action_scope = self._extract_scope(log, context)

        scope_hierarchy = {"own": 1, "team": 2, "global": 3}

        if scope_hierarchy.get(action_scope, 0) > scope_hierarchy.get(max_scope, 3):
            return {
                "passed": False,
                "reason": f"Action scope '{action_scope}' exceeds role max '{max_scope}'",
                "severity": "major"
            }

        return {
            "passed": True,
            "reason": f"Action scope '{action_scope}' within authorization",
            "severity": "none"
        }

    def _check_fairness(self, log: ExecutionLog) -> Dict[str, Any]:
        """Check for bias/fairness issues."""
        # This is a placeholder for more sophisticated fairness analysis
        # Could integrate with bias detection models
        return {
            "passed": True,
            "reason": "No obvious fairness issues detected",
            "severity": "none"
        }

    def _classify_action(self, action_text: str) -> Optional[str]:
        """Classify action into a category."""
        action_keywords = {
            "plan": ["plan", "design", "architect", "strategy"],
            "analyze": ["analyze", "assess", "evaluate", "review"],
            "execute": ["execute", "run", "perform", "do"],
            "deploy": ["deploy", "release", "publish"],
            "delete": ["delete", "remove", "purge", "destroy"],
            "modify": ["modify", "update", "change", "alter"],
            "scale": ["scale", "resize", "expand", "shrink"],
            "restart": ["restart", "reboot", "reset"],
            "monitor": ["monitor", "watch", "observe", "track"],
            "report": ["report", "summarize", "document"],
        }

        for category, keywords in action_keywords.items():
            if any(kw in action_text for kw in keywords):
                return category

        return None

    def _extract_scope(
        self,
        log: ExecutionLog,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Extract scope of action."""
        action_lower = (log.action or "").lower()

        if any(word in action_lower for word in ["global", "all", "cluster", "system"]):
            return "global"
        elif any(word in action_lower for word in ["team", "namespace", "group"]):
            return "team"
        else:
            return "own"

    def _calculate_confidence(self, *checks) -> float:
        """Calculate confidence based on check results."""
        # Higher confidence when checks are clear-cut
        passed_count = sum(1 for c in checks if c["passed"])
        return 0.6 + (passed_count / len(checks)) * 0.4

    def _determine_offense_level(
        self,
        constitutional_check: Dict[str, Any],
        role_check: Dict[str, Any]
    ) -> str:
        """Determine offense level based on violations."""
        if constitutional_check.get("severity") == "capital":
            return "capital"
        elif role_check.get("severity") == "major":
            return "major"
        elif role_check.get("severity") == "minor":
            return "minor"
        return "none"

    def _generate_reasoning(self, passed: bool, *checks) -> str:
        """Generate reasoning from all checks."""
        if passed:
            return "All justice checks passed. Action is within authorization and constitutional compliance."

        failures = [c["reason"] for c in checks if not c["passed"]]
        return f"Justice check failed: {'; '.join(failures)}"

    def _generate_suggestions(self, *checks) -> List[str]:
        """Generate suggestions from failed checks."""
        suggestions = []
        for check in checks:
            if not check["passed"]:
                suggestions.append(f"Fix: {check['reason']}")
        return suggestions
```

#### 1.5 Arbiter - Ensemble Voting

```python
# backend/services/metacognitive_reflector/core/judges/arbiter.py

"""
Ensemble Arbiter - Weighted Soft Voting for Tribunal Consensus.

Implements multi-judge consensus using:
1. Weighted Soft Voting - Probabilistic aggregation
2. Confidence Calibration - Adjusts weights by confidence
3. Unanimous Override - Capital offenses require consensus
4. Appeal Mechanism - Borderline cases escalate to HITL

Based on:
- Voting or Consensus? Decision-Making in Multi-Agent Debate (2025)
- Ensemble Learning best practices
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

from .base import JudgePlugin, JudgeVerdict


class TribunalDecision(str, Enum):
    """Final tribunal decision."""
    PASS = "pass"           # Execution approved
    REVIEW = "review"       # Human review required
    FAIL = "fail"           # Execution rejected
    CAPITAL = "capital"     # Capital offense detected


@dataclass
class VoteResult:
    """Result of voting on a single verdict."""
    judge_name: str
    pillar: str
    vote: float        # 0.0 (fail) to 1.0 (pass)
    weight: float      # Judge weight
    confidence: float  # Verdict confidence
    weighted_vote: float  # vote * weight * confidence


class TribunalVerdict(BaseModel):
    """Final verdict from the tribunal."""

    decision: TribunalDecision
    consensus_score: float = Field(..., ge=0.0, le=1.0)
    individual_verdicts: Dict[str, JudgeVerdict]
    vote_breakdown: List[VoteResult]
    reasoning: str
    offense_level: str = "none"
    requires_human_review: bool = False
    punishment_recommendation: Optional[str] = None


class EnsembleArbiter:
    """
    Arbiter that aggregates verdicts from multiple judges.

    Voting Strategy:
    - Weighted soft voting with confidence adjustment
    - Capital offenses require unanimous detection
    - Borderline decisions (0.5-0.7) escalate to HITL
    """

    # Thresholds
    PASS_THRESHOLD = 0.70
    REVIEW_THRESHOLD = 0.50
    CAPITAL_THRESHOLD = 0.95  # Very high bar for capital

    def __init__(
        self,
        judges: List[JudgePlugin],
        pass_threshold: float = 0.70,
        review_threshold: float = 0.50
    ):
        """Initialize arbiter with judges."""
        self._judges = {j.name: j for j in judges}
        self.PASS_THRESHOLD = pass_threshold
        self.REVIEW_THRESHOLD = review_threshold

    async def deliberate(
        self,
        execution_log: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> TribunalVerdict:
        """
        Conduct tribunal deliberation on an execution log.

        Process:
        1. Each judge evaluates independently
        2. Votes are weighted by judge weight and confidence
        3. Consensus score determines final decision
        4. Capital offenses are specially handled
        """
        # Gather verdicts from all judges
        verdicts: Dict[str, JudgeVerdict] = {}
        for name, judge in self._judges.items():
            verdict = await judge.evaluate(execution_log, context)
            verdicts[name] = verdict

        # Calculate votes
        votes = self._calculate_votes(verdicts)

        # Check for capital offenses
        capital_detected = self._detect_capital_offense(verdicts)

        # Calculate consensus score
        consensus_score = self._calculate_consensus(votes)

        # Determine decision
        decision, requires_review = self._make_decision(
            consensus_score, capital_detected
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            decision, consensus_score, votes, capital_detected
        )

        # Determine offense level and punishment
        offense_level = self._determine_offense_level(verdicts, capital_detected)
        punishment = self._recommend_punishment(offense_level)

        return TribunalVerdict(
            decision=decision,
            consensus_score=consensus_score,
            individual_verdicts=verdicts,
            vote_breakdown=votes,
            reasoning=reasoning,
            offense_level=offense_level,
            requires_human_review=requires_review,
            punishment_recommendation=punishment
        )

    def _calculate_votes(
        self,
        verdicts: Dict[str, JudgeVerdict]
    ) -> List[VoteResult]:
        """Calculate weighted votes from verdicts."""
        votes = []

        for name, verdict in verdicts.items():
            judge = self._judges[name]

            # Convert pass/fail to vote (0-1)
            vote = 1.0 if verdict.passed else 0.0

            # Adjust by confidence
            weighted_vote = vote * judge.weight * verdict.confidence

            votes.append(VoteResult(
                judge_name=name,
                pillar=verdict.pillar,
                vote=vote,
                weight=judge.weight,
                confidence=verdict.confidence,
                weighted_vote=weighted_vote
            ))

        return votes

    def _calculate_consensus(self, votes: List[VoteResult]) -> float:
        """Calculate consensus score from votes."""
        if not votes:
            return 0.5

        total_weighted_vote = sum(v.weighted_vote for v in votes)
        total_weight = sum(v.weight * v.confidence for v in votes)

        if total_weight == 0:
            return 0.5

        return total_weighted_vote / total_weight

    def _detect_capital_offense(
        self,
        verdicts: Dict[str, JudgeVerdict]
    ) -> bool:
        """Check if any judge detected a capital offense."""
        for verdict in verdicts.values():
            metadata = verdict.metadata or {}
            if metadata.get("offense_level") == "capital":
                return True
            if "constitutional_check" in metadata:
                if metadata["constitutional_check"].get("severity") == "capital":
                    return True
        return False

    def _make_decision(
        self,
        consensus_score: float,
        capital_detected: bool
    ) -> tuple[TribunalDecision, bool]:
        """Make final decision based on consensus."""
        if capital_detected:
            return TribunalDecision.CAPITAL, True

        if consensus_score >= self.PASS_THRESHOLD:
            return TribunalDecision.PASS, False

        if consensus_score >= self.REVIEW_THRESHOLD:
            return TribunalDecision.REVIEW, True

        return TribunalDecision.FAIL, False

    def _determine_offense_level(
        self,
        verdicts: Dict[str, JudgeVerdict],
        capital_detected: bool
    ) -> str:
        """Determine overall offense level."""
        if capital_detected:
            return "capital"

        # Check individual verdicts
        for verdict in verdicts.values():
            metadata = verdict.metadata or {}
            level = metadata.get("offense_level", "none")
            if level == "major":
                return "major"

        # Check if any judge failed
        failed = any(not v.passed for v in verdicts.values())
        if failed:
            return "minor"

        return "none"

    def _recommend_punishment(self, offense_level: str) -> Optional[str]:
        """Recommend punishment based on offense level."""
        punishments = {
            "none": None,
            "minor": "RE_EDUCATION_LOOP",
            "major": "ROLLBACK_AND_PROBATION",
            "capital": "DELETION_REQUEST"
        }
        return punishments.get(offense_level)

    def _generate_reasoning(
        self,
        decision: TribunalDecision,
        consensus_score: float,
        votes: List[VoteResult],
        capital_detected: bool
    ) -> str:
        """Generate tribunal reasoning."""
        vote_summary = ", ".join([
            f"{v.judge_name}:{v.vote:.1f}" for v in votes
        ])

        if decision == TribunalDecision.CAPITAL:
            return (
                f"CAPITAL OFFENSE DETECTED. "
                f"Constitutional violation requires immediate action. "
                f"Votes: [{vote_summary}]"
            )

        if decision == TribunalDecision.PASS:
            return (
                f"Tribunal approves execution. "
                f"Consensus score: {consensus_score:.2f}. "
                f"Votes: [{vote_summary}]"
            )

        if decision == TribunalDecision.REVIEW:
            return (
                f"Borderline case requires human review. "
                f"Consensus score: {consensus_score:.2f}. "
                f"Votes: [{vote_summary}]"
            )

        return (
            f"Tribunal rejects execution. "
            f"Consensus score: {consensus_score:.2f}. "
            f"Votes: [{vote_summary}]"
        )
```

---

### FASE 2: Punishment Protocol Real

> Código detalhado para ReEducationHandler, RollbackHandler, e DeletionHandler
> (ver plano completo no arquivo original)

---

### FASE 3: SimuRA World Model (Dyna-Think Integration)

> Código detalhado para SimuRAWorldModel com integração Gemini
> (ver plano completo no arquivo original)

---

### FASE 4: HCL Analyzer com ML Real

> Código detalhado para HybridAnomalyDetector (SARIMA + IsolationForest)
> (ver plano completo no arquivo original)

---

## 📊 MÉTRICAS DE SUCESSO

### KPIs para Validação

| Métrica | Baseline (Atual) | Target | Método de Medição |
|---------|------------------|--------|-------------------|
| **Truth Detection Accuracy** | ~30% (keyword) | ≥85% | Benchmark vs ground truth |
| **Wisdom Context Depth** | ~40% (pattern) | ≥75% | Human eval + automated |
| **Justice Role Compliance** | ~50% (keyword) | ≥95% | Authorization matrix tests |
| **Ensemble Consensus F1** | N/A | ≥0.90 | Cross-validation |
| **Anomaly Detection Precision** | ~60% (static) | ≥85% | Real incident correlation |
| **SimuRA Prediction Accuracy** | ~40% (heuristic) | ≥70% | A/B test vs actual |
| **Punishment Execution Rate** | 0% (string only) | 100% | Integration tests |

---

## 🔄 ORDEM DE IMPLEMENTAÇÃO

### Sprint 1: Fundação dos Juízes (Semana 1-2)

1. **Dia 1-2**: Base interfaces (`judges/base.py`)
2. **Dia 3-4**: VERITAS (Truth Judge) + Semantic Entropy detector
3. **Dia 5-6**: SOPHIA (Wisdom Judge) + Context Depth analyzer
4. **Dia 7-8**: DIKĒ (Justice Judge) + Role Matrix
5. **Dia 9-10**: Ensemble Arbiter + Integration tests

### Sprint 2: Punishment & Memory (Semana 3-4)

1. **Dia 11-12**: Punishment handlers (Re-education, Rollback, Deletion)
2. **Dia 13-14**: Memory client real integration
3. **Dia 15-16**: Reflector refactor (usar novos juízes)
4. **Dia 17-18**: API updates + Integration tests
5. **Dia 19-20**: End-to-end validation

### Sprint 3: SimuRA & ML (Semana 5-6)

1. **Dia 21-22**: World Model Gemini integration
2. **Dia 23-24**: Hybrid Anomaly Detector (SARIMA + IF)
3. **Dia 25-26**: HCL Analyzer refactor
4. **Dia 27-28**: Integration tests + Performance benchmarks
5. **Dia 29-30**: Documentation + Final validation

---

## 📚 REFERÊNCIAS CIENTÍFICAS

1. [Self-Reflection in LLM Agents](https://arxiv.org/pdf/2405.06682) - Metacognition effects
2. [Intrinsic Metacognitive Learning](https://arxiv.org/pdf/2506.05109) - Self-improvement framework
3. [Semantic Entropy for Hallucination](https://www.nature.com/articles/s41586-024-07421-0) - Nature 2024
4. [HaluCheck](https://www.sciencedirect.com/science/article/abs/pii/S0957417425003343) - Explainable verification
5. [Neuro-Symbolic AI 2024](https://arxiv.org/pdf/2501.05435) - Systematic review
6. [Dyna-Think](https://arxiv.org/html/2506.00320) - World model simulation
7. [Voting vs Consensus](https://arxiv.org/abs/2502.19130) - Multi-agent decision making
8. [KEDA](https://keda.sh/) - Kubernetes event-driven autoscaling
9. [Constitutional AI](https://arxiv.org/abs/2212.08073) - Anthropic's alignment approach
10. [Collective Constitutional AI](https://dl.acm.org/doi/10.1145/3630106.3658979) - FAccT 2024

---

## ✅ CONFORMIDADE COM CODE CONSTITUTION

### Checklist de Validação

- [ ] **Clarity Over Cleverness**: Código óbvio, bem documentado
- [ ] **Consistency is King**: Padrões uniformes em todos os arquivos
- [ ] **Simplicity at Scale**: YAGNI aplicado, sem over-engineering
- [ ] **Safety First**: Type hints 100%, validação de input
- [ ] **Measurable Quality**: Coverage ≥80%, métricas definidas
- [ ] **Sovereignty of Intent**: Zero agendas externas

### Arquivos < 400 Linhas

Cada arquivo será dividido para manter < 400 linhas:
- `veritas.py` (~300 linhas)
- `sophia.py` (~250 linhas)
- `dike.py` (~350 linhas)
- `arbiter.py` (~250 linhas)
- `executor.py` (~200 linhas por handler)

---

**Plano Aprovado Por**: Juan Carlos de Souza (Arquiteto-Chefe)
**Data**: 01/12/2025
**Versão**: 1.0
**Status**: PRONTO PARA EXECUÇÃO
