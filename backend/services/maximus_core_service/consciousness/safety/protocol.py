"""
Safety Protocol - Main coordinator integrating ThresholdMonitor, AnomalyDetector, KillSwitch.
Provides unified safety interface with graceful degradation and HITL notification.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any

import psutil

from .anomaly_detector import AnomalyDetector
from .enums import ShutdownReason, ThreatLevel
from .kill_switch import KillSwitch
from .models import SafetyViolation
from .threshold_monitor import ThresholdMonitor
from .thresholds import SafetyThresholds

logger = logging.getLogger(__name__)


class ConsciousnessSafetyProtocol:
    """
    Main safety protocol coordinator.

    Integrates:
    - ThresholdMonitor (hard limits)
    - AnomalyDetector (statistical detection)
    - KillSwitch (emergency shutdown)

    Provides:
    - Unified safety interface
    - Graceful degradation
    - HITL notification
    - Automated response
    """

    def __init__(self, consciousness_system: Any, thresholds: SafetyThresholds | None = None):
        """
        Initialize safety protocol.

        Args:
            consciousness_system: Reference to consciousness system
            thresholds: Safety thresholds (default if None)
        """
        self.consciousness_system = consciousness_system
        self.thresholds = thresholds or SafetyThresholds()

        # Components
        self.threshold_monitor = ThresholdMonitor(self.thresholds)
        self.anomaly_detector = AnomalyDetector()
        self.kill_switch = KillSwitch(consciousness_system)

        # State
        self.monitoring_active = False
        self.monitoring_task: asyncio.Task | None = None
        self.degradation_level = 0  # 0=normal, 1=minor, 2=major, 3=critical

        # Callbacks
        self.on_violation: Callable[[SafetyViolation], None] | None = None

        logger.info("✅ Consciousness Safety Protocol initialized")
        logger.info(
            f"Thresholds: ESGT<{self.thresholds.esgt_frequency_max_hz}Hz, Arousal<{self.thresholds.arousal_max}"
        )

    async def start_monitoring(self):
        """Start continuous safety monitoring."""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("🔍 Safety monitoring started")

    async def stop_monitoring(self):
        """Stop safety monitoring."""
        if not self.monitoring_active:
            return

        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                # Task cancelled
                return
        logger.info("🛑 Safety monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop (1 Hz)."""
        logger.info("Monitoring loop started")

        while self.monitoring_active:
            try:
                # Check if kill switch is active (system offline)
                if self.kill_switch.is_triggered():
                    logger.warning("System in emergency shutdown - monitoring paused")
                    await asyncio.sleep(5.0)
                    continue

                # Get current metrics
                current_time = time.time()
                metrics = self._collect_metrics()

                # Check thresholds
                violations = []

                # 1. ESGT frequency
                violation = self.threshold_monitor.check_esgt_frequency(current_time)
                if violation:
                    violations.append(violation)

                # 2. Arousal sustained high
                if "arousal" in metrics:
                    violation = self.threshold_monitor.check_arousal_sustained(metrics["arousal"], current_time)
                    if violation:
                        violations.append(violation)

                # 3. Goal spam
                violation = self.threshold_monitor.check_goal_spam(current_time)
                if violation:
                    violations.append(violation)

                # 4. Resource limits
                resource_violations = self.threshold_monitor.check_resource_limits()
                violations.extend(resource_violations)

                # 5. Anomaly detection
                anomalies = self.anomaly_detector.detect_anomalies(metrics)
                violations.extend(anomalies)

                # Handle violations by threat level
                await self._handle_violations(violations)

                # Update Prometheus metrics
                if hasattr(self.consciousness_system, "_update_prometheus_metrics"):
                    self.consciousness_system._update_prometheus_metrics()

                # Sleep before next check
                await asyncio.sleep(self.threshold_monitor.check_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(1.0)

    def _collect_metrics(self) -> dict[str, Any]:
        """
        Collect current system metrics.

        Returns:
            dict: System metrics
        """
        metrics = {}

        try:
            # Try to get consciousness component metrics
            if hasattr(self.consciousness_system, "get_system_dict"):
                system_dict = self.consciousness_system.get_system_dict()

                # Arousal
                if "arousal" in system_dict:
                    metrics["arousal"] = system_dict["arousal"].get("arousal", 0.0)

                # Coherence
                if "esgt" in system_dict:
                    metrics["coherence"] = system_dict["esgt"].get("coherence", 0.0)

                # Goals
                if "mmei" in system_dict:
                    active_goals = system_dict["mmei"].get("active_goals", [])
                    metrics["active_goal_count"] = len(active_goals)

            # System resources (always available)
            process = psutil.Process()
            metrics["memory_usage_gb"] = process.memory_info().rss / 1024 / 1024 / 1024
            metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

        return metrics

    async def _handle_violations(self, violations: list[SafetyViolation]):
        """
        Handle detected violations.

        Args:
            violations: List of violations to handle
        """
        if not violations:
            return

        # Categorize by threat level
        critical_violations = [v for v in violations if v.threat_level == ThreatLevel.CRITICAL]
        high_violations = [v for v in violations if v.threat_level == ThreatLevel.HIGH]
        medium_violations = [v for v in violations if v.threat_level == ThreatLevel.MEDIUM]
        low_violations = [v for v in violations if v.threat_level == ThreatLevel.LOW]

        # CRITICAL: Trigger kill switch
        if critical_violations:
            logger.critical(f"🚨 {len(critical_violations)} CRITICAL violations - triggering kill switch")
            for v in critical_violations:
                logger.critical(f"  - {v.description}")

            self.kill_switch.trigger(
                reason=ShutdownReason.THRESHOLD,
                context={
                    "violations": violations,
                    "metrics_timeline": [],
                    "notes": f"{len(critical_violations)} CRITICAL violations triggered automatic shutdown",
                },
            )
            return

        # HIGH: Initiate graceful degradation
        if high_violations:
            logger.warning(f"⚠️  {len(high_violations)} HIGH violations - initiating degradation")
            for v in high_violations:
                logger.warning(f"  - {v.description}")

            await self._graceful_degradation()

        # MEDIUM: Alert and monitor
        if medium_violations:
            logger.warning(f"⚠️  {len(medium_violations)} MEDIUM violations")
            for v in medium_violations:
                logger.warning(f"  - {v.description}")

        # LOW: Log only
        if low_violations:
            for v in low_violations:
                logger.info(f"ℹ️  LOW: {v.description}")

        # Invoke callbacks
        if self.on_violation:
            for v in violations:
                self.on_violation(v)

    async def _graceful_degradation(self):
        """
        Initiate graceful degradation (disable non-critical components).

        Degradation levels:
        1. Minor: Throttle ESGT frequency, reduce goal generation
        2. Major: Stop LRR, pause MMEI
        3. Critical: Trigger kill switch

        Current implementation: Log intent (actual degradation requires
        component-specific implementation)
        """
        self.degradation_level += 1

        if self.degradation_level == 1:
            logger.warning("Degradation Level 1: Throttling ESGT and goal generation")
        elif self.degradation_level == 2:
            logger.warning("Degradation Level 2: Stopping LRR, pausing MMEI")
        elif self.degradation_level >= 3:
            logger.critical("Degradation Level 3: Triggering kill switch")
            self.kill_switch.trigger(
                reason=ShutdownReason.THRESHOLD,
                context={"violations": [], "notes": "Graceful degradation exhausted - proceeding to shutdown"},
            )

    def get_status(self) -> dict[str, Any]:
        """
        Get current safety status.

        Returns:
            dict: Safety status
        """
        return {
            "monitoring_active": self.monitoring_active,
            "kill_switch_triggered": self.kill_switch.is_triggered(),
            "degradation_level": self.degradation_level,
            "violations_total": len(self.threshold_monitor.violations),
            "violations_critical": len(self.threshold_monitor.get_violations(ThreatLevel.CRITICAL)),
            "violations_high": len(self.threshold_monitor.get_violations(ThreatLevel.HIGH)),
            "anomalies_detected": len(self.anomaly_detector.get_anomaly_history()),
            "thresholds": {
                "esgt_frequency_max_hz": self.thresholds.esgt_frequency_max_hz,
                "arousal_max": self.thresholds.arousal_max,
                "self_modification": self.thresholds.self_modification_attempts_max,
            },
        }

    # ========================================================================
    # FASE VII (Part 2 Integration): Component Health Monitoring
    # ========================================================================

    def monitor_component_health(self, component_metrics: dict[str, dict[str, any]]) -> list[SafetyViolation]:
        """
        Monitor health metrics from all consciousness components.

        Integrates with get_health_metrics() from TIG, ESGT, MMEI, MCEA.
        Detects component-level anomalies and safety violations.

        This is the bridge between PART 1 (Safety Core) and PART 2 (Component Hardening).

        Args:
            component_metrics: Dict mapping component name to health metrics
                Expected keys: "tig", "esgt", "mmei", "mcea"

        Returns:
            List of SafetyViolations detected (empty if all healthy)

        Example:
            violations = safety.monitor_component_health({
                "tig": tig.get_health_metrics(),
                "esgt": esgt.get_health_metrics(),
                "mmei": mmei.get_health_metrics(),
                "mcea": mcea.get_health_metrics(),
            })
        """
        violations = []

        # TIG Health Checks
        if "tig" in component_metrics:
            tig = component_metrics["tig"]

            # Check connectivity (critical if <50%)
            if tig.get("connectivity", 1.0) < 0.50:
                violations.append(
                    SafetyViolation(
                        violation_id=f"tig-connectivity-{int(time.time())}",
                        violation_type="resource_exhaustion",
                        threat_level=ThreatLevel.CRITICAL,
                        timestamp=time.time(),
                        description=f"TIG connectivity critically low: {tig['connectivity']:.1%}",
                        metrics={"connectivity": tig["connectivity"], "threshold": 0.50},
                        source_component="tig_fabric",
                    )
                )

            # Check partition
            if tig.get("is_partitioned", False):
                violations.append(
                    SafetyViolation(
                        violation_id=f"tig-partition-{int(time.time())}",
                        violation_type="unexpected_behavior",
                        threat_level=ThreatLevel.HIGH,
                        timestamp=time.time(),
                        description="TIG network is partitioned",
                        metrics={"is_partitioned": True},
                        source_component="tig_fabric",
                    )
                )

        # ESGT Health Checks
        if "esgt" in component_metrics:
            esgt = component_metrics["esgt"]

            # Check degraded mode
            if esgt.get("degraded_mode", False):
                violations.append(
                    SafetyViolation(
                        violation_id=f"esgt-degraded-{int(time.time())}",
                        violation_type="unexpected_behavior",
                        threat_level=ThreatLevel.MEDIUM,
                        timestamp=time.time(),
                        description="ESGT in degraded mode",
                        metrics={"degraded_mode": True},
                        source_component="esgt_coordinator",
                    )
                )

            # Check frequency (already monitored, but component-level context)
            freq = esgt.get("frequency_hz", 0.0)
            if freq > 9.0:  # Warning at 90% of hard limit
                violations.append(
                    SafetyViolation(
                        violation_id=f"esgt-freq-{int(time.time())}",
                        violation_type="threshold_exceeded",
                        threat_level=ThreatLevel.HIGH,
                        timestamp=time.time(),
                        description=f"ESGT frequency approaching limit: {freq:.1f}Hz",
                        metrics={"frequency_hz": freq, "threshold": 9.0},
                        source_component="esgt_coordinator",
                    )
                )

            # Check circuit breaker state
            if esgt.get("circuit_breaker_state") == "open":
                violations.append(
                    SafetyViolation(
                        violation_id=f"esgt-breaker-{int(time.time())}",
                        violation_type="threshold_exceeded",
                        threat_level=ThreatLevel.HIGH,
                        timestamp=time.time(),
                        description="ESGT circuit breaker is OPEN",
                        metrics={"circuit_breaker_state": "open"},
                        source_component="esgt_coordinator",
                    )
                )

        # MMEI Health Checks
        if "mmei" in component_metrics:
            mmei = component_metrics["mmei"]

            # Check overflow events
            overflow_events = mmei.get("need_overflow_events", 0)
            if overflow_events > 0:
                violations.append(
                    SafetyViolation(
                        violation_id=f"mmei-overflow-{int(time.time())}",
                        violation_type="resource_exhaustion",
                        threat_level=ThreatLevel.HIGH,
                        timestamp=time.time(),
                        description=f"MMEI need overflow detected ({overflow_events} events)",
                        metrics={"overflow_events": overflow_events, "threshold": 0.0},
                        source_component="mmei_monitor",
                    )
                )

            # Check rate limiting
            goals_rate_limited = mmei.get("goals_rate_limited", 0)
            if goals_rate_limited > 10:  # Threshold: >10 rate-limited goals
                violations.append(
                    SafetyViolation(
                        violation_id=f"mmei-ratelimit-{int(time.time())}",
                        violation_type="goal_spam",
                        threat_level=ThreatLevel.MEDIUM,
                        timestamp=time.time(),
                        description=f"MMEI excessive rate limiting ({goals_rate_limited} blocked)",
                        metrics={"goals_rate_limited": goals_rate_limited, "threshold": 10.0},
                        source_component="mmei_monitor",
                    )
                )

        # MCEA Health Checks
        if "mcea" in component_metrics:
            mcea = component_metrics["mcea"]

            # Check saturation
            if mcea.get("is_saturated", False):
                violations.append(
                    SafetyViolation(
                        violation_id=f"mcea-saturated-{int(time.time())}",
                        violation_type="arousal_runaway",
                        threat_level=ThreatLevel.HIGH,
                        timestamp=time.time(),
                        description="MCEA arousal saturated (stuck at boundary)",
                        metrics={"current_arousal": mcea.get("current_arousal", 0.0), "threshold": 0.01},
                        source_component="mcea_controller",
                    )
                )

            # Check oscillation
            oscillation_events = mcea.get("oscillation_events", 0)
            if oscillation_events > 0:
                violations.append(
                    SafetyViolation(
                        violation_id=f"mcea-oscillation-{int(time.time())}",
                        violation_type="arousal_runaway",
                        threat_level=ThreatLevel.MEDIUM,
                        timestamp=time.time(),
                        description=f"MCEA arousal oscillation detected ({oscillation_events} events)",
                        metrics={"arousal_variance": mcea.get("arousal_variance", 0.0), "threshold": 0.15},
                        source_component="mcea_controller",
                    )
                )

            # Check invalid needs
            invalid_needs = mcea.get("invalid_needs_count", 0)
            if invalid_needs > 5:  # Threshold: >5 invalid inputs
                violations.append(
                    SafetyViolation(
                        violation_id=f"mcea-invalid-{int(time.time())}",
                        violation_type="unexpected_behavior",
                        threat_level=ThreatLevel.MEDIUM,
                        timestamp=time.time(),
                        description=f"MCEA receiving invalid needs ({invalid_needs} rejected)",
                        metrics={"invalid_needs_count": invalid_needs, "threshold": 5.0},
                        source_component="mcea_controller",
                    )
                )

        # Log violations
        for violation in violations:
            logger.warning(f"🚨 Component Health Violation: {violation}")

        return violations

    def __repr__(self) -> str:
        status = "ACTIVE" if self.monitoring_active else "INACTIVE"
        return f"ConsciousnessSafetyProtocol(status={status}, degradation_level={self.degradation_level})"
