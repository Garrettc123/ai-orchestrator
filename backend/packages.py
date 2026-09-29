"""Every Garrettc123 repo listed in the pin audit. One process."""
from __future__ import annotations
from typing import Any, Dict

NAMES = ["PROMETHEUS-Global-Infrastructure-Brain", "ai-swarm-crypto-bounty-system", "zero-human-ai-platform", "THE-FORGE", "ARCHITECT_Pro-Enterprise", "AutoGenesis-AI-Platform", "autonomous-income-deployment", "TITAN-Autonomous-Business-Empire", "autonomous-butler-core", "ai-business-platform", "ai-ops-studio", "apex-revenue-system", "asynchronous-automation-framework", "autonoma-agents", "autonomous-revenue-architect", "enterprise-devops-platform", "enterprise-mlops-platform", "garcar-autonomous-wealth-system", "neural-mesh", "NEXUS-AI-CORE", "real-time-decision-engine", "smart-contract-auditor-ai", "systems-master-hub", "termux-automation-app", "termux-automation-scripts", "zeus-dashboard", "ai-agent-platform", "ai-business-automation-tree", "ai-consulting-automaton", "ai-orchestrator", "ai-powered-deal-desk", "ai-training-data-factory", "ai-wealth-ecosystem", "APEX-AI-ENGINE", "APEX-Universal-AI-Operating-System", "apex-zero-human-orchestrator", "api-key-automaton", "assets-library-2025", "async-automation-framework", "async-automation-workflows", "atlas-agents", "atlas-dashboard", "atlas-infrastructure", "atlas-integrations", "atlas-orchestration", "autohelix", "automated-sales-outreach", "automation-frontend-dashboard", "autonomous-event-mesh", "autonomous-orchestrator-core", "autonomous-revenue-ops", "autonomous-self-healing", "autonomous-support-ai", "autonomous-zero-touch-deploy", "believe-revenue-site", "churn-predictor-ai-backend", "client-onboarding-platform", "code-snippets-vault", "cognitive-api-marketplace", "content-engine-ai-backend", "conversational-ai-engine", "cuddly-octo-telegram", "customer-churn-predictor", "customer-intelligence-branch", "deal-desk-ai-backend", "deal-desk-ai-frontend", "defi-yield-aggregator", "devops-portfolio", "distributed-job-orchestration-engine", "document-intelligence-hub", "documentation-hub", "ecommerce-microservices", "enterprise-ai-deployment", "enterprise-ai-grid", "enterprise-automation-system", "enterprise-cicd-foundation", "enterprise-data-mesh-platform", "enterprise-feature-flag-system", "enterprise-pilot-programs", "enterprise-proposal-generator", "enterprise-unified-platform", "evals", "garcar-acquisition", "garcar-alpha-os", "garcar-apex-nexus", "garcar-command-plane", "garcar-control-plane", "garcar-deploy-engine", "garcar-emergency-payments", "garcar-enterprise-production", "garcar-landing", "garcar-lead-intake", "garcar-payments", "garcar-repo-foundry", "garcar-shopify-app", "garcar-singularity-grid", "garrettc1", "Garrettc123.github.io", "garrettc2", "garrettc3", "garrettc4", "garrettc5", "genesis-consciousness-deploy", "gumroad", "haikus-for-codespaces", "hyper-automation-factory", "hypervelocity-orchestrator", "infrastructure-code-architect", "infrastructure-templates", "intelligent-ci-cd-orchestrator", "intelligent-customer-data-platform", "iot-analytics-pipeline", "lead-enrichment-engine", "living-infrastructure-brain", "machine-payments", "marketing-automation-branch", "mars-api", "mars-production", "master-deployment-auto-deploy-revenue", "meta-orchestration-engine", "ml-fraud-detection", "mobile-builds-catalog", "mobile-nexus-dashboard", "monarch-nexus-core", "monarch-nexus-v2", "multimodal-input-api", "napoleon-hill-success-system", "neural-code-synthesizer", "neural-mesh-pipeline", "NEXUS-Master-Orchestration-Hub", "NEXUS-Mobile-Command-Center", "NEXUS-Quantum-Intelligence-Framework", "nexusai-platform", "nwu-data-monetization", "nwu-protocol", "observability-intelligence-platform", "paleontology-analysis-tools", "perfect-customer-acquisition-system", "Pipeline-A.I", "pixel-control-hub", "portfolio", "portfolio-website", "predictive-infrastructure-optimizer", "process-copilot", "product-development-branch", "quantum-neural-synthesizer", "real-time-streaming-analytics", "revenue-agent-system", "revenue-intelligence-engine", "RHNS-Architecture", "saas-revenue-accelerator", "security-sentinel-framework", "semantic-knowledge-nexus", "seo-content-factory", "SINGULARITY-AGI-Research-Platform", "sovereign-chat", "stablecoin-protocol", "stripe-payment-integration", "subscription-intelligence-engine", "supersecret", "system-aura-core", "termux-automation-docs", "termux-automation-service", "termux-workspace-sync", "tree-of-life", "tree-of-life-core", "tree-of-life-master-integration", "tree-of-life-minimal", "tree-of-life-system", "ueep-bootstrap", "ueep-frontend", "ueep-ha-system", "ULTIMATE-MASTER-SYSTEM", "unprecedented-autonomous-revenue-os", "zero-human-approval-dashboard", "zero-human-enterprise-grid", "zero-human-governance-core", "zero-human-infra-as-code", "zero-human-orchestration", "zero-human-orchestrator", "zero-human-platform-core"]

