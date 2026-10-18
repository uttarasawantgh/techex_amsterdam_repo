# 🛡️ TowerShield AI: Edge AI Governance & Bidirectional Compute Router

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![vLLM: Enabled](https://img.shields.io/badge/vLLM-Local%20Inference-green.svg)](https://github.com/vllm-project/vllm)
[![Hardware: NVIDIA DGX Spark](https://img.shields.io/badge/Hardware-NVIDIA%20DGX%20Spark-76B900.svg)](https://www.nvidia.com/)
[![Framework: Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)

> **A production-grade, air-gapped, tri-tiered local compute router for DGX-powered cell tower safety systems.**  
> Features bidirectional token-economic elasticity, multi-hop sequential model escalation, staged downward optimization cascades, and Human-In-The-Loop (HITL) safety governance.

---

## 📌 Executive Summary & Core Challenge

Telecommunication tower infrastructure requires continuous structural health monitoring, thermal analysis, and environmental hazard detection. Relying solely on cloud-hosted LLM architectures introduces critical vulnerabilities:

1. **High Cloud Egress Costs:** Transmitting raw multi-modal sensor telemetry and vision feeds strains network bandwidth and operational budgets.
2. **Latency Risks:** Cloud roundtrip latency prevents real-time mitigation during high-velocity windshear or rapid structural torsion.
3. **Zero-Egress Security Mandates:** Strict regulatory and air-gapped network policies demand that operational data remains strictly localized on the edge node.

**TowerShield AI** solves these challenges by deploying a dynamic **3-Pillar Compute Router** on an **NVIDIA DGX Spark** edge cluster. It dynamically balances computational cost, latency, and reasoning depth through a tri-tiered local model stack—guaranteeing **100% on-premise residency ($0.00 cloud egress)** while upholding rigorous safety guardrails.

---

## 🏛️ System Architecture & The 3-Pillar Routing Model

TowerShield orchestrates compute load across three dedicated vLLM model containers hosted locally on the DGX Spark node:

```
                          ┌────────────────────────────────────────┐
                          │   Incoming Sensor Telemetry / Event    │
                          └───────────────────┬────────────────────┘
                                              │
                                              ▼
                        ┌──────────────────────────────────────────┐
                        │ PILLAR 1: Keyword Heuristics & Intent    │
                        └─────────────────────┬────────────────────┘
                                              │
           ┌──────────────────────────────────┼──────────────────────────────────┐
           │                                  │                                  │
           ▼                                  ▼                                  ▼
┌──────────────────────┐           ┌──────────────────────┐           ┌──────────────────────┐
│     0.5B Tier        │           │     1.5B Tier        │           │     7B-VL Tier       │
│ Micro-Edge Filter    │           │ Operational Mid-Tier │           │  Multimodal Vision   │
│   (Port 8003)        │           │   (Port 8002)        │           │   (Port 8001)        │
└──────────┬───────────┘           └──────────┬───────────┘           └──────────┬───────────┘
           │                                  │                                  │
           └──────────────────────────────────┼──────────────────────────────────┘
                                              │
                                              ▼
                        ┌──────────────────────────────────────────┐
                        │ PILLAR 2 & 3: Logprob Confidence &       │
                        │        Token Economics Engine            │
                        └─────────────────────┬────────────────────┘
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     │                                                 │
                     ▼                                                 ▼
      [ STAGED DOWNWARD OPTIMIZATION ]               [ MULTI-HOP SEQUENTIAL ESCALATION ]
      High-tier audit confirmed nominal             Uncertainty > threshold; steps up
         7B-VL ➔ 1.5B ➔ 0.5B settlement                   1.5B ➔ 7B-VL verification
                     │                                                 │
                     └────────────────────────┬────────────────────────┘
                                              │
                                              ▼
                            ┌────────────────────────────────────┐
                            │    CRITICAL HARD SAFETY CHECK      │
                            └─────────────────┬──────────────────┘
                                              │
                                              ├──────► [ LOCAL_RESOLVED ]
                                              │
                                              └──────► [ ESCALATE_HITL ] 
                                                       Operator Sign-off Gate
```

### Routing Pillars Breakdown

* **Pillar 1: Keyword Heuristics & Baseline Intent:** Evaluates initial text prompts for deterministic markers (`CRITICAL`, `WARNING`, `AUDIT`, `INFO`) to select an optimal baseline model container.
* **Pillar 2: Execution & Logprob Confidence Scoring:** Measures token output probabilities during initial evaluation to calculate real-time model uncertainty.
* **Pillar 3: Token Economics Engine:** Weighs computational cost ($\Lambda$ penalty) against model confidence to dynamically adjust routing paths.

---

## ⚙️ Tri-Tiered Local vLLM Engine Setup

The system manages three concurrent containerized models running on local `vLLM` endpoints:

| Model Tier | Base Weights | Target Port | VRAM Allocation | Operational Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Micro-Edge** | `Qwen/Qwen2.5-0.5B-Instruct` | `8003` | 15% VRAM | Sub-second triage for routine pings & noise filtering |
| **Operational** | `Qwen/Qwen2.5-1.5B-Instruct` | `8002` | 25% VRAM | Mid-tier diagnostic checks & warning evaluations |
| **Multimodal** | `Qwen/Qwen2.5-VL-7B-Instruct` | `8001` | 45% VRAM | Complex visual anomaly, structural load & cross-modality verification |

---

## ⚡ Key Architectural Features

1. **Staged Downward Optimization Cascade ($7B \rightarrow 1.5B \rightarrow 0.5B$):**  
   When a thorough scan is initiated on the heavy `7B-VL` engine and evaluates high stability ($>0.70$ confidence), the system gracefully cascades down through intermediate profiles to settle on the micro-edge tier, conserving DGX compute load for pending tasks.

2. **Multi-Hop Sequential Escalation Logic ($1.5B \rightarrow 7B-VL$):**  
   If an initial triage on a mid-tier model encounters ambiguity or sensor jitter, the economic uncertainty formula ($U_{penalty} + E_{penalty} > \text{threshold}$) automatically triggers an upward hop to `7B-VL`, injecting Hop 1 findings into Hop 2 as multi-modal context.

3. **`ESCALATE_HITL` Governance Circuit Breaker:**  
   Catastrophic structural threats (e.g., multi-tower cascading torsion) immediately trip an unbreakable hard safety lock. The system halts unverified automated execution and securely routes to an interactive Human-In-The-Loop gate requiring explicit operator authorization.

---

## 📂 Repository Structure

```text
techex_amsterdam_repo/
├── app.py                         # Streamlit Governance UI & Executive Dashboard
├── embedded_router_harness.py     # Backend Router Engine & Multi-Hop Execution Logic
├── requirements.txt               # Dependencies (vLLM, Streamlit, OpenAI SDK, PyTorch)
├── README.md                      # Architecture Documentation & Master Guide
└── assets/                        # Architecture diagrams and UI screenshots
```

---

## 🚀 Installation & DGX Spark Setup Guide

### 1. Prerequisites
* NVIDIA DGX Spark / On-Premise GPU Node (CUDA 12.0+)
* Python 3.10 or higher
* Docker & NVIDIA Container Toolkit installed

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/uttarasawantgh/techex_amsterdam_repo.git
cd techex_amsterdam_repo

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Launch Local vLLM Inference Engines
Initialize the three local vLLM model containers across distinct ports:

```bash
# Port 8001: 7B-VL Multimodal Engine
python3 -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-VL-7B-Instruct --port 8001 &

# Port 8002: 1.5B Operational Engine
python3 -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-1.5B-Instruct --port 8002 &

# Port 8003: 0.5B Micro-Edge Filter
python3 -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-0.5B-Instruct --port 8003 &
```

---

## 🎮 Step-by-Step Live Demo Guide

To demonstrate the full bidirectional governance architecture, execute the following four test cases across the split **Streamlit UI** and **VS Code CLI** environments.

---

### 🖥️ Part 1: Streamlit UI Demonstrations

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```

#### Test Case 1: The Critical Test Case (Hard Safety & HITL Intercept)
* **Objective:** Demonstrate automated hard-safety circuit breaking and Human-In-The-Loop (HITL) operator control.
* **Selection:** Select `CRITICAL: Multi-Tower Windshear Torsion (Tower 4)` from the scenario dropdown.
* **Prompt Payload:**  
  `CRITICAL ALERT: Complex multi-tower cascading structural torsion detected across Tower 4 and adjacent relay masts following high-velocity windshear. Thermal and stress fractures span multiple concealed structural joints.`
* **Expected Result:**  
  The dashboard flags the alert, halts automated action, and locks into **`ESCALATE_HITL`**. Scroll down to inspect the **HITL Safety Gate** and click `✅ AUTHORIZE SECURE LOCAL PULL [y]` to simulate operator intervention.

#### Test Case 2: The Routine Test Case (Micro-Edge Baseline)
* **Objective:** Demonstrate sub-second zero-cost telemetry filtering on the micro-edge profile.
* **Selection:** Select `ROUTINE: Scheduled Structural Telemetry Ping` from the scenario dropdown.
* **Prompt Payload:**  
  `INFO: Routine 15-minute telemetry heartbeat. All structural load cells, tilt sensors, and wind velocity gauges reporting nominal baselines.`
* **Expected Result:**  
  Resolves instantly via `0.5B Micro-Edge Filter` as **`LOCAL_RESOLVED`** with $0.00 cloud egress cost.

---

### ⌨️ Part 2: VS Code CLI Demonstrations

Execute raw execution traces directly in your terminal to view real-time logprob confidence scoring and model-hopping.

#### Test Case 3: The Audit Test Case (Staged Downward Optimization Cascade)
* **Objective:** Verify downward compute-shedding ($7\text{B} \rightarrow 1.5\text{B} \rightarrow 0.5\text{B}$) when a heavy audit confirms baseline stability.
* **CLI Command:**
  ```bash
  python3 embedded_router_harness.py "AUDIT: Comprehensive structural and thermal scan for Tower 2, all metrics completely nominal and baseline stable"
  ```
* **Expected CLI Output:**
  ```text
  [ROUTING_MODEL]: Qwen/Qwen2.5-VL-7B-Instruct
  [ROUTING_STATUS]: LOCAL_RESOLVED
  [DOWNWARD OPTIMIZATION TRACE]:
  -> Initial Tier: 7B-VL High-Precision Scan
  -> High Token Confidence Evaluated (>0.70)
  -> Stepped Down [1.5B Mid-Tier]: Nominal telemetry confirmed.
  -> Final Economic Settlement [0.5B Profile]: Resource load minimized.
  ```

#### Test Case 4: The Upward Escalation Test Case (Up-Step Hop)
* **Objective:** Verify dynamic upward compute scaling ($1.5\text{B} \rightarrow 7\text{B-VL}$) when encountering ambiguous multi-modal variables.
* **CLI Command:**
  ```bash
  python3 embedded_router_harness.py "WARNING: Unconfirmed thermal gradient fluctuating near joint 4B alongside intermittent sensor jitter; correlation to structural load unknown."
  ```
* **Expected CLI Output:**
  ```text
  [ROUTING_MODEL]: Qwen/Qwen2.5-1.5B-Instruct
  [ROUTING_STATUS]: LOCAL_RESOLVED
  [MULTI-HOP EXECUTION TRACE]:
  Hop 1 [Qwen/Qwen2.5-1.5B-Instruct]: Initial evaluation completed (Confidence: 0.65).
  -> Escalation Triggered: Economic uncertainty penalty exceeded threshold (0.55).
  -> Hop 2 Escalated [Qwen/Qwen2.5-VL-7B-Instruct]: Secondary deep visual & structural verification completed.
  ```

---

## 🛠️ Tech Stack

* **Inference Engine:** [vLLM](https://github.com/vllm-project/vllm) (Local OpenAI-compatible REST endpoints)
* **Models:** Qwen2.5 Series (`0.5B-Instruct`, `1.5B-Instruct`, `VL-7B-Instruct`)
* **Frontend UI:** Streamlit
* **Backend Runtime:** Python 3.10 / PyTorch / OpenAI Python API
* **Hardware Target:** NVIDIA DGX Spark / Local CUDA Acceleration

---

## 👤 Author & Acknowledgments

* **Author:** Uttara Sawant  
* **GitHub:** [@uttarasawantgh](https://github.com/uttarasawantgh)
* **Gemini:** Utilized as an AI collaborator for architectural troubleshooting, debugging complex structural normalization logic, and optimizing code documentation. 
