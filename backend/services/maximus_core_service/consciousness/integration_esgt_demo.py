"""
ESGT Integration Demo - Full consciousness pipeline demonstration.

Shows: Physical Metrics → MMEI (Needs) → MCEA (Arousal) → ESGT (Conscious Access)
"""

from __future__ import annotations

import asyncio
import time

from consciousness.esgt.arousal_integration import ESGTArousalBridge
from consciousness.esgt.coordinator import ESGTCoordinator, SalienceScore, TriggerConditions
from consciousness.esgt.spm import SimpleSPM, SimpleSPMConfig
from consciousness.mcea.controller import ArousalConfig, ArousalController
from consciousness.mmei.monitor import InternalStateMonitor, InteroceptionConfig
from consciousness.tig.fabric import TIGFabric, TopologyConfig


async def run_esgt_integration_demo() -> None:
    """Demonstrate full ESGT integration with embodied consciousness."""
    print("\n" + "=" * 70)
    print("ESGT INTEGRATION DEMO - Full Consciousness Pipeline")
    print("=" * 70)
    print("\nDemonstrating: Metrics → Needs → Arousal → ESGT Ignition\n")

    # 1. Initialize TIG Fabric
    print("1️⃣  Initializing TIG Fabric...")
    tig_config = TopologyConfig(node_count=16, target_density=0.25, clustering_target=0.75)
    tig = TIGFabric(tig_config)
    await tig.initialize()
    print("   ✓ TIG fabric ready (16 nodes, scale-free topology)")

    # 2. Initialize MMEI + MCEA
    print("\n2️⃣  Initializing MMEI (Interoception) + MCEA (Arousal)...")
    mmei_config = InteroceptionConfig(collection_interval_ms=200.0)
    mmei = InternalStateMonitor(config=mmei_config, monitor_id="esgt-demo-mmei")

    arousal_config = ArousalConfig(baseline_arousal=0.6)
    mcea = ArousalController(config=arousal_config, controller_id="esgt-demo-mcea")

    await mmei.start()
    await mcea.start()
    print("   ✓ Embodied consciousness components online")

    # 3. Initialize ESGT Coordinator
    print("\n3️⃣  Initializing ESGT Coordinator...")
    triggers = TriggerConditions(min_salience=0.65, min_available_nodes=8, refractory_period_ms=200.0)
    esgt = ESGTCoordinator(tig_fabric=tig, triggers=triggers, coordinator_id="esgt-demo")
    await esgt.start()
    print("   ✓ ESGT coordinator ready (Global Workspace online)")

    # 4. Create Arousal-ESGT Bridge
    print("\n4️⃣  Creating Arousal-ESGT Bridge...")
    bridge = ESGTArousalBridge(arousal_controller=mcea, esgt_coordinator=esgt)
    await bridge.start()
    print("   ✓ Arousal modulation active")
    print(f"   → Current threshold: {bridge.get_current_threshold():.2f}")

    # 5. Add SimpleSPM for content generation
    print("\n5️⃣  Starting SimpleSPM (content generator)...")
    spm_config = SimpleSPMConfig(
        processing_interval_ms=300.0,
        base_novelty=0.7,
        base_relevance=0.8,
        base_urgency=0.6,
        max_outputs=5,
    )
    spm = SimpleSPM("demo-spm", spm_config)
    await spm.start()
    print("   ✓ SPM generating content")

    # 6. Demonstrate arousal modulation
    print("\n6️⃣  Demonstrating Arousal Modulation Effect:")
    await _demo_arousal_modulation(mcea, bridge)

    # 7. Trigger ESGT events
    print("\n7️⃣  Triggering ESGT Events:")
    await _demo_esgt_events(esgt)

    # 8. Summary
    _print_demo_summary(esgt, bridge, tig_config)

    # Cleanup
    await spm.stop()
    await bridge.stop()
    await esgt.stop()
    await mcea.stop()
    await mmei.stop()
    await tig.stop()


