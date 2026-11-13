📊 AI Lifestyle & Budget Auditor
- An interactive personal finance and lifestyle analytics application built with Python, Streamlit, Google GenAI SDK (gemini-3.8-flash), Pydantic, Pandas, and Plotly.

🏗️ Data Pipeline & Architecture
- Flow: Streamlit UI (Demo / BYOK) ➔ Structured Prompt ➔ Gemini 3.8 Flash (JSON Mode + Pydantic) ➔ Pandas DataFrame ➔ Plotly Interactive Dashboard & CSV Export 

✨ Key Engineering Highlights
- Deterministic Schema Enforcement (Pydantic + JSON Mode): Enforces strict output schemas (BudgetCategoryAudit, LifestyleInsight, ActionStep) so LLM responses map reliably into relational tables without parsing failures.
- Hybrid Execution Model (Interactive Demo + BYOK): Allows instant exploration via pre-computed sample scenarios or live real-time audits using the user's own Gemini API key (stored strictly in session memory).
- LLM Semantics + Pandas Precision: Combines AI-driven cross-domain insights (e.g., linking elevated stress and sleep deficit to discretionary spending) with deterministic share calculations and balance reconciliation in Pandas.
- Interactive BI Visualizations (Plotly Express): Features net income allocation donut charts, status-coded efficiency bar charts (Optimal, Warning, Critical), and one-click CSV exports.

🚀 Run Locally

1. Clone the repository: git clone https://github.com/michalfabiny/ai-lifestyle-auditor.git
2. Create & activate virtual environment: python3 -m venv .venv && source .venv/bin/activate
3. Install dependencies: pip install -r requirements.txt
4. Run the app: streamlit run app.py