def _family(name: str) -> str:
    n = name.lower()
    rules = [
        (("payment","stripe","billing","gumroad","shopify"), "billing"),
        (("lead","outreach","sales","seo","marketing","acquisition"), "outreach"),
        (("deal-desk","proposal","consulting"), "proposal"),
        (("crm","churn","customer","onboarding"), "crm"),
        (("butler","support","deploy-engine","zero-touch"), "fulfillment"),
        (("landing","github.io","portfolio","documentation","content-engine","believe-revenue","haikus"), "content"),
        (("audit","compliance","security","fraud","sentinel"), "compliance"),
        (("nwu","titan","governance","sovereign","zero-human-governance"), "governance"),
        (("eval","paleontology","document-intelligence","training-data","singularity-agi"), "research"),
        (("revenue","income","wealth","monetization","mars"), "revenue"),
        (("termux","devops","cicd","infra","prometheus","atlas-infra","zero-human-infra","dashboard","zeus","command","control-plane","ops-studio","pixel","orchestrator"), "core"),
    ]
    for keys, fam in rules:
        if any(k in n for k in keys):
            return fam
    if name == "ai-orchestrator":
        return "core"
    return "intelligence"

def _state(name: str) -> str:
    if name in {"ai-orchestrator", "garcar-landing", "Garrettc123.github.io"}:
        return "healthy"
    if name in {"autonomous-income-deployment", "RHNS-Architecture", "THE-FORGE", "mars-api", "mars-production", "garcar-payments", "stripe-payment-integration"}:
        return "provisioning"
    return "dormant"

PACKAGES = {n: {"family": _family(n), "state": _state(n)} for n in NAMES}

def run(name: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    row = PACKAGES.get(name)
    if not row:
        return {"ok": False, "error": "unknown_package", "name": name, "count": len(PACKAGES)}
    from onesys import HOP_ORGAN, ONESYS, SPINE
    family = row["family"]
    if family == "intelligence":
        from knowledge import ask
        q = payload.get("query") or payload.get("task") or ("status " + name)
        kn = ask(str(q), intent=payload.get("intent") or "auto")
        return {"ok": bool(kn.get("ok")), "package": name, "family": family, "via": "knowledge", "result": kn}
    if family == "core":
        return {"ok": True, "package": name, "family": family, "via": "core", "result": ONESYS.snapshot()}
    hop = next((h for h, org in HOP_ORGAN.items() if org == family), None)
    if hop in SPINE:
        act = ONESYS.act(hop, payload=payload, confidence=float(payload.get("confidence", 0.8)))
        return {"ok": bool(act.get("ok")), "package": name, "family": family, "via": "spine." + hop, "result": act}
    return {"ok": True, "package": name, "family": family, "via": "registered", "state": row["state"]}

def summary() -> Dict[str, Any]:
    by: Dict[str, int] = {}
    states: Dict[str, int] = {}
    for v in PACKAGES.values():
        by[v["family"]] = by.get(v["family"], 0) + 1
        states[v["state"]] = states.get(v["state"], 0) + 1
    return {"organism": "Garrett.ai", "count": len(PACKAGES), "by_family": by, "by_state": states, "names": sorted(PACKAGES)}
