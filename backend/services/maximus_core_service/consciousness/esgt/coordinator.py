"""
ESGT Coordinator - Global Workspace Ignition Protocol.

Implements GWD consciousness emergence via 5-phase protocol:
PREPARE → SYNCHRONIZE → BROADCAST → SUSTAIN → DISSOLVE

Based on Dehaene et al. (2021) Global Workspace Dynamics theory.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, TYPE_CHECKING

import numpy as np

from consciousness.esgt.kuramoto import (
    KuramotoNetwork,
    OscillatorConfig,
)
from consciousness.tig.fabric import TIGFabric, CircuitBreaker
from consciousness.tig.sync import PTPCluster

from .attention_helpers import (
    compute_salience_from_attention as _compute_salience,
    build_content_from_attention as _build_content,
)
# Re-exports for backward compatibility (tests import from coordinator)
from .enums import ESGTPhase, SalienceLevel
from .models import SalienceScore, TriggerConditions, ESGTEvent

__all__ = ["ESGTCoordinator", "ESGTPhase", "SalienceLevel", "SalienceScore", "TriggerConditions", "ESGTEvent"]
from .pfc_integration import process_social_signal_through_pfc
from .safety import FrequencyLimiter

if TYPE_CHECKING:  # pragma: no cover
    from consciousness.mea.attention_schema import AttentionState
    from consciousness.mea.boundary_detector import BoundaryAssessment
    from consciousness.mea.self_model import IntrospectiveSummary


class ESGTCoordinator:
    """
    Coordinates ESGT ignition events for consciousness emergence.

    Implements GWD protocol: monitors salience, evaluates triggers,
    initiates synchronization, manages 5-phase protocol, records metrics.
    """

    # FASE VII (Safety Hardening): Hard limits
    MAX_FREQUENCY_HZ = 10.0
    MAX_CONCURRENT_EVENTS = 3
    MIN_COHERENCE_THRESHOLD = 0.50
    DEGRADED_MODE_THRESHOLD = 0.65

    def __init__(
        self,
        tig_fabric: TIGFabric,
        ptp_cluster: PTPCluster | None = None,
        triggers: TriggerConditions | None = None,
        kuramoto_config: OscillatorConfig | None = None,
        coordinator_id: str = "esgt-coordinator",
        prefrontal_cortex: Any | None = None,
    ):
        self.coordinator_id = coordinator_id
        self.tig = tig_fabric
        self.ptp = ptp_cluster
        self.triggers = triggers or TriggerConditions()
        self.kuramoto_config = kuramoto_config or OscillatorConfig()

        # Kuramoto network for phase synchronization
        self.kuramoto = KuramotoNetwork(self.kuramoto_config)

        # ESGT state
        self.active_event: ESGTEvent | None = None
        self.event_history: list[ESGTEvent] = []
        self.last_esgt_time: float = 0.0

        # Monitoring
        self._running: bool = False
        self._monitor_task: asyncio.Task | None = None

        # Performance tracking
        self.total_events: int = 0
        self.successful_events: int = 0

        # FASE VII (Safety Hardening): Frequency tracking
        from collections import deque

        self.ignition_timestamps: deque = deque(maxlen=100)
        self.frequency_limiter = FrequencyLimiter(self.MAX_FREQUENCY_HZ)

        # FASE VII (Safety Hardening): Concurrent event tracking
        self.active_events: set[str] = set()
        self.max_concurrent = self.MAX_CONCURRENT_EVENTS

        # FASE VII (Safety Hardening): Coherence monitoring
        self.coherence_history: deque = deque(maxlen=10)
        self.degraded_mode = False

        # FASE VII (Safety Hardening): Circuit breaker for ignition
        self.ignition_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=10.0)

        # TRACK 1: PrefrontalCortex integration for social cognition
        self.pfc = prefrontal_cortex
        self.social_signals_processed = 0

    async def start(self) -> None:
        """Start ESGT coordinator."""
        if self._running:
            return

        self._running = True

        # Initialize Kuramoto oscillators for all TIG nodes
        for node_id in self.tig.nodes.keys():
            self.kuramoto.add_oscillator(node_id, self.kuramoto_config)

        print("🧠 ESGT Coordinator started - monitoring for ignition triggers")

    async def stop(self) -> None:
        """Stop coordinator."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            
        # Break circular references
        self.tig = None  # type: ignore
        self.pfc = None
        self.event_history.clear()
        self.active_events.clear()

    def _create_blocked_event(self, content_source: str, target_coherence: float, reason: str) -> ESGTEvent:
        """Create a blocked/failed event for tracking."""
        event = ESGTEvent(
            event_id=f"esgt-blocked-{int(time.time() * 1000):016d}",
            timestamp_start=time.time(),
            content={},
            content_source=content_source,
            target_coherence=target_coherence,
        )
        event.transition_phase(ESGTPhase.FAILED)
        event.finalize(success=False, reason=reason)
        return event

    async def initiate_esgt(
        self,
        salience: SalienceScore,
        content: dict[str, Any],
        content_source: str = "unknown",
        target_duration_ms: float = 200.0,
        target_coherence: float = 0.70,
    ) -> ESGTEvent:
        """Initiate a transient global synchronization event with safety checks."""
        # FASE VII: Check 1 - Frequency limiter (HARD LIMIT)
        if not await self.frequency_limiter.allow():
            print("🛑 ESGT: Ignition BLOCKED by frequency limiter")
            return self._create_blocked_event(content_source, target_coherence, "frequency_limit_exceeded")

        # FASE VII: Check 2 - Concurrent event limit (HARD LIMIT)
        if len(self.active_events) >= self.max_concurrent:
            print(f"🛑 ESGT: Ignition BLOCKED - {len(self.active_events)} concurrent events")
            return self._create_blocked_event(content_source, target_coherence, "max_concurrent_events")

        # FASE VII: Check 3 - Circuit breaker
        if self.ignition_breaker.is_open():
            print("🛑 ESGT: Ignition BLOCKED by circuit breaker")
            return self._create_blocked_event(content_source, target_coherence, "circuit_breaker_open")

        # FASE VII: Check 4 - Degraded mode (higher salience threshold)
        if self.degraded_mode:
            total_salience = salience.compute_total()
            if total_salience < 0.85:  # Higher threshold in degraded mode
                print(f"⚠️  ESGT: Low salience {total_salience:.2f} in degraded mode")
                return self._create_blocked_event(content_source, target_coherence, "degraded_mode_low_salience")

        event = ESGTEvent(
            event_id=f"esgt-{int(time.time() * 1000):016d}",
            timestamp_start=time.time(),
            content=content,
            content_source=content_source,
            target_coherence=target_coherence,
        )

        # Increment total events (all attempts, not just successful)
        self.total_events += 1

        # Validate trigger conditions
        trigger_result, failure_reason = await self._check_triggers(salience)
        if not trigger_result:
            event.transition_phase(ESGTPhase.FAILED)
            event.finalize(success=False, reason=failure_reason)
            self.event_history.append(event)  # Record failed attempt
            return event

        try:
            # PHASE 1: PREPARE
            event.transition_phase(ESGTPhase.PREPARE)
            prepare_start = time.time()

            participating = await self._recruit_nodes(content)
            event.participating_nodes = participating
            event.node_count = len(participating)

            event.prepare_latency_ms = (time.time() - prepare_start) * 1000

            if len(participating) < self.triggers.min_available_nodes:
                event.finalize(success=False, reason="Insufficient nodes recruited")
                return event

            # PHASE 2: SYNCHRONIZE
            event.transition_phase(ESGTPhase.SYNCHRONIZE)
            sync_start = time.time()

            # Build topology for recruited nodes
            topology = self._build_topology(participating)

            # Run Kuramoto synchronization
            dynamics = await self.kuramoto.synchronize(
                topology=topology,
                duration_ms=300.0,  # Max 300ms to achieve sync (allows time for simulation)
                target_coherence=target_coherence,
                dt=0.005,
            )

            event.sync_latency_ms = (time.time() - sync_start) * 1000
            event.time_to_sync_ms = dynamics.time_to_sync * 1000 if dynamics.time_to_sync else None

            # Check if synchronization achieved
            coherence = self.kuramoto.get_coherence()
            if not coherence or not coherence.is_conscious_level():
                event.finalize(
                    success=False, reason=f"Sync failed: coherence={coherence.order_parameter if coherence else 0:.3f}"
                )
                return event

            # Record peak coherence achieved during sync
            event.achieved_coherence = coherence.order_parameter

            # PHASE 3: BROADCAST
            event.transition_phase(ESGTPhase.BROADCAST)
            broadcast_start = time.time()

            # Enter ESGT mode on TIG fabric
            await self.tig.enter_esgt_mode()

            # TRACK 1: Process social signals through PFC if available
            counter = [self.social_signals_processed]
            pfc_response = await process_social_signal_through_pfc(self.pfc, content, counter)
            self.social_signals_processed = counter[0]
            if pfc_response:
                # Enrich content with compassionate action
                content["pfc_action"] = pfc_response
                print(f"🧠 PFC: Generated compassionate action - {pfc_response.get('action', 'unknown')}")

            # Global broadcast of conscious content
            message = {
                "type": "esgt_content",
                "event_id": event.event_id,
                "content": content,
                "coherence": coherence.order_parameter,
                "timestamp": event.timestamp_start,
            }

            await self.tig.broadcast_global(message, priority=10)

            event.broadcast_latency_ms = (time.time() - broadcast_start) * 1000

            # PHASE 4: SUSTAIN
            event.transition_phase(ESGTPhase.SUSTAIN)

            # Sustain synchronization for target duration
            await self._sustain_coherence(event, target_duration_ms, topology)

            # PHASE 5: DISSOLVE
            event.transition_phase(ESGTPhase.DISSOLVE)

            # Graceful desynchronization
            await self._dissolve_event(event)

            # Exit ESGT mode
            await self.tig.exit_esgt_mode()

            # Finalize (use max coherence from history, not post-dissolve value)
            if event.coherence_history:
                event.achieved_coherence = max(event.coherence_history)
            event.transition_phase(ESGTPhase.COMPLETE)
            event.finalize(success=True)

            # Record
            self.event_history.append(event)
            self.last_esgt_time = time.time()
            if event.was_successful():
                self.successful_events += 1

            print(
                f"✅ ESGT {event.event_id}: coherence={event.achieved_coherence:.3f}, "
                f"duration={event.total_duration_ms:.1f}ms, nodes={event.node_count}"
            )

            return event

        except Exception as e:
            event.transition_phase(ESGTPhase.FAILED)
            event.finalize(success=False, reason=str(e))
            self.event_history.append(event)  # Record failed attempt
            print(f"❌ ESGT {event.event_id} failed: {e}")
            return event

    def compute_salience_from_attention(
        self,
        attention_state: "AttentionState",
        boundary: "BoundaryAssessment | None" = None,
        arousal_level: float | None = None,
    ) -> SalienceScore:
        """Build a SalienceScore from MEA attention outputs."""
        return _compute_salience(attention_state, boundary, arousal_level)

    def build_content_from_attention(
        self,
        attention_state: "AttentionState",
        summary: "IntrospectiveSummary | None" = None,
    ) -> dict[str, Any]:
        """Construct ESGT content payload using MEA attention and self narrative."""
        return _build_content(attention_state, summary)

    async def _check_triggers(self, salience: SalienceScore) -> tuple[bool, str]:
        """Check if all trigger conditions are met. Returns (success, failure_reason)."""
        # Salience check
        if not self.triggers.check_salience(salience):
            return False, f"Salience too low ({salience.compute_total():.2f} < {self.triggers.min_salience:.2f})"

        # Resource check
        tig_metrics = self.tig.get_metrics()
        tig_latency = tig_metrics.avg_latency_us / 1000.0  # Convert to ms
        available_nodes = sum(1 for node in self.tig.nodes.values() if node.node_state.value in ["active", "esgt_mode"])
        cpu_capacity = 0.60  # Simulated - would query actual metrics

        if not self.triggers.check_resources(
            tig_latency_ms=tig_latency, available_nodes=available_nodes, cpu_capacity=cpu_capacity
        ):
            return False, f"Insufficient resources (nodes={available_nodes}, latency={tig_latency:.1f}ms)"

        # Temporal gating
        time_since_last = time.time() - self.last_esgt_time if self.last_esgt_time > 0 else float("inf")
        recent_count = sum(1 for e in self.event_history[-10:] if time.time() - e.timestamp_start < 1.0)

        if not self.triggers.check_temporal_gating(time_since_last, recent_count):
            return (
                False,
                f"Refractory period violation (time_since_last={time_since_last * 1000:.1f}ms < {self.triggers.refractory_period_ms:.1f}ms)",
            )

        # Arousal check (simulated - would query MCEA)
        arousal = 0.70  # Simulated
        if not self.triggers.check_arousal(arousal):
            return False, f"Arousal too low ({arousal:.2f} < {self.triggers.min_arousal_level:.2f})"

        return True, ""

    async def _recruit_nodes(self, content: dict[str, Any]) -> set[str]:
        """
        Recruit participating nodes for ESGT.

        Selection based on:
        - Relevance to content
        - Current load
        - Connectivity quality
        """
        recruited = set()

        for node_id, node in self.tig.nodes.items():
            # For now, recruit all active nodes
            # In full implementation, would use content-based selection
            if node.node_state.value in ["active", "esgt_mode"]:
                recruited.add(node_id)

        return recruited

    def _build_topology(self, node_ids: set[str]) -> dict[str, list[str]]:
        """Build connectivity topology for Kuramoto network."""
        topology = {}

        for node_id in node_ids:
            node = self.tig.nodes.get(node_id)
            if node:
                # Get neighbors that are also participating
                neighbors = [
                    conn.remote_node_id
                    for conn in node.connections.values()
                    if conn.active and conn.remote_node_id in node_ids
                ]
                topology[node_id] = neighbors

        return topology

    async def _sustain_coherence(self, event: ESGTEvent, duration_ms: float, topology: dict[str, list[str]]) -> None:
        """
        Sustain synchronization for target duration.

        Continuously updates Kuramoto dynamics and monitors coherence.
        """
        start_time = time.time()
        duration_s = duration_ms / 1000.0

        while (time.time() - start_time) < duration_s:
            # Update network
            self.kuramoto.update_network(topology, dt=0.005)

            # Record coherence
            coherence = self.kuramoto.get_coherence()
            if coherence:
                event.coherence_history.append(coherence.order_parameter)

            # Small yield
            await asyncio.sleep(0.005)

    async def _dissolve_event(self, event: ESGTEvent) -> None:
        """Gracefully dissolve synchronization."""
        # Reduce coupling strength gradually
        for osc in self.kuramoto.oscillators.values():
            osc.config.coupling_strength *= 0.5

        # Continue for 50ms with reduced coupling
        topology = self._build_topology(event.participating_nodes)

        for _ in range(10):  # 10 x 5ms = 50ms
            self.kuramoto.update_network(topology, dt=0.005)
            await asyncio.sleep(0.005)

        # Reset oscillators
        self.kuramoto.reset_all()

    def get_success_rate(self) -> float:
        """Get percentage of successful ESGT events."""
        if self.total_events == 0:
            return 0.0
        return self.successful_events / self.total_events

    def get_recent_coherence(self, window: int = 10) -> float:
        """Get average coherence of recent events."""
        recent = self.event_history[-window:]
        if not recent:
            return 0.0

        coherences = [e.achieved_coherence for e in recent if e.success]
        return float(np.mean(coherences)) if coherences else 0.0

    def _enter_degraded_mode(self) -> None:
        """Enter degraded mode - reduce ignition rate due to low coherence."""
        self.degraded_mode = True
        self.max_concurrent = 1
        print("⚠️  ESGT: Entering DEGRADED MODE - reducing ignition rate due to low coherence")

    def _exit_degraded_mode(self) -> None:
        """Exit degraded mode - restore normal operation when coherence improves."""
        self.degraded_mode = False
        self.max_concurrent = self.MAX_CONCURRENT_EVENTS
        print("✓ ESGT: Exiting DEGRADED MODE - coherence restored")

    def get_health_metrics(self) -> dict[str, Any]:
        """Get ESGT health metrics for Safety Core integration."""
        # Compute current frequency
        now = time.time()
        recent_ignitions = [
            t
            for t in self.ignition_timestamps
            if now - t < 1.0  # Last second
        ]
        current_frequency = len(recent_ignitions)

        # Compute average coherence
        avg_coherence = sum(self.coherence_history) / len(self.coherence_history) if self.coherence_history else 0.0

        return {
            "frequency_hz": current_frequency,
            "active_events": len(self.active_events),
            "degraded_mode": self.degraded_mode,
            "average_coherence": avg_coherence,
            "circuit_breaker_state": self.ignition_breaker.state,
            "total_events": self.total_events,
            "successful_events": self.successful_events,
        }

    def __repr__(self) -> str:
        return (
            f"ESGTCoordinator(id={self.coordinator_id}, "
            f"events={self.total_events}, "
            f"success_rate={self.get_success_rate():.1%}, "
            f"running={self._running})"
        )
