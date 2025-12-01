# MAXIMUS 2.0 - Migration Manifest
**Date**: 2025-11-30  
**Architect**: Juan Carlos  
**Authority**: CODE_CONSTITUTION.md v1.1 + A CONSTITUIÇÃO VÉRTICE v3.0

## Executive Summary

This manifest documents the migration of **76 services** → **12 CORE services** as part of the MAXIMUS 2.0 transformation.

**Migration Summary**:
- ✅ **12 CORE** services retained (to be refactored)
- 📦 **57 LEGACY** services moved to `/media/juan/DATA/backups/maximus-legado-services-2025-11-30/`
- 🗑️ **4 DELETE** services archived
- 💀 **1 MONOLITH** archived (`api_gateway` - 273K lines)
- 🆕 **3 NEW** services to be created

**Source**: `/home/juan/vertice-dev/backend/services/`  
**Destination**: `/media/juan/DATA/backups/maximus-legado-services-2025-11-30/`  
**Backup Size**: 642MB

---

## 🎯 CORE Services (12) - RETAINED

These services define Maximus 2.0 as "a Constitutional Meta-Cognitive AI that Manages Agents."

| # | Service | Purpose | Lines | Status | Action |
|---|---------|---------|-------|--------|--------|
| 1 | `meta_orchestrator` | Agent coordination (ROMA) | 1,525 | ✅ Constitutional | No changes |
| 2 | `hcl_planner_service` | Infrastructure planning (Gemini 2.5 Pro) | 1,334 | ✅ Constitutional | No changes |
| 3 | `hcl_executor_service` | Execute infrastructure actions | 2,151 | 🔧 Needs refactor | Refactor to constitutional |
| 4 | `hcl_analyzer_service` | System metrics analysis | 2,054 | 🔧 Needs refactor | Refactor to constitutional |
| 5 | `hcl_monitor_service` | Continuous monitoring | 1,554 | 🔧 Needs refactor | Refactor to constitutional |
| 6 | `maximus_core_service` | Consciousness system (TIG Fabric) | Large | 🔧 Needs major refactor | Break down, enforce limits |
| 7 | `digital_thalamus_service` | Neural gateway, routing | 2,762 | 🔧 Needs refactor | Refactor to constitutional |
| 8 | `prefrontal_cortex_service` | Executive function, decisions | TBD | 🔧 Needs refactor | Refactor to constitutional |
| 9 | `ethical_audit_service` | Constitutional compliance | 6,416 | 🔧 Needs major refactor | Refactor to lean guardian |
| 10 | `reactive_fabric_core` | Immune reflex, threat response | TBD | 🔧 Needs refactor | Refactor to constitutional |
| 11 | `metacognitive_reflector` | Self-critique, thought tracing | - | 🆕 NEW | Create from scratch |
| 12 | `episodic_memory` | MIRIX memory system | - | 🆕 NEW | Create from scratch |

**Total CORE**: 12 services (9 existing + 3 new)

---

## 📦 LEGACY Services (57) - MOVED TO DATA

### L1: OSINT/Intelligence (9 services)

| # | Service | Purpose | Destination | Plugin Candidate |
|---|---------|---------|-------------|------------------|
| 1 | `google_osint_service` | Google OSINT intelligence | `/DATA/backups/.../` | ✅ Yes (OSINTPlugin) |
| 2 | `osint_service` | General OSINT | `/DATA/backups/.../` | ✅ Yes |
| 3 | `threat_intel_service` | Threat intelligence feeds | `/DATA/backups/.../` | ✅ Yes |
| 4 | `vuln_intel_service` | Vulnerability intelligence | `/DATA/backups/.../` | ✅ Yes |
| 5 | `ip_intelligence_service` | IP reputation | `/DATA/backups/.../` | ✅ Yes |
| 6 | `domain_service` | Domain intelligence | `/DATA/backups/.../` | ✅ Yes (DomainIntelPlugin) |
| 7 | `sinesp_service` | SINESP Brazil integration | `/DATA/backups/.../` | ⚠️ Maybe |
| 8 | `hcl_kb_service` | HCL knowledge base | `/DATA/backups/.../` | ⚠️ Maybe |
| 9 | `hpc_service` | HPC integration | `/DATA/backups/.../` | ⚠️ Maybe |

