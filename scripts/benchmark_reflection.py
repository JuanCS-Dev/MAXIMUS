#!/usr/bin/env python3
"""
Benchmark Script - Async Reflection Performance
================================================

Validates async reflection performance improvement.

Target: 355ms → <100ms (7x faster)
"""

import asyncio
import time
from typing import List
from statistics import mean, stdev

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.shared.reflector_client import (
    ReflectorClient,
    PrioritizedReflectorClient,
    ReflectionPriority
)
from backend.services.metacognitive_reflector.models.reflection import ExecutionLog
from datetime import datetime
from uuid import uuid4


async def benchmark_sync_reflection(iterations: int = 100) -> List[float]:
    """Benchmark synchronous reflection."""
    print(f"\n📊 Benchmarking SYNC reflection ({iterations} iterations)...")
    
    client = ReflectorClient()
    latencies: List[float] = []
    
    for i in range(iterations):
        log = ExecutionLog(
            trace_id=f"sync-{uuid4().hex[:8]}",
            agent_id="benchmark_agent",
            task=f"Benchmark task {i}",
            action="Testing sync reflection",
            outcome="Success",
            reasoning_trace="Benchmark test",
            timestamp=datetime.now()
        )
        
        start = time.perf_counter()
        try:
            await client.submit_log(log)
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies.append(elapsed_ms)
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    await client.close()
    return latencies


async def benchmark_async_reflection(iterations: int = 100) -> List[float]:
    """Benchmark async reflection."""
    print(f"\n📊 Benchmarking ASYNC reflection ({iterations} iterations)...")
    
    client = PrioritizedReflectorClient()
    await client.start()
    
    submission_latencies: List[float] = []
    
    for i in range(iterations):
        log = ExecutionLog(
            trace_id=f"async-{uuid4().hex[:8]}",
            agent_id="benchmark_agent",
            task=f"Benchmark task {i}",
            action="Testing async reflection",
            outcome="Success",
            reasoning_trace="Benchmark test",
            timestamp=datetime.now()
        )
        
        start = time.perf_counter()
        try:
            await client.submit_log_async(log, priority=ReflectionPriority.HIGH)
            elapsed_ms = (time.perf_counter() - start) * 1000
            submission_latencies.append(elapsed_ms)
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Wait for queue to process
    print("  ⏳ Waiting for background processing...")
    await asyncio.sleep(2)
    
    await client.stop()
    return submission_latencies


def print_stats(name: str, latencies: List[float], target_ms: float):
    """Print statistics."""
    if not latencies:
        print(f"\n❌ {name}: No data")
        return
    
    avg = mean(latencies)
    std = stdev(latencies) if len(latencies) > 1 else 0
    p50 = sorted(latencies)[len(latencies) // 2]
    p95 = sorted(latencies)[int(len(latencies) * 0.95)]
    p99 = sorted(latencies)[int(len(latencies) * 0.99)]
    
    passed = avg < target_ms
    status = "✅ PASS" if passed else "❌ FAIL"
    
    print(f"\n{status} {name} Performance:")
    print(f"  Average:    {avg:6.2f}ms (target: <{target_ms}ms)")
    print(f"  Std Dev:    {std:6.2f}ms")
    print(f"  Median (p50): {p50:6.2f}ms")
    print(f"  p95:        {p95:6.2f}ms")
    print(f"  p99:        {p99:6.2f}ms")
    print(f"  Min:        {min(latencies):6.2f}ms")
    print(f"  Max:        {max(latencies):6.2f}ms")


async def main():
    """Run benchmarks."""
    print("="*60)
    print("🚀 ASYNC REFLECTION BENCHMARK")
    print("="*60)
    print(f"Target: 355ms → <100ms (7x improvement)")
    
    iterations = 100
    
    # Benchmark sync (baseline)
    sync_latencies = await benchmark_sync_reflection(iterations)
    print_stats("SYNC (Baseline)", sync_latencies, target_ms=355)
    
    # Benchmark async
    async_latencies = await benchmark_async_reflection(iterations)
    print_stats("ASYNC (Optimized)", async_latencies, target_ms=100)
    
    # Calculate improvement
    if sync_latencies and async_latencies:
        sync_avg = mean(sync_latencies)
        async_avg = mean(async_latencies)
        improvement = (sync_avg - async_avg) / sync_avg * 100
        speedup = sync_avg / async_avg
        
        print(f"\n📈 IMPROVEMENT:")
        print(f"  Speedup:      {speedup:.1f}x faster")
        print(f"  Reduction:    {improvement:.1f}%")
        
        if speedup >= 5.0:
            print(f"\n🎉 SUCCESS: Achieved {speedup:.1f}x speedup (target: 7x)")
        elif speedup >= 3.0:
            print(f"\n⚠️  PARTIAL: Achieved {speedup:.1f}x speedup (target: 7x)")
        else:
            print(f"\n❌ FAILED: Only {speedup:.1f}x speedup (target: 7x)")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted")
    except Exception as e:
        print(f"\n\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
