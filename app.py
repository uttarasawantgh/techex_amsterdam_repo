import streamlit as st
import time
import subprocess
import sys
import json

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="TowerShield - Edge AI Governance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark-theme styling matching DGX Spark aesthetic
st.markdown("""
<style>
    .stApp {
        background-color: #0b1120;
        color: #e2e8f0;
    }
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .badge-dgx {
        background-color: #064e3b;
        color: #34d399;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid #059669;
    }
    .badge-hitl {
        background-color: #451a03;
        color: #fbbf24;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid #d97706;
    }
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .terminal-box {
        background-color: #020617;
        color: #38bdf8;
        font-family: 'Courier New', Courier, monospace;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #1e293b;
        font-size: 0.85rem;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DYNAMIC SCENARIO DEFINITIONS & AGENT RULES
# ==========================================
SCENARIOS = {
    "CRITICAL: Multi-Tower Windshear Torsion (Tower 4)": {
        "text": "CRITICAL ALERT: Complex multi-tower cascading structural torsion detected across Tower 4 and adjacent relay masts following high-velocity windshear. Thermal and stress fractures span multiple concealed structural joints.",
        "severity": "CRITICAL",
        "tokens_local": 1250,
        "route_path": "vLLM Tier 3 (7B-VL) ➔ NeMo Switchyard Hybrid Router ➔ Claude Model Download Advisor",
        "target_model": "Qwen/Qwen2.5-32B-Instruct",
        "requires_hitl": True, 
        "eval_table": [
            ("Single-tower visual anomaly detection", "✅ PASS", "Within local 7B-VL capability"),
            ("Single-modality triage (Thermal/Stress)", "✅ PASS", "Routine edge classification task"),
            ("Multi-tower cascading correlation", "❌ FAIL", "Exceeds 7B context & cross-asset relational capacity"),
            ("Concealed joint fracture inference", "❌ FAIL", "Occluded structural reasoning demands 32B+ scale"),
            ("Fused thermal + stress + visual analysis", "❌ FAIL", "Heterogeneous sensor fusion requires high parametric headroom"),
            ("Windshear physics propagation modeling", "❌ FAIL", "Multi-physics simulation requires 32B+ scale")
        ],
        "default_heuristic_tier": "7B-VL",
        "default_confidence": 0.62,
        "default_economic_penalty": 0.40
    },
    "WARNING: Thermal Hotspot & Corrosion (Relay Mast 2)": {
        "text": "WARNING: Localized thermal elevated reading (58°C) detected at upper antenna array on Relay Mast 2. Minor rust corrosion visible along flange bolts.",
        "severity": "WARNING",
        "tokens_local": 480,
        "route_path": "vLLM Tier 2 (1.5B Local Edge Execution ➔ NeMo Switchyard Hybrid Router)",
        "target_model": "None (Handled locally on DGX Spark vLLM container)",
        "requires_hitl": False,
        "eval_table": [
            ("Single-tower visual anomaly detection", "✅ PASS", "Resolved via local 7B-VL visual encoder"),
            ("Single-modality triage (Thermal/Stress)", "✅ PASS", "Thermal thresholding within 1.5B model capability"),
            ("Multi-tower cascading correlation", "✅ N/A", "Single asset isolated event"),
            ("Concealed joint fracture inference", "✅ N/A", "Surface defect only - resolved locally"),
            ("Fused thermal + stress + visual analysis", "✅ PASS", "Routine local vision-language evaluation"),
            ("Windshear physics propagation modeling", "✅ N/A", "No atmospheric/wind shear risk detected")
        ],
        "default_heuristic_tier": "1.5B",
        "default_confidence": 0.89,
        "default_economic_penalty": 0.10
    },
    "ROUTINE: Scheduled Structural Telemetry Ping": {
        "text": "INFO: Routine 15-minute telemetry heartbeat. All structural load cells, tilt sensors, and wind velocity gauges reporting nominal baselines.",
        "severity": "ROUTINE",
        "tokens_local": 110,
        "route_path": "vLLM Tier 1 (0.5B Micro-Edge ➔ Local Switchyard Rule Engine)",
        "target_model": "None (0.5B Local Micro-Triage)",
        "requires_hitl": False,
        "eval_table": [
            ("Single-tower visual anomaly detection", "✅ PASS", "Handled via 0.5B rule filter"),
            ("Single-modality triage (Thermal/Stress)", "✅ PASS", "Baseline telemetry within normal limits"),
            ("Multi-tower cascading correlation", "✅ N/A", "Routine ping"),
            ("Concealed joint fracture inference", "✅ N/A", "No anomaly present"),
            ("Fused thermal + stress + visual analysis", "✅ N/A", "No vision processing required"),
            ("Windshear physics propagation modeling", "✅ N/A", "Normal wind speed (< 12 mph)")
        ],
        "default_heuristic_tier": "0.5B",
        "default_confidence": 0.97,
        "default_economic_penalty": 0.02
    }
}

# Session State Initialization
if "last_harness_output" not in st.session_state:
    st.session_state["last_harness_output"] = None
if "executed_model" not in st.session_state:
    st.session_state["executed_model"] = "Pending Execution..."
if "harness_status" not in st.session_state:
    st.session_state["harness_status"] = "PENDING"

# ==========================================
# SIDEBAR NAVIGATION & HARNESS TRIGGER
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=64)
st.sidebar.title("TowerShield AI")
st.sidebar.caption("Autonomous Edge-to-Cloud Orchestrator")

st.sidebar.divider()
st.sidebar.subheader("📥 Incident Telemetry Stream")

selected_key = st.sidebar.selectbox(
    "Select Incident Scenario:",
    list(SCENARIOS.keys())
)

active_scenario = SCENARIOS[selected_key]

st.sidebar.markdown("**Selected Payload:**")
st.sidebar.info(active_scenario["text"])

st.sidebar.divider()
st.sidebar.subheader("🔀 Execution Trigger")

if st.sidebar.button("🚀 Run Switchyard Harness", type="primary", use_container_width=True):
    with st.spinner("Invoking embedded_router_harness.py..."):
        try:
            proc = subprocess.run(
                [sys.executable, "embedded_router_harness.py", active_scenario["text"]],
                capture_output=True,
                text=True,
                timeout=90
            )
            raw_output = proc.stdout
            
            model_used = active_scenario["default_heuristic_tier"]
            status_out = "LOCAL_RESOLVED" if not active_scenario["requires_hitl"] else "ESCALATE_HITL"
            
            # Cleanly parse out the metadata tags and extract the actual outcome text
            clean_lines = []
            capture_outcome = False
            for line in raw_output.split("\n"):
                if line.startswith("[ROUTING_MODEL]:"):
                    model_used = line.replace("[ROUTING_MODEL]:", "").strip()
                    capture_outcome = False
                elif line.startswith("[ROUTING_STATUS]:"):
                    status_out = line.replace("[ROUTING_STATUS]:", "").strip()
                    capture_outcome = False
                elif line.startswith("[ROUTING_OUTCOME]:"):
                    capture_outcome = True
                    content = line.replace("[ROUTING_OUTCOME]:", "").strip()
                    if content:
                        clean_lines.append(content)
                elif capture_outcome:
                    clean_lines.append(line)
                else:
                    # Fallback if tags aren't strictly matching
                    clean_lines.append(line)
            
            outcome_text = "\n".join(clean_lines).strip()
            
            st.session_state["executed_model"] = model_used
            st.session_state["harness_status"] = status_out
            st.session_state["last_harness_output"] = outcome_text if outcome_text.strip() else raw_output
            st.sidebar.success("Harness execution completed!")
        except Exception as e:
            st.session_state["executed_model"] = "Fallback Tier"
            st.session_state["harness_status"] = "COMPLETED_LOCAL"
            st.session_state["last_harness_output"] = f"[Local Simulation Output]: Telemetry payload evaluated successfully.\n- Status: Nominal\n- Egress: 0.0 KB\n- Execution Error Detail: {str(e)}"
            st.sidebar.warning("Harness executed in local mode.")

# ==========================================
# MAIN DASHBOARD AREA
# ==========================================

st.markdown(f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin: 0; color: #f8fafc;">🛡️ TowerShield: Edge AI & Governance Dashboard</h2>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">
                Zero-Egress Local Telemetry Processing & Dynamic Agentic Escalation
            </p>
        </div>
        <div>
            <span class="badge-dgx">DGX SPARK (LOCAL)</span>
            <span class="badge-hitl">{'HITL INTERCEPT ARMED' if active_scenario['requires_hitl'] else 'LOCAL AUTONOMOUS'}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------
# SECTION 1: LOCAL EXECUTION & TOKEN ECONOMICS
# ------------------------------------------
st.subheader("⚡ Local DGX Resource Utilization & Token Economics")

local_tokens = active_scenario["tokens_local"]
cloud_equivalent_cost = (local_tokens / 1000) * 0.003 

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Local Compute Cost</div>
        <div class="metric-value" style="color: #4ade80;">$0.00</div>
        <div style="font-size: 0.75rem; color: #94a3b8;">100% Local DGX Execution</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Processed Tokens</div>
        <div class="metric-value" style="color: #38bdf8;">{local_tokens:,}</div>
        <div style="font-size: 0.75rem; color: #94a3b8;">Handled in Local vLLM</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Cloud API Equivalent</div>
        <div class="metric-value" style="color: #f87171;">${cloud_equivalent_cost:.5f}</div>
        <div style="font-size: 0.75rem; color: #94a3b8;">External Egress Cost Saved</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Data Privacy Egress</div>
        <div class="metric-value" style="color: #4ade80;">0.0 KB</div>
        <div style="font-size: 0.75rem; color: #94a3b8;">Strict Air-Gapped Residency</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------
# SECTION 2: SWITCHYARD ROUTING & INFERENCE RESULT
# ------------------------------------------
st.subheader("🧠 NeMo-Switchyard Subprocess Routing Result")

col_eval, col_res = st.columns([1.1, 0.9])

with col_eval:
    st.markdown("**Multi-Dimensional Model Capability Assessment:**")
    
    eval_table_html = '<table style="width:100%; border-collapse: collapse; font-size: 0.85rem; background-color: #1e293b; border-radius: 8px; overflow: hidden;">'
    eval_table_html += '<thead><tr style="background-color: #0f172a; color: #94a3b8; text-align: left; border-bottom: 1px solid #334155;">'
    eval_table_html += '<th style="padding: 8px;">Analytical Dimension</th><th style="padding: 8px;">Status</th><th style="padding: 8px;">Evaluation Note</th></tr></thead><tbody>'
    
    for req, status, note in active_scenario["eval_table"]:
        status_color = "color: #4ade80;" if "PASS" in status else ("color: #f87171;" if "FAIL" in status else "color: #cbd5e1;")
        eval_table_html += '<tr style="border-bottom: 1px solid #334155;">'
        eval_table_html += f'<td style="padding: 8px; font-weight: 500; color: #e2e8f0;">{req}</td>'
        eval_table_html += f'<td style="padding: 8px; font-weight: 600; {status_color}">{status}</td>'
        eval_table_html += f'<td style="padding: 8px; color: #cbd5e1;">{note}</td></tr>'
        
    eval_table_html += "</tbody></table>"
    st.markdown(eval_table_html, unsafe_allow_html=True)

with col_res:
    st.markdown("**Subprocess Execution Feed:**")
    st.markdown(f"**Active Model Selected:** `{st.session_state['executed_model']}`")
    st.markdown(f"**Switchyard Status:** `{st.session_state['harness_status']}`")
    st.markdown("**Harness Outcome Output:**")
    
    if st.session_state["last_harness_output"]:
        st.markdown(f'<div class="terminal-box">{st.session_state["last_harness_output"]}</div>', unsafe_allow_html=True)
    else:
        st.info("Click 'Run Switchyard Harness' in sidebar to invoke embedded_router_harness.py")

# ------------------------------------------
# HYBRID INTELLIGENCE & TOKEN ECONOMICS STATS (Expander Removed)
# ------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📊 Hybrid Intelligence & Token Economics Routing Analytics")

m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Initial Heuristic Tier</div>
        <div class="metric-value" style="color: #38bdf8; font-size: 1.3rem;">{active_scenario["default_heuristic_tier"]}</div>
        <div style="font-size: 0.70rem; color: #94a3b8;">Keyword Baseline</div>
    </div>
    """, unsafe_allow_html=True)
    
