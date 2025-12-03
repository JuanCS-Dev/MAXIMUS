"""
Consciousness System API - FastAPI endpoints for monitoring dashboard.

Includes REST endpoints, WebSocket, and SSE streaming for real-time cockpit.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator
from dataclasses import asdict
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from consciousness.api_schemas import (
    ArousalAdjustment,
    ConsciousnessStateResponse,
    EmergencyShutdownRequest,
    ESGTEventResponse,
    SafetyStatusResponse,
    SafetyViolationResponse,
    SalienceInput,
)
from consciousness.prometheus_metrics import get_metrics_handler


def create_consciousness_api(consciousness_system: dict[str, Any]) -> APIRouter:
    """Create consciousness API router with all endpoints."""
    router = APIRouter(prefix="/api/consciousness", tags=["consciousness"])

    active_connections: list[WebSocket] = []
    sse_subscribers: list[asyncio.Queue[dict[str, Any]]] = []
    event_history: list[dict[str, Any]] = []
    MAX_HISTORY = 100

    def add_event_to_history(event: Any) -> None:
        """Add ESGT event to history."""
        event_dict = asdict(event) if hasattr(event, "__dataclass_fields__") else dict(event)
        event_dict["timestamp"] = datetime.now().isoformat()
        event_history.append(event_dict)
        if len(event_history) > MAX_HISTORY:
            event_history.pop(0)

    async def broadcast_to_consumers(message: dict[str, Any]) -> None:
        """Broadcast message to WebSockets and SSE subscribers."""
        dead_connections: list[WebSocket] = []
        for connection in active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        for connection in dead_connections:
            active_connections.remove(connection)

        if sse_subscribers:
            serialized = message | {"timestamp": message.get("timestamp", datetime.now().isoformat())}
            for queue in list(sse_subscribers):
                try:
                    queue.put_nowait(serialized)
                except asyncio.QueueFull:
                    try:
                        queue.get_nowait()
                        queue.put_nowait(serialized)
                    except (asyncio.QueueEmpty, asyncio.QueueFull):
                        # Queue full or empty, skip
                        continue

    @router.get("/state", response_model=ConsciousnessStateResponse)
    async def get_consciousness_state() -> ConsciousnessStateResponse:
        """Get current complete consciousness state."""
        try:
            tig = consciousness_system.get("tig")
            esgt = consciousness_system.get("esgt")
            arousal = consciousness_system.get("arousal")

            if not all([tig, esgt, arousal]):
                raise HTTPException(status_code=503, detail="Consciousness system not fully initialized")

            tig_metrics_raw = tig.get_metrics() if tig and hasattr(tig, "get_metrics") else {}
            tig_metrics = asdict(tig_metrics_raw) if hasattr(tig_metrics_raw, "__dataclass_fields__") else tig_metrics_raw
            arousal_state = arousal.get_current_arousal() if arousal and hasattr(arousal, "get_current_arousal") else None

            return ConsciousnessStateResponse(
                timestamp=datetime.now().isoformat(),
                esgt_active=bool(esgt._running) if esgt and hasattr(esgt, "_running") else False,
                arousal_level=arousal_state.arousal if arousal_state else 0.5,
                arousal_classification=arousal_state.level.value if arousal_state and hasattr(arousal_state.level, "value") else "UNKNOWN",
                tig_metrics=tig_metrics,
                recent_events_count=len(event_history),
                system_health="HEALTHY" if all([tig, esgt, arousal]) else "DEGRADED",
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving state: {str(e)}") from e

    @router.get("/esgt/events", response_model=list[ESGTEventResponse])
    async def get_esgt_events(limit: int = 20) -> list[ESGTEventResponse]:
        """Get recent ESGT events."""
        if limit < 1 or limit > MAX_HISTORY:
            raise HTTPException(status_code=400, detail=f"Limit must be between 1 and {MAX_HISTORY}")
        events = event_history[-limit:]
        return [
            ESGTEventResponse(
                event_id=evt.get("event_id", "unknown"),
                timestamp=evt.get("timestamp", datetime.now().isoformat()),
                success=evt.get("success", False),
                salience={
                    "novelty": evt.get("salience", {}).get("novelty", 0),
                    "relevance": evt.get("salience", {}).get("relevance", 0),
                    "urgency": evt.get("salience", {}).get("urgency", 0),
                },
                coherence=evt.get("coherence_achieved"),
                duration_ms=evt.get("duration_ms"),
                nodes_participating=len(evt.get("nodes_participating", [])),
                reason=evt.get("reason"),
            )
            for evt in events
        ]

    @router.get("/arousal")
    async def get_arousal_state() -> dict[str, Any]:
        """Get current arousal state."""
        try:
            arousal = consciousness_system.get("arousal")
            if not arousal:
                raise HTTPException(status_code=503, detail="Arousal controller not initialized")
            arousal_state = arousal.get_current_arousal()
            if not arousal_state:
                return {"error": "No arousal state available"}
            return {
                "arousal": arousal_state.arousal,
                "level": arousal_state.level.value if hasattr(arousal_state.level, "value") else str(arousal_state.level),
                "baseline": arousal_state.baseline_arousal,
                "need_contribution": arousal_state.need_contribution,
                "temporal_contribution": arousal_state.temporal_contribution,
                "timestamp": datetime.now().isoformat(),
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving arousal: {str(e)}") from e

    @router.post("/esgt/trigger")
    async def trigger_esgt(salience: SalienceInput) -> dict[str, Any]:
        """Manually trigger ESGT ignition."""
        try:
            esgt = consciousness_system.get("esgt")
            if not esgt:
                raise HTTPException(status_code=503, detail="ESGT coordinator not initialized")
            from consciousness.esgt.coordinator import SalienceScore
            salience_score = SalienceScore(novelty=salience.novelty, relevance=salience.relevance, urgency=salience.urgency)
            event = await esgt.initiate_esgt(salience_score, salience.context)
            add_event_to_history(event)
            await broadcast_to_consumers({"type": "esgt_event", "event": asdict(event) if hasattr(event, "__dataclass_fields__") else dict(event)})
            return {
                "success": event.success,
                "event_id": event.event_id,
                "coherence": event.achieved_coherence,
                "duration_ms": event.time_to_sync_ms,
                "reason": getattr(event, "reason", None),
                "timestamp": datetime.now().isoformat(),
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error triggering ESGT: {str(e)}") from e

    @router.post("/arousal/adjust")
    async def adjust_arousal(adjustment: ArousalAdjustment) -> dict[str, Any]:
        """Adjust arousal level."""
        try:
            arousal = consciousness_system.get("arousal")
            if not arousal:
                raise HTTPException(status_code=503, detail="Arousal controller not initialized")
            arousal.request_modulation(source=adjustment.source, delta=adjustment.delta, duration_seconds=adjustment.duration_seconds)
            await asyncio.sleep(0.1)
            new_state = arousal.get_current_arousal()
            await broadcast_to_consumers({"type": "arousal_change", "arousal": new_state.arousal, "level": new_state.level.value if hasattr(new_state.level, "value") else str(new_state.level)})
            return {"arousal": new_state.arousal, "level": new_state.level.value if hasattr(new_state.level, "value") else str(new_state.level), "delta_applied": adjustment.delta}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adjusting arousal: {str(e)}") from e

    @router.get("/metrics")
    async def get_metrics() -> dict[str, Any]:
        """Get consciousness system metrics."""
        try:
            tig = consciousness_system.get("tig")
            esgt = consciousness_system.get("esgt")
            metrics: dict[str, Any] = {}
            if tig and hasattr(tig, "get_metrics"):
                metrics["tig"] = tig.get_metrics()
            if esgt and hasattr(esgt, "get_metrics"):
                metrics["esgt"] = esgt.get_metrics()
            metrics["events_count"] = len(event_history)
            metrics["timestamp"] = datetime.now().isoformat()
            return metrics
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}") from e

    @router.get("/safety/status", response_model=SafetyStatusResponse)
    async def get_safety_status() -> SafetyStatusResponse:
        """Get safety protocol status."""
        try:
            system = consciousness_system.get("system")
            if not system:
                raise HTTPException(status_code=503, detail="Consciousness system not initialized")
            status = system.get_safety_status()
            if not status:
                raise HTTPException(status_code=503, detail="Safety protocol not enabled in this system")
            return SafetyStatusResponse(**status)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving safety status: {str(e)}") from e

    @router.get("/safety/violations", response_model=list[SafetyViolationResponse])
    async def get_safety_violations(limit: int = 100) -> list[SafetyViolationResponse]:
        """Get recent safety violations."""
        if limit < 1 or limit > 1000:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")
        try:
            system = consciousness_system.get("system")
            if not system:
                raise HTTPException(status_code=503, detail="Consciousness system not initialized")
            violations = system.get_safety_violations(limit=limit)
            return [
                SafetyViolationResponse(
                    violation_id=v.violation_id, violation_type=v.violation_type.value, severity=v.severity.value,
                    timestamp=v.timestamp.isoformat(), value_observed=v.value_observed, threshold_violated=v.threshold_violated,
                    message=v.message, context=v.context,
                )
                for v in violations
            ]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving violations: {str(e)}") from e

    @router.post("/safety/emergency-shutdown")
    async def execute_emergency_shutdown(request: EmergencyShutdownRequest) -> dict[str, Any]:
        """Execute emergency shutdown (HITL only)."""
        try:
            system = consciousness_system.get("system")
            if not system:
                raise HTTPException(status_code=503, detail="Consciousness system not initialized")
            shutdown_executed = await system.execute_emergency_shutdown(reason=request.reason)
            return {"success": True, "shutdown_executed": shutdown_executed, "message": ("Emergency shutdown executed" if shutdown_executed else "HITL overrode shutdown"), "timestamp": datetime.now().isoformat()}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error executing emergency shutdown: {str(e)}") from e

    @router.get("/reactive-fabric/metrics")
    async def get_reactive_fabric_metrics() -> dict[str, Any]:
        """Get latest Reactive Fabric metrics."""
        try:
            system = consciousness_system.get("system")
            if not system or not hasattr(system, 'orchestrator'):
                raise HTTPException(status_code=503, detail="Reactive Fabric orchestrator not initialized")
            metrics = await system.orchestrator.metrics_collector.collect()
            return {
                "timestamp": metrics.timestamp,
                "tig": {"node_count": metrics.tig_node_count, "edge_count": metrics.tig_edge_count, "avg_latency_us": metrics.tig_avg_latency_us, "coherence": metrics.tig_coherence},
                "esgt": {"event_count": metrics.esgt_event_count, "success_rate": metrics.esgt_success_rate, "frequency_hz": metrics.esgt_frequency_hz, "avg_coherence": metrics.esgt_avg_coherence},
                "arousal": {"level": metrics.arousal_level, "classification": metrics.arousal_classification, "stress": metrics.arousal_stress, "need": metrics.arousal_need},
                "pfc": {"signals_processed": metrics.pfc_signals_processed, "actions_generated": metrics.pfc_actions_generated, "approval_rate": metrics.pfc_approval_rate},
                "tom": {"total_agents": metrics.tom_total_agents, "total_beliefs": metrics.tom_total_beliefs, "cache_hit_rate": metrics.tom_cache_hit_rate},
                "safety": {"violations": metrics.safety_violations, "kill_switch_active": metrics.kill_switch_active},
                "health_score": metrics.health_score, "collection_duration_ms": metrics.collection_duration_ms, "errors": metrics.errors,
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving reactive fabric metrics: {str(e)}") from e

    @router.get("/reactive-fabric/events")
    async def get_reactive_fabric_events(limit: int = 20) -> dict[str, Any]:
        """Get recent Reactive Fabric events."""
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
        try:
            system = consciousness_system.get("system")
            if not system or not hasattr(system, 'orchestrator'):
                raise HTTPException(status_code=503, detail="Reactive Fabric orchestrator not initialized")
            events = system.orchestrator.event_collector.get_recent_events(limit=limit)
            return {
                "events": [
                    {"event_id": e.event_id, "type": e.event_type.value, "severity": e.severity.value, "timestamp": e.timestamp, "source": e.source, "data": e.data, "salience": {"novelty": e.novelty, "relevance": e.relevance, "urgency": e.urgency}, "processed": e.processed, "esgt_triggered": e.esgt_triggered}
                    for e in events
                ],
                "total_count": len(events),
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving reactive fabric events: {str(e)}") from e

    @router.get("/reactive-fabric/orchestration")
    async def get_reactive_fabric_orchestration() -> dict[str, Any]:
        """Get Reactive Fabric orchestration status."""
        try:
            system = consciousness_system.get("system")
            if not system or not hasattr(system, 'orchestrator'):
                raise HTTPException(status_code=503, detail="Reactive Fabric orchestrator not initialized")
            orchestrator = system.orchestrator
            stats = orchestrator.get_orchestration_stats()
            recent_decisions = orchestrator.get_recent_decisions(limit=10)
            return {
                "status": {"running": orchestrator._running, "collection_interval_ms": orchestrator.collection_interval_ms, "salience_threshold": orchestrator.salience_threshold},
                "statistics": stats,
                "recent_decisions": [
                    {"timestamp": d.timestamp, "should_trigger": d.should_trigger_esgt, "salience": {"novelty": d.salience.novelty, "relevance": d.salience.relevance, "urgency": d.salience.urgency, "total": d.salience.compute_total()}, "reason": d.reason, "confidence": d.confidence, "triggering_events_count": len(d.triggering_events), "health_score": d.metrics_snapshot.health_score}
                    for d in recent_decisions
                ],
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving orchestration status: {str(e)}") from e

    router.add_route("/metrics", get_metrics_handler(), methods=["GET"])

    async def _sse_event_stream(request: Request, queue: asyncio.Queue[dict[str, Any]]) -> AsyncGenerator[bytes, None]:
        """SSE generator transmitting events while connection is active."""
        heartbeat_interval = 15.0
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=heartbeat_interval)
                except asyncio.TimeoutError:
                    message = {"type": "heartbeat", "timestamp": datetime.now().isoformat()}
                yield f"data: {json.dumps(message)}\n\n".encode("utf-8")
        finally:
            if queue in sse_subscribers:
                sse_subscribers.remove(queue)

    @router.get("/stream/sse")
    async def stream_sse(request: Request) -> StreamingResponse:
        """SSE endpoint for cockpit and React frontend."""
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=250)
        sse_subscribers.append(queue)
        queue.put_nowait({"type": "connection_ack", "timestamp": datetime.now().isoformat(), "recent_events": len(event_history)})
        return StreamingResponse(_sse_event_stream(request, queue), media_type="text/event-stream")

    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        """WebSocket endpoint for real-time consciousness state streaming."""
        await websocket.accept()
        active_connections.append(websocket)
        try:
            esgt = consciousness_system.get("esgt")
            arousal = consciousness_system.get("arousal")
            if arousal:
                arousal_state = arousal.get_current_arousal()
                await websocket.send_json({"type": "initial_state", "arousal": arousal_state.arousal if arousal_state else 0.5, "events_count": len(event_history), "esgt_active": bool(esgt._running) if esgt and hasattr(esgt, "_running") else False})
            while True:
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
                except TimeoutError:
                    await websocket.send_json({"type": "heartbeat", "timestamp": datetime.now().isoformat()})
        except WebSocketDisconnect:
            if websocket in active_connections:
                active_connections.remove(websocket)
        except Exception:
            if websocket in active_connections:
                active_connections.remove(websocket)

    async def _periodic_state_broadcast() -> None:
        """Send periodic state snapshot to consumers."""
        while True:
            await asyncio.sleep(5.0)
            try:
                if not consciousness_system:
                    continue
                arousal = consciousness_system.get("arousal")
                esgt = consciousness_system.get("esgt")
                arousal_state = arousal.get_current_arousal() if arousal and hasattr(arousal, "get_current_arousal") else None
                await broadcast_to_consumers({"type": "state_snapshot", "timestamp": datetime.now().isoformat(), "arousal": getattr(arousal_state, "arousal", None), "esgt_active": getattr(esgt, "_running", False), "events_count": len(event_history)})
            except Exception:
                continue

    background_tasks: list[asyncio.Task[None]] = []

    @router.on_event("startup")
    async def _start_background_tasks() -> None:
        background_tasks.append(asyncio.create_task(_periodic_state_broadcast()))

    @router.on_event("shutdown")
    async def _stop_background_tasks() -> None:
        for task in background_tasks:
            task.cancel()
        background_tasks.clear()

    return router