**Rationale**: Valuable intelligence tools but NOT core meta-cognitive AI. Can be loaded as plugins when needed.

### L2: Offensive/Security Tools (8 services)

| # | Service | Purpose | Destination | Plugin Candidate |
|---|---------|---------|-------------|------------------|
| 1 | `offensive_gateway` | Offensive security gateway | `/DATA/backups/.../` | ✅ Yes |
| 2 | `web_attack_service` | Web attack simulations | `/DATA/backups/.../` | ✅ Yes |
| 3 | `nmap_service` | Network scanning | `/DATA/backups/.../` | ✅ Yes |
| 4 | `network_recon_service` | Network reconnaissance | `/DATA/backups/.../` | ✅ Yes |
| 5 | `malware_analysis_service` | Malware analysis | `/DATA/backups/.../` | ✅ Yes |
| 6 | `vuln_scanner_service` | Vulnerability scanning | `/DATA/backups/.../` | ✅ Yes |
| 7 | `social_eng_service` | Social engineering tests | `/DATA/backups/.../` | ⚠️ Maybe |
| 8 | `cyber_service` | General cyber operations | `/DATA/backups/.../` | ✅ Yes (CyberPlugin) |

**Rationale**: Specialist security tools, not meta-cognitive orchestration. Plugin candidates for security operations.

### L3: Sensory Cortex (5 services)

| # | Service | Purpose | Destination | Plugin Candidate |
|---|---------|---------|-------------|------------------|
| 1 | `visual_cortex_service` | Visual processing | `/DATA/backups/.../` | ❌ No (over-engineered) |
| 2 | `auditory_cortex_service` | Audio processing | `/DATA/backups/.../` | ❌ No (over-engineered) |
| 3 | `somatosensory_service` | Touch/haptic processing | `/DATA/backups/.../` | ❌ No (over-engineered) |
| 4 | `chemical_sensing_service` | Chemical detection | `/DATA/backups/.../` | ❌ No (over-engineered) |
| 5 | `vestibular_service` | Balance/orientation | `/DATA/backups/.../` | ❌ No (over-engineered) |

**Rationale**: Maximus 2.0 is NOT a robotics controller. These sensory modules are over-engineered for current needs. Archive for potential future use.

### L4: Immune System Bloat (11 services) 💀

| # | Service | Purpose | Lines | Destination | Plugin Candidate |
|---|---------|---------|-------|-------------|------------------|
| 1 | `active_immune_core` | Active immune responses | 89,828 | `/DATA/backups/.../` | ❌ No (MASSIVE bloat) |
| 2 | `adaptive_immune_system` | Adaptive immunity | 30,044 | `/DATA/backups/.../` | ❌ No (MASSIVE bloat) |
| 3 | `immunis_bcell_service` | B-cell simulation | TBD | `/DATA/backups/.../` | ❌ No |
| 4 | `immunis_cytotoxic_t_service` | Cytotoxic T-cell | TBD | `/DATA/backups/.../` | ❌ No |
| 5 | `immunis_dendritic_service` | Dendritic cell | TBD | `/DATA/backups/.../` | ❌ No |
| 6 | `immunis_helper_t_service` | Helper T-cell | TBD | `/DATA/backups/.../` | ❌ No |
| 7 | `immunis_macrophage_service` | Macrophage | TBD | `/DATA/backups/.../` | ❌ No |
| 8 | `immunis_neutrophil_service` | Neutrophil | TBD | `/DATA/backups/.../` | ❌ No |
| 9 | `immunis_nk_cell_service` | NK cell | TBD | `/DATA/backups/.../` | ❌ No |
| 10 | `immunis_treg_service` | Regulatory T-cell | TBD | `/DATA/backups/.../` | ❌ No |
| 11 | `ai_immune_system` | AI immune coordinator | 1,871 | `/DATA/backups/.../` | ❌ No |

**Rationale**: MASSIVELY over-engineered biological immune metaphor. Maximus 2.0 needs ONE lean immune service (`ethical_audit` + `reactive_fabric`), not 11 specialized cell types totaling 120K+ lines.

### L5: Orchestration Experiments (4 services)

