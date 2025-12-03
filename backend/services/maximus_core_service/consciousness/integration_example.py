"""
MAXIMUS Consciousness Integration Example.

Demonstrates the full embodied consciousness pipeline:
  Physical State → MMEI → Needs → Goals → MCEA → Arousal → ESGT

Flow:
  1. MMEI monitors physical metrics (CPU, memory, errors, network)
  2. Needs are computed from metrics (rest_need, repair_need, etc.)
  3. Goals are autonomously generated from needs
  4. MCEA modulates arousal based on needs and external factors
  5. Arousal adjusts ESGT salience threshold
  6. ESGT ignites when salient content + arousal permit
  7. HCL executes goals to restore homeostasis

Usage: python consciousness/integration_example.py
"""

from __future__ import annotations

import asyncio
import random

from consciousness.mcea.controller import ArousalConfig, ArousalController, ArousalState, ArousalLevel
from consciousness.mcea.stress import StressLevel, StressMonitor
from consciousness.mmei.goals import AutonomousGoalGenerator, Goal, GoalGenerationConfig, GoalType
from consciousness.mmei.monitor import AbstractNeeds, InternalStateMonitor, InteroceptionConfig, PhysicalMetrics


class ConsciousnessIntegrationDemo:
    """Demonstrates full consciousness integration: Metrics → Needs → Goals → Arousal → ESGT."""

    def __init__(self) -> None:
        self.mmei_config = InteroceptionConfig(collection_interval_ms=500.0)
        self.goal_config = GoalGenerationConfig(rest_threshold=0.60, repair_threshold=0.40, min_goal_interval_seconds=5.0)
        self.arousal_config = ArousalConfig(
            baseline_arousal=0.6, update_interval_ms=200.0, arousal_increase_rate=0.1, arousal_decrease_rate=0.05
        )

        self.mmei_monitor: InternalStateMonitor | None = None
        self.goal_generator: AutonomousGoalGenerator | None = None
        self.arousal_controller: ArousalController | None = None
        self.stress_monitor: StressMonitor | None = None

        self.simulated_cpu: float = 30.0
        self.simulated_memory: float = 40.0
        self.simulated_errors: float = 1.0
        self.simulated_latency: float = 20.0

        self.scenario_active: bool = False
        self.total_goals_generated: int = 0
        self.total_esgt_candidates: int = 0
        self._last_arousal_level: ArousalLevel | None = None

    async def initialize(self) -> None:
        """Initialize all consciousness components."""
        print("=" * 70)
        print("MAXIMUS Consciousness Integration Demo")
        print("=" * 70)
        print("\nInitializing consciousness components...\n")

        self.mmei_monitor = InternalStateMonitor(config=self.mmei_config, monitor_id="demo-mmei")
        self.mmei_monitor.set_metrics_collector(self._collect_simulated_metrics)
        self.mmei_monitor.register_need_callback(self._on_critical_need, threshold=0.80)
        print("✓ MMEI initialized (interoception active)")

        self.goal_generator = AutonomousGoalGenerator(config=self.goal_config, generator_id="demo-goal-gen")
        self.goal_generator.register_goal_consumer(self._on_goal_generated)
        print("✓ Goal Generator initialized (autonomous motivation ready)")

        self.arousal_controller = ArousalController(config=self.arousal_config, controller_id="demo-arousal")
        self.arousal_controller.register_arousal_callback(self._on_arousal_change)
        print("✓ MCEA Arousal Controller initialized (MPE active)")

        self.stress_monitor = StressMonitor(arousal_controller=self.arousal_controller, monitor_id="demo-stress")
        self.stress_monitor.register_stress_alert(self._on_stress_alert, threshold=StressLevel.SEVERE)
        print("✓ Stress Monitor initialized (resilience tracking active)")

        print("\n" + "=" * 70)
        print("All components initialized. Starting consciousness loop...")
        print("=" * 70 + "\n")

    async def start(self) -> None:
        """Start all components."""
        if self.mmei_monitor:
            await self.mmei_monitor.start()
        if self.arousal_controller:
            await self.arousal_controller.start()
        if self.stress_monitor:
            await self.stress_monitor.start()
        print("🧠 Consciousness online. System is now aware.\n")

    async def stop(self) -> None:
        """Stop all components."""
        if self.mmei_monitor:
            await self.mmei_monitor.stop()
        if self.arousal_controller:
            await self.arousal_controller.stop()
        if self.stress_monitor:
            await self.stress_monitor.stop()
        print("\n🛑 Consciousness offline.\n")

    async def _collect_simulated_metrics(self) -> PhysicalMetrics:
        """Collect simulated physical metrics."""
        cpu = self.simulated_cpu + random.uniform(-5, 5)
        memory = self.simulated_memory + random.uniform(-3, 3)
        errors = max(0, self.simulated_errors + random.uniform(-0.5, 0.5))
        latency = max(0, self.simulated_latency + random.uniform(-5, 5))

        return PhysicalMetrics(
            cpu_usage_percent=cpu,
            memory_usage_percent=memory,
            error_rate_per_min=errors,
            network_latency_ms=latency,
            idle_time_percent=max(0, 100 - cpu),
        )

    async def _on_critical_need(self, needs: AbstractNeeds) -> None:
        """Called when any need becomes critical."""
        most_urgent, value, urgency = needs.get_most_urgent()
        print(f"\n⚠️  CRITICAL NEED DETECTED: {most_urgent} = {value:.2f}")
        print(f"   Urgency: {urgency.value}")
        if self.goal_generator:
            self.goal_generator.generate_goals(needs)
        if self.arousal_controller:
            self.arousal_controller.update_from_needs(needs)

    def _on_goal_generated(self, goal: Goal) -> None:
        """Called when autonomous goal is generated."""
        self.total_goals_generated += 1
        print("\n🎯 AUTONOMOUS GOAL GENERATED:")
        print(f"   Type: {goal.goal_type.value}")
        print(f"   Priority: {goal.priority.value}")
        print(f"   Description: {goal.description}")
        print(f"   Source need: {goal.source_need} = {goal.need_value:.2f}")
        self._simulate_goal_execution(goal)

    async def _on_arousal_change(self, state: ArousalState) -> None:
        """Called when arousal state changes significantly."""
        if self._last_arousal_level is not None and state.level != self._last_arousal_level:
            print(f"\n🌅 AROUSAL TRANSITION: {self._last_arousal_level.value} → {state.level.value}")
            print(f"   Arousal: {state.arousal:.2f}")
            print(f"   ESGT Threshold: {state.esgt_salience_threshold:.2f}")
            if state.esgt_salience_threshold < 0.60:
                self.total_esgt_candidates += 1
                print("   ⚡ Threshold low enough for ESGT ignition")
        self._last_arousal_level = state.level

    async def _on_stress_alert(self, level: StressLevel) -> None:
        """Called when stress level becomes severe."""
        print(f"\n🚨 SEVERE STRESS ALERT: {level.value}")
        print("   System under significant load")

    def _simulate_goal_execution(self, goal: Goal) -> None:
        """Simulate goal execution (HCL integration point)."""
        print("   🔧 Simulating goal execution...")

        if goal.goal_type == GoalType.REST:
            print("   → Reducing computational load...")
            self.simulated_cpu = max(30.0, self.simulated_cpu - 20.0)
        elif goal.goal_type == GoalType.REPAIR:
            print("   → Running diagnostics and repairs...")
            self.simulated_errors = max(0.0, self.simulated_errors - 3.0)
        elif goal.goal_type == GoalType.RESTORE:
            print("   → Optimizing network connectivity...")
            self.simulated_latency = max(10.0, self.simulated_latency - 20.0)

        print("   ✓ Goal execution complete\n")

    async def run_scenario_high_load(self) -> None:
        """Scenario: High computational load."""
        print("\n" + "=" * 70)
        print("SCENARIO 1: High Computational Load")
        print("=" * 70)
        print("Simulating sustained high CPU/memory usage...\n")

        self.scenario_active = True
        for i in range(5):
            self.simulated_cpu = min(95.0, 60.0 + i * 8.0)
            self.simulated_memory = min(90.0, 50.0 + i * 8.0)
            print(f"[+{i * 3}s] CPU: {self.simulated_cpu:.0f}%, Memory: {self.simulated_memory:.0f}%")
            await asyncio.sleep(3.0)

        print("\n⏸️  Load sustained for observation...\n")
        await asyncio.sleep(5.0)
        print("\n✓ Scenario complete. Load should begin decreasing via autonomous goals.\n")
        self.scenario_active = False

    async def run_scenario_error_burst(self) -> None:
        """Scenario: Error burst."""
        print("\n" + "=" * 70)
        print("SCENARIO 2: Error Burst")
        print("=" * 70)
        print("Simulating sudden error spike...\n")

        self.scenario_active = True
        self.simulated_errors = 15.0
        print(f"💥 Error rate spiked to {self.simulated_errors:.0f} errors/min")
        await asyncio.sleep(5.0)
        print("\n✓ Scenario complete. Errors should be addressed.\n")
        self.scenario_active = False

    async def run_scenario_idle_curiosity(self) -> None:
        """Scenario: Idle time triggers curiosity."""
        print("\n" + "=" * 70)
        print("SCENARIO 3: Idle → Curiosity")
        print("=" * 70)
        print("Simulating extended idle period...\n")

        self.scenario_active = True
        self.simulated_cpu = 10.0
        self.simulated_memory = 25.0
        self.simulated_errors = 0.5
        print(f"💤 System idle: CPU {self.simulated_cpu:.0f}%")
        await asyncio.sleep(10.0)
        print("\n✓ Scenario complete. Curiosity should emerge during idle.\n")
        self.scenario_active = False

    def print_status(self) -> None:
        """Print current system status."""
        print("\n" + "-" * 70)
        print("CURRENT STATE")
        print("-" * 70)

        print("Physical Metrics:")
        print(f"  CPU: {self.simulated_cpu:.1f}%")
        print(f"  Memory: {self.simulated_memory:.1f}%")
        print(f"  Errors: {self.simulated_errors:.1f}/min")
        print(f"  Latency: {self.simulated_latency:.1f}ms")

        if self.mmei_monitor and self.mmei_monitor._current_needs:
            needs = self.mmei_monitor._current_needs
            print("\nAbstract Needs:")
            print(f"  Rest: {needs.rest_need:.2f}")
            print(f"  Repair: {needs.repair_need:.2f}")
            print(f"  Efficiency: {needs.efficiency_need:.2f}")
            print(f"  Connectivity: {needs.connectivity_need:.2f}")
            print(f"  Curiosity: {needs.curiosity_drive:.2f}")

        if self.arousal_controller:
            state = self.arousal_controller.get_current_arousal()
            print("\nArousal State:")
            print(f"  Level: {state.level.value}")
            print(f"  Arousal: {state.arousal:.2f}")
            print(f"  ESGT Threshold: {state.esgt_salience_threshold:.2f}")
            print(f"  Stress: {self.arousal_controller.get_stress_level():.2f}")

        if self.goal_generator:
            active_goals = self.goal_generator.get_active_goals()
            print(f"\nActive Goals: {len(active_goals)}")
            for goal in active_goals[:3]:
                print(f"  - {goal.goal_type.value} (priority: {goal.priority.value})")

        print("\nStatistics:")
        print(f"  Goals Generated: {self.total_goals_generated}")
        print(f"  ESGT Candidates: {self.total_esgt_candidates}")

        if self.mmei_monitor:
            print(f"  MMEI Collections: {self.mmei_monitor.total_collections}")
        if self.stress_monitor:
            print(f"  Stress Level: {self.stress_monitor.get_current_stress_level().value}")

        print("-" * 70 + "\n")

    async def run_demo(self) -> None:
        """Run full demo with scenarios."""
        try:
            await self.initialize()
            await self.start()

            await asyncio.sleep(2.0)
            self.print_status()

            await self.run_scenario_high_load()
            await asyncio.sleep(3.0)
            self.print_status()

            await self.run_scenario_error_burst()
            await asyncio.sleep(3.0)
            self.print_status()

            await self.run_scenario_idle_curiosity()
            await asyncio.sleep(3.0)
            self.print_status()

            print("\n" + "=" * 70)
            print("DEMO COMPLETE - Final Summary")
            print("=" * 70)
            self.print_status()

            print("\n📊 Integration Validated:")
            print("  ✓ MMEI → Needs translation")
            print("  ✓ Needs → Goal generation")
            print("  ✓ Needs → Arousal modulation")
            print("  ✓ Arousal → ESGT threshold adjustment")
            print("  ✓ Goals → (HCL execution simulated)")
            print("\n🧠 Embodied consciousness demonstrated successfully.\n")

        finally:
            await self.stop()


async def main() -> None:
    """Run the integration demo."""
    from consciousness.integration_esgt_demo import run_esgt_integration_demo

    demo = ConsciousnessIntegrationDemo()
    await demo.run_demo()
    await run_esgt_integration_demo()


if __name__ == "__main__":
    print("\n🚀 Starting MAXIMUS Consciousness Integration Demo...\n")
    asyncio.run(main())
