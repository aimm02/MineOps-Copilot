# MineOps-Copilot: AI-Powered Fleet Maintenance & Safety Command

MineOps-Copilot is an intelligent, Multi-Agent Retrieval-Augmented Generation (RAG) system designed specifically for the predictive maintenance and safety compliance (K3) of Komatsu HD785-5 dump truck fleets. By integrating static technical manuals with live telemetry data, this system serves as a central advisory unit for fleet commanders and maintenance crews.

## ⚠️ The Problem
In heavy-duty mining operations, unscheduled equipment downtime results in severe financial losses and disrupted supply chains. Furthermore, diagnosing mechanical anomalies using thousands of pages of static technical manuals is time-consuming and prone to human error. Ensuring strict compliance with K3 safety regulations (such as Kepmen ESDM 1827) during high-pressure maintenance scenarios is often challenging, increasing the risk of workplace accidents.

## 🎯 Objectives
*   **Accelerate Diagnostics:** Reduce the time required to cross-reference mechanical symptoms with official repair manuals.
*   **Enforce Safety Protocols:** Automatically integrate mandatory K3 procedures (e.g., Lockout/Tagout - LOTO) into every maintenance directive.
*   **Predictive Shift:** Transition fleet management from a reactive maintenance model to a proactive, data-driven strategy.

## 💡 System Utility & Use Cases
MineOps-Copilot empowers mechanics, safety officers, and fleet managers to:
1.  Query exact procedural steps for specific fault codes or mechanical issues instantly.
2.  Correlate real-time equipment fatigue (via telemetry) with historical baseline thresholds.
3.  Generate comprehensive, step-by-step repair plans that are strictly bound by national mining safety regulations.

## ⚙️ Core System Components
The architecture is built on a highly modular, agentic framework:
*   **Multi-Agent RAG Engine:** Utilizes LangGraph to route user queries between specific diagnostic agents, retrieving context-aware answers from vector databases.
*   **Real-Time Telemetry Dashboard:** A live visual interface tracking payload, engine/transmission temperatures, brake pressure, and drivetrain vibrations.
*   **K3 Compliance Validator:** An automated safeguard that ensures every generated output complies with heavy-equipment safety standards.
*   **Ragas Evaluation Framework:** A built-in validation pipeline testing the LLM's output against 4 critical metrics (Faithfulness, Answer Relevancy, Context Precision, and Context Recall) to guarantee hallucination-free diagnostics.

## 🛠️ Technology Stack
*   **Application Framework:** Streamlit (Frontend), LangGraph & LangChain (Orchestration)
*   **LLM & Embeddings:** Google Gemini 1.5 Flash API, `gemini-embedding-001`
*   **Vector Database:** ChromaDB (for technical documents and manuals)
*   **Relational Database:** SQLite (for telemetry data and session state management)
*   **Evaluation & Benchmarking:** Ragas Framework, Pandas

---

## 📊 Real-Time Equipment Telemetry

![Active Telemetry Dashboard](telemetry-dashboard.png)

The MineOps-Copilot integrates a live telemetry monitoring module specifically configured for the Komatsu HD785-5 fleet. This interface captures and visualizes continuous operational data streams, tracking critical mechanical metrics including payload capacity, engine and transmission fluid temperatures, brake line pressure, and drivetrain vibrations.

Coupled with the RAG-powered analytical engine, this dashboard serves as the foundation for predictive maintenance. By correlating live mechanical trends against historical baseline thresholds and K3 safety regulations, the system enables fleet commanders to preemptively identify anomalies, mitigate equipment fatigue, and issue data-driven maintenance directives before catastrophic failures occur.