| # | Service | Purpose | Destination | Plugin Candidate |
|---|---------|---------|-------------|------------------|
| 1 | `maximus_orchestrator_service` | Legacy orchestrator | `/DATA/backups/.../` | ❌ No (replaced by meta_orchestrator) |
| 2 | `maximus_integration_service` | Legacy integrations | `/DATA/backups/.../` | ❌ No |
| 3 | `c2_orchestration_service` | C2 orchestration | `/DATA/backups/.../` | ⚠️ Maybe |
| 4 | `wargaming_crisol` | Wargaming simulations | `/DATA/backups/.../` | ⚠️ Maybe |

**Rationale**: Old orchestration experiments replaced by `meta_orchestrator`. Archive for historical reference.

### L6: Monitoring/Observability (3 services)

| # | Service | Purpose | Destination | Plugin Candidate |
|---|---------|---------|-------------|------------------|
| 1 | `network_monitor_service` | Network monitoring | `/DATA/backups/.../` | ✅ Yes |
| 2 | `ssl_monitor_service` | SSL certificate monitoring | `/DATA/backups/.../` | ✅ Yes |
| 3 | `maximus_dlq_monitor_service` | Dead letter queue monitor | `/DATA/backups/.../` | ⚠️ Maybe |

**Rationale**: Useful observability utilities but not core AI. Plugin candidates.

### L7: Miscellaneous Services (13 services)

| # | Service | Purpose | Lines | Destination | Plugin Candidate |
|---|---------|---------|-------|-------------|------------------|
| 1 | `adr_core_service` | Architecture decision records | 2,843 | `/DATA/backups/.../` | ⚠️ Maybe |
| 2 | `bas_service` | BAS (unclear purpose) | 2,447 | `/DATA/backups/.../` | ❌ Unknown |
| 3 | `edge_agent_service` | Edge agent | 2,376 | `/DATA/backups/.../` | ⚠️ Maybe |
| 4 | `cloud_coordinator_service` | Cloud coordination | 1,833 | `/DATA/backups/.../` | ⚠️ Maybe |
| 5 | `homeostatic_regulation` | Homeostasis | 1,830 | `/DATA/backups/.../` | ❌ No |
| 6 | `memory_consolidation_service` | Memory consolidation | TBD | `/DATA/backups/.../` | ⚠️ Check (replaced by episodic_memory?) |
| 7 | `neuromodulation_service` | Neuromodulation | TBD | `/DATA/backups/.../` | ❌ No |
| 8 | `hitl_patch_service` | Human-in-the-loop patches | 1,856 | `/DATA/backups/.../` | ⚠️ Maybe |
| 9 | `strategic_planning_service` | Strategic planning | TBD | `/DATA/backups/.../` | ⚠️ Check (overlaps with prefrontal_cortex?) |
| 10 | `narrative_manipulation_filter` | Narrative filtering | TBD | `/DATA/backups/.../` | ❌ No |
| 11 | `reflex_triage_engine` | Reflex triage | TBD | `/DATA/backups/.../` | ❌ Check (overlaps with reactive_fabric?) |
| 12 | `rte_service` | RTE (unclear) | TBD | `/DATA/backups/.../` | ❌ Unknown |
| 13 | `hsas_service` | HSAS (unclear) | TBD | `/DATA/backups/.../` | ❌ Unknown |

**Rationale**: Mixed bag of services crossing the line between "might be useful" and "definitely not core." Archive all for future review.

### L8: Service Labs (3 services)

| # | Service | Purpose | Destination | Plugin Candidate |
|---|---------|---------|-------------|------------------|
| 1 | `maba_service` | MABA (unclear) | `/DATA/backups/.../` | ❌ Unknown |
| 2 | `mvp_service` | MVP (unclear) | `/DATA/backups/.../` | ❌ Unknown |
| 3 | `mav-detection-service` | MAV detection | `/DATA/backups/.../` | ❌ Unknown |

**Rationale**: Experimental services with unclear purpose. Archive for potential future use.

### L9: Experimental/Oracles (4 services)

| # | Service | Purpose | Destination | Plugin Candidate |
|---|---------|---------|-------------|------------------|
| 1 | `maximus_oraculo` | Oracle v1 | `/DATA/backups/.../` | ❌ No (research) |
| 2 | `maximus_oraculo_v2` | Oracle v2 | `/DATA/backups/.../` | ❌ No (research) |
| 3 | `maximus_eureka` | Eureka moments | `/DATA/backups/.../` | ⚠️ Maybe |
| 4 | `maximus_predict` | Prediction engine | `/DATA/backups/.../` | ⚠️ Maybe |