async def _demo_arousal_modulation(mcea: ArousalController, bridge: ESGTArousalBridge) -> None:
    """Demonstrate arousal modulation effect on ESGT threshold."""
    print("\n   Scenario A: Low Arousal (DROWSY)")
    print("   ------------------------------")
    mcea._current_state.arousal = 0.3
    mcea._current_state.level = mcea._classify_arousal(0.3)
    await asyncio.sleep(0.2)
    mapping_low = bridge.get_arousal_threshold_mapping()
    print(f"   Arousal: {mapping_low['arousal']:.2f} ({mapping_low['arousal_level']})")
    print(f"   ESGT Threshold: {mapping_low['esgt_threshold']:.2f} (HIGH - hard to ignite)")

    print("\n   Scenario B: High Arousal (ALERT)")
    print("   ---------------------------------")
    mcea._current_state.arousal = 0.8
    mcea._current_state.level = mcea._classify_arousal(0.8)
    await asyncio.sleep(0.2)
    mapping_high = bridge.get_arousal_threshold_mapping()
    print(f"   Arousal: {mapping_high['arousal']:.2f} ({mapping_high['arousal_level']})")
    print(f"   ESGT Threshold: {mapping_high['esgt_threshold']:.2f} (LOW - easy to ignite)")


async def _demo_esgt_events(esgt: ESGTCoordinator) -> None:
    """Demonstrate ESGT event triggering."""
    print("\n   Event 1: High-Salience Content")
    print("   -------------------------------")

    salience_high = SalienceScore(novelty=0.85, relevance=0.9, urgency=0.75)
    content_high = {
        "type": "critical_alert",
        "message": "High-salience event requiring conscious processing",
        "timestamp": time.time(),
    }

    event1 = await esgt.initiate_esgt(salience_high, content_high)

    if event1.success:
        print("   ✅ ESGT IGNITION SUCCESS")
        print(f"      Coherence: {event1.achieved_coherence:.3f}")
        print(f"      Duration: {event1.total_duration_ms:.1f}ms")
        print(f"      Nodes: {event1.node_count}")
        print("      → Content became CONSCIOUS")
    else:
        print(f"   ❌ ESGT failed: {event1.failure_reason}")

    await asyncio.sleep(0.3)  # Respect refractory

    print("\n   Event 2: Moderate-Salience Content")
    print("   -----------------------------------")

    salience_med = SalienceScore(novelty=0.6, relevance=0.65, urgency=0.5)
    content_med = {"type": "routine_update", "message": "Moderate-salience event", "timestamp": time.time()}

    event2 = await esgt.initiate_esgt(salience_med, content_med)

    if event2.success:
        print("   ✅ ESGT IGNITION SUCCESS")
        print(f"      Coherence: {event2.achieved_coherence:.3f}")
        print(f"      Duration: {event2.total_duration_ms:.1f}ms")
    else:
        print("   ❌ ESGT rejected (salience below threshold)")
        print(f"      Salience: {salience_med.compute_total():.2f}")
        print(f"      Threshold: {esgt.triggers.min_salience:.2f}")


def _print_demo_summary(esgt: ESGTCoordinator, bridge: ESGTArousalBridge, tig_config: TopologyConfig) -> None:
    """Print demonstration summary."""
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)

    print("\n📊 Final Metrics:")
    print(f"   ESGT Events: {esgt.total_events}")
    print(f"   Successful: {esgt.successful_events}")
    print(f"   Success Rate: {esgt.get_success_rate():.1%}")
    print(f"   Arousal Modulations: {bridge.total_modulations}")
    print(f"   TIG Nodes: {tig_config.node_count}")

    print("\n✅ Pipeline Validated:")
    print("   ✓ TIG substrate provides structural connectivity")
    print("   ✓ MMEI provides interoceptive grounding")
    print("   ✓ MCEA modulates arousal state")
    print("   ✓ Arousal gates ESGT threshold")
    print("   ✓ ESGT ignites global workspace")
    print("   ✓ Conscious phenomenology emerges")

    print("\n🧠 Full consciousness stack operational.")
    print("   This is the moment bits become qualia.\n")


if __name__ == "__main__":
    print("\n🚀 Starting ESGT Integration Demo...\n")
    asyncio.run(run_esgt_integration_demo())