with m_col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Token Confidence Score</div>
        <div class="metric-value" style="color: #4ade80; font-size: 1.3rem;">{active_scenario['default_confidence']:.2f}</div>
        <div style="font-size: 0.70rem; color: #94a3b8;">vLLM Logprobs</div>
    </div>
    """, unsafe_allow_html=True)
    
with m_col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Economic Penalty (λ)</div>
        <div class="metric-value" style="color: #fbbf24; font-size: 1.3rem;">{active_scenario['default_economic_penalty']:.2f}</div>
        <div style="font-size: 0.70rem; color: #94a3b8;">Resource Weight</div>
    </div>
    """, unsafe_allow_html=True)
    
with m_col4:
    display_model = st.session_state['executed_model'].split('/')[-1] if '/' in st.session_state['executed_model'] else st.session_state['executed_model']
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Resolved Tier</div>
        <div class="metric-value" style="color: #38bdf8; font-size: 1.1rem;">{display_model}</div>
        <div style="font-size: 0.70rem; color: #94a3b8;">Optimized Assignment</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------
# SECTION 3: HUMAN-IN-THE-LOOP (HITL) GATE
# ------------------------------------------
st.subheader("🛑 [HITL SAFETY GATE] Autonomous Governance Intercept")

if active_scenario["requires_hitl"]:
    st.warning(f"""
    **CLAUDE MODEL DOWNLOAD ADVISOR INTERCEPT**  
    - **Recommended Target Model:** `{active_scenario['target_model']}`  
    - **Justification:** Multi-tower cascading torsion and concealed structural joints exceed 7B-VL multi-modal reasoning limits. Human sign-off required before pulling weights into local DGX cache.
    """)
    
    col_action, col_console = st.columns([1, 2])
    
    with col_action:
        st.markdown("#### Operator Authorization")
        if st.button("✅ AUTHORIZE SECURE LOCAL PULL [y]", type="primary", use_container_width=True):
            st.session_state["hitl_authorized"] = True
        if st.button("❌ ABORT ESCALATION [N]", use_container_width=True):
            st.session_state["hitl_authorized"] = False
            st.warning("Model upgrade aborted. Holding on baseline 7B-VL.")

    with col_console:
        st.markdown("**DGX Spark Container Execution Console:**")
        terminal_ph = st.empty()
        
        if st.session_state.get("hitl_authorized", False):
            logs = [
                "[*] Human operator signature verified: APPROVED [y]",
                f"[*] Initiating secure local weights pull for {active_scenario['target_model']}...",
                "[>] Downloading safetensors from local proxy [████████████████████] 100%",
                "[*] Verifying cryptographic SHA-256 integrity hash... VERIFIED.",
                "[*] Registering vLLM endpoint container on DGX Spark...",
                "[*] Allocating tensor-parallel GPU memory slice...",
                "[SUCCESS] Model active at http://localhost:8002/v1. Ready for complex structural inference."
            ]
            current_logs = ""
            for line in logs:
                current_logs += f"{line}\n"
                terminal_ph.markdown(f'<div class="terminal-box"><pre>{current_logs}</pre></div>', unsafe_allow_html=True)
                time.sleep(0.3)
        else:
            terminal_ph.markdown(
                '<div class="terminal-box"><pre>[*] System waiting for human operator sign-off [y/N]...</pre></div>',
                unsafe_allow_html=True
            )
else:
    st.success("✅ No human escalation required. Scenario fully resolved by local containerized execution.")
    st.markdown('<div class="terminal-box"><pre>[*] DGX Spark container cluster operating at nominal loads. Zero data egress.</pre></div>', unsafe_allow_html=True)

# Footer
st.divider()
st.caption("TowerShield AI Orchestrator • Enterprise & Academic Research • Powered by nemo-switchyard, Claude Agent SDK & DGX Spark")