**Rationale**: Research experiments, not production-ready. Archive for potential future development.

---

## 🗑️ DELETE Services (4) - ARCHIVED PERMANENTLY

| # | Service | Reason | Destination | Restore? |
|---|---------|--------|-------------|----------|
| 1 | `atlas_service` | Empty directory | `/DATA/backups/.../DELETE/` | ❌ No |
| 2 | `auth_service` | Empty directory | `/DATA/backups/.../DELETE/` | ❌ No |
| 3 | `mock_vulnerable_apps` | Test fixtures only | `/DATA/backups/.../DELETE/` | ❌ No |
| 4 | `__pycache__` | Python bytecode | Deleted immediately | ❌ No |

**Rationale**: No production code, safe to delete.

---

## 💀 MONOLITH - ARCHIVED & REPLACED

### `api_gateway` (273,835 lines) 💀

**Current State**:
- **Lines**: 273,835
- **Files**: 41
- **Problem**: Massive monolith mixing routing, business logic, transformations, validations

**Action**:
1. ✅ Archive to `/DATA/backups/.../api_gateway_MONOLITH/`
2. 🔍 Extract critical routing logic (manual review)
3. 🆕 Create minimal `api_gateway` (<500 lines)

**Replacement**:
```
api_gateway/
├── main.py              # <200 lines (FastAPI app)
├── routes/
│   ├── meta.py          # Routes to meta_orchestrator
│   ├── hcl.py           # Routes to HCL services
│   └── consciousness.py # Routes to consciousness services
├── middleware/
│   └── auth.py          # JWT validation
└── requirements.txt
```

**Rationale**: This monolith is the EPITOME of technical debt. Maximus 2.0 needs a lean gateway that just routes requests, period.

---

## 🆕 NEW Services (3) - TO BE CREATED

| # | Service | Purpose | Lines (Target) | Technologies |
|---|---------|---------|----------------|--------------|
| 1 | `metacognitive_reflector` | Self-critique, ethical auditing | ~800 | FastAPI, Gemini 2.5 Pro |
| 2 | `episodic_memory` | MIRIX memory system | ~1,200 | Qdrant, PostgreSQL, FastAPI |
| 3 | `api_gateway` | Minimal routing gateway | <500 | FastAPI |

---

## Migration Timeline

### Pre-Migration (Nov 30, 2025)
- [x] Create implementation plan
- [x] Create migration manifest  
- [ ] Get architect approval
- [ ] Run dependency analysis

### Phase 1: Migration Execution (Dec 1-2, 2025)
- [ ] Create backup directory structure
- [ ] Move 57 LEGACY services to DATA disk
- [ ] Archive `api_gateway` monolith
- [ ] Delete 4 empty/stub services
- [ ] Verify 12 CORE services remain intact

### Phase 2: New Service Creation (Dec 3-5, 2025)
- [ ] Create `metacognitive_reflector`
- [ ] Create `episodic_memory`
- [ ] Create minimal `api_gateway`

### Phase 3: Verification (Dec 6-7, 2025)
- [ ] Update docker-compose.yml
- [ ] Test CORE service startup
- [ ] Run constitutional audit
- [ ] Document migration

---

## Access Guide for LEGACY Services

### How to Access Archived Services

**Location**: `/media/juan/DATA/backups/maximus-legado-services-2025-11-30/`

**Browse**:
```bash
cd /media/juan/DATA/backups/maximus-legado-services-2025-11-30/
ls -1
```

**Restore a Service Temporarily** (for reference):
```bash
# Example: temporarily restore google_osint_service for code review
cp -r /media/juan/DATA/backups/maximus-legado-services-2025-11-30/google_osint_service \
      /tmp/google_osint_service

# Review code
cd /tmp/google_osint_service
```

**Extract Logic for Plugin**:
```bash
# Example: extract OSINT logic into a plugin
cd /media/juan/DATA/backups/maximus-legado-services-2025-11-30/google_osint_service

# Identify key functions
grep -n "def " core/*.py

# Copy relevant code to new plugin
# (Follow PLUGIN_DEVELOPMENT_GUIDE.md when created)
```

**Permanent Restore** (emergency only):
```bash
# Copy service back to active directory
sudo cp -r /media/juan/DATA/backups/maximus-legado-services-2025-11-30/google_osint_service \
           /home/juan/vertice-dev/backend/services/

# Add to docker-compose.yml
# Restart services
```

---

## Plugin Candidates (Future Phase 9)

Priority list for converting LEGACY services to plugins:

### High Priority
1. **OSINTPlugin** (from `google_osint_service`, `osint_service`)
2. **CyberPlugin** (from `cyber_service`)
3. **DomainIntelPlugin** (from `domain_service`)
4. **VulnScannerPlugin** (from `vuln_scanner_service`)
5. **NetworkMonitorPlugin** (from `network_monitor_service`, `ssl_monitor_service`)

### Medium Priority
6. **ThreatIntelPlugin** (from `threat_intel_service`)
7. **MalwareAnalysisPlugin** (from `malware_analysis_service`)
8. **NetworkReconPlugin** (from `network_recon_service`, `nmap_service`)

### Low Priority (Research)
9. **EurekaPlugin** (from `maximus_eureka`)
10. **PredictPlugin** (from `maximus_predict`)

---

## Rollback Instructions

If migration fails:

```bash
#!/bin/bash
# rollback_migration.sh

BACKUP_DIR="/media/juan/DATA/backups/maximus-legado-services-2025-11-30"
SERVICES_DIR="/home/juan/vertice-dev/backend/services"

echo "⚠️  ROLLING BACK MIGRATION..."

# Copy ALL services back
cp -r "$BACKUP_DIR"/* "$SERVICES_DIR/"

# Restore api_gateway from monolith
mv "$SERVICES_DIR/api_gateway_MONOLITH" "$SERVICES_DIR/api_gateway"

# Restore docker-compose
cd /home/juan/vertice-dev
git checkout docker-compose.yml

# Restart
docker compose down
docker compose up -d

echo "✅ Rollback complete. All services restored."
```

---

## Verification Checklist

### Post-Migration
- [ ] Exactly 12 CORE services in `/backend/services/`
- [ ] 57 services in DATA backup directory
- [ ] api_gateway monolith in DATA backup
- [ ] DELETE services in DATA backup (DELETE subfolder)
- [ ] __pycache__ permanently deleted

### Docker
- [ ] docker-compose.yml updated (only CORE services)
- [ ] All CORE services start successfully
- [ ] No orphan containers from LEGACY services

### Constitutional Compliance
- [ ] Zero files > 400 lines in CORE services
- [ ] Zero TODOs/FIXMEs in CORE services
- [ ] mypy --strict passes for all CORE services
- [ ] pylint --fail-under=9.5 passes

### Documentation
- [ ] MIGRATION_MANIFEST.md created
- [ ] MAXIMUS_2_IDENTITY.md created
- [ ] CORE_SERVICES_GUIDE.md created
- [ ] LEGACY_ACCESS_GUIDE.md created
- [ ] README.md updated

---

## Statistics

### Before Migration
- **Services**: 76
- **Size**: 642MB
- **Largest Service**: `active_immune_core` (89,828 lines)
- **Largest Monolith**: `api_gateway` (273,835 lines)
- **Constitutional Compliance**: ~2.7%

### After Migration (Target)
- **Services**: 12 CORE + 3 NEW = 15
- **Size**: ~50-100MB (estimated)
- **Largest Service**: TBD (all < 10,000 lines)
- **Largest File**: <400 lines (enforced)
- **Constitutional Compliance**: 100%

### Size Reduction
- **Services**: 76 → 15 (~80% reduction)
- **Codebase**: ~2.3M lines → <20K lines (~99% reduction)
- **Complexity**: Frankenstein → Lean Machine

---

## Sign-Off

**Migration Plan Created**: 2025-11-30  
**Created By**: Antigravity (Executor Tático)  
**Architect Approval**: _Pending_ (Juan Carlos)  
**Execution Start**: _Pending approval_

**Philosophy**:
> "We are not building a Frankenstein.  
> We are building a Constitutional Meta-Cognitive AI that Manages Agents.  
> Everything else is LEGADO."

---

**Status**: 🟡 MANIFEST COMPLETE, AWAITING APPROVAL  
**Next Action**: Get architect (Juan) approval to proceed with migration
