import json
import os
from typing import Literal
from dotenv import load_dotenv
from google import genai
from google.genai import types
import pydantic
from pydantic import BaseModel, Field
import streamlit as st
import pandas as pd
import plotly.express as px

# Načítanie API kľúča z .env súboru do systémových premenných
load_dotenv()

st.set_page_config(
    page_title="AI Lifestyle & Budget Auditor", page_icon="📊", layout="wide"
)


# Cachujeme klienta, aby sa pri každom kliknutí v UI nevytváral odznova
@st.cache_resource
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


client = get_gemini_client()

st.title("📊 AI Lifestyle & Budget Auditor")
st.markdown(
    "Intelligent personal finance and habit audit powered by **Gemini 3.8 Flash**, **Pydantic**, **Pandas**, and **Plotly**."
)
# --- STEP 1: DATA CONTRACT DEFINITION (PYDANTIC SCHEMA - EN) ---
class BudgetCategoryAudit(BaseModel):
    category: str = Field(description="Expense category name")
    amount: float = Field(description="Monthly amount in EUR")
    share_percent: float = Field(
        description="Percentage share of the expense relative to net income"
    )
    status: Literal["Optimal", "Warning", "Critical"]
    recommendation: str = Field(
        description="Concise, actionable recommendation for this category"
    )


class LifestyleInsight(BaseModel):
    domain: str = Field(
        description="Lifestyle domain (e.g., Sleep, Physical Activity, Stress)"
    )
    current_value: str = Field(description="Current value entered by the user")
    impact: str = Field(
        description="How this habit affects energy, health, and work performance"
    )
    action_item: str = Field(description="Concrete step for improvement")


class ActionStep(BaseModel):
    step: str = Field(description="Concrete action step")
    horizon: Literal["Short-term (within 30 days)", "Long-term (3-12 months)"]
    priority: Literal["High", "Medium"]


class AuditReport(BaseModel):
    overall_score: int = Field(
        description="Overall financial and lifestyle health score from 0 to 100"
    )
    executive_summary: str = Field(
        description="Executive summary of the situation in 2-3 punchy sentences"
    )
    budget_analysis: list[BudgetCategoryAudit]
    lifestyle_insights: list[LifestyleInsight]
    action_plan: list[ActionStep]
# --- SIDEBAR: MODE SELECTION & BYOK CONFIGURATION ---
st.sidebar.header("⚙️ Configuration & Mode")
app_mode = st.sidebar.radio(
    "Select Execution Mode:",
    options=["Interactive Demo (Sample Data)", "Live AI Audit (Your API Key)"],
    help="Use Demo mode to explore the dashboard instantly, or enter your own Gemini API key for a live audit.",
)

user_api_key = ""
if app_mode == "Live AI Audit (Your API Key)":
    # Lokálne na tvojom Macu predvyplní kľúč z .env, na verejnom webe bude pole prázdne
    default_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.sidebar.text_input(
        "🔑 Enter your Gemini API Key",
        value=default_key,
        type="password",
        placeholder="AIzaSy...",
        help="Your key is stored only in your current browser session and never saved to disk.",
    )
    if not user_api_key:
        st.sidebar.warning("⚠️ Please enter a Gemini API Key to run a live audit.")
else:
    st.sidebar.info("💡 Demo mode active: Uses pre-computed realistic audit data without API calls.")



# --- STEP 3: SIDEBAR INPUT FORM (EN) ---
st.sidebar.header("📝 Monthly Inputs")

with st.sidebar.form("audit_form"):
    st.subheader("💰 Finances (€ / month)")
    income = st.number_input(
        "Net Monthly Income (€)", min_value=0, value=1800, step=50
    )
    housing = st.number_input(
        "Housing & Utilities (€)", min_value=0, value=600, step=20
    )
    food = st.number_input(
        "Groceries & Household (€)", min_value=0, value=350, step=20
    )
    transport = st.number_input(
        "Transport & Car (€)", min_value=0, value=150, step=10
    )
    leisure = st.number_input(
        "Leisure, Dining & Hobbies (€)", min_value=0, value=250, step=20
    )

    st.subheader("🏃‍♂️ Lifestyle (Average)")
    sleep_hours = st.slider(
        "Average Sleep (hours/day)",
        min_value=3.0,
        max_value=12.0,
        value=6.5,
        step=0.5,
    )
    sport_sessions = st.slider(
        "Exercise / Workouts (sessions/week)",
        min_value=0,
        max_value=14,
        value=3,
        step=1,
    )
    stress_level = st.select_slider(
        "Subjective Stress Level",
        options=["Low", "Moderate", "Elevated", "High", "Critical"],
        value="Elevated",
    )

    submitted = st.form_submit_button(
        "🚀 Run AI Audit", use_container_width=True
    )
    
    

    

# Spracovanie po odoslaní formulára
# --- KROK 4B: VOLANIE GEMINI API V JSON MODE ---
# --- STEP 4: DATA PROCESSING (DEMO OR LIVE BYOK) & SESSION STATE ---
if submitted:
    total_expenses = housing + food + transport + leisure
    savings = income - total_expenses

    user_data = {
        "finances": {
            "net_income": income,
            "expenses": {
                "Housing & Utilities": housing,
                "Groceries & Household": food,
                "Transport & Car": transport,
                "Leisure, Dining & Hobbies": leisure,
            },
            "total_expenses": total_expenses,
            "monthly_savings": savings,
        },
        "lifestyle": {
            "sleep_hours": sleep_hours,
            "workouts_per_week": sport_sessions,
            "stress_level": stress_level,
        },
    }

    if app_mode == "Interactive Demo (Sample Data)":
        # Pre-computed realistic JSON matching the exact AuditReport schema
        demo_report = {
            "overall_score": 76,
            "executive_summary": (
                "Your financial foundation is solid with a healthy 25% savings rate, "
                "giving you strong resilience. However, elevated stress combined with "
                "6.5 hours of sleep creates a recovery bottleneck that can impact long-term productivity."
            ),
            "budget_analysis": [
                {
                    "category": "Housing & Utilities",
                    "amount": float(housing),
                    "share_percent": round((housing / income) * 100, 1) if income else 0,
                    "status": "Warning" if (income and housing / income > 0.30) else "Optimal",
                    "recommendation": "Keep fixed housing costs near or below 30% of net income to preserve cash-flow flexibility.",
                },
                {
                    "category": "Groceries & Household",
                    "amount": float(food),
                    "share_percent": round((food / income) * 100, 1) if income else 0,
                    "status": "Optimal",
                    "recommendation": "Well-balanced nutrition budget; focus on high-protein meal prep to save time on busy workdays.",
                },
                {
                    "category": "Transport & Car",
                    "amount": float(transport),
                    "share_percent": round((transport / income) * 100, 1) if income else 0,
                    "status": "Optimal",
                    "recommendation": "Efficient mobility spending that keeps fixed commuting overhead low.",
                },
                {
                    "category": "Leisure, Dining & Hobbies",
                    "amount": float(leisure),
                    "share_percent": round((leisure / income) * 100, 1) if income else 0,
                    "status": "Warning" if (income and leisure / income > 0.15) else "Optimal",
                    "recommendation": "Audit impulse dining out; prioritize activities that actively reduce stress and improve recovery.",
                },
            ],
            "lifestyle_insights": [
                {
                    "domain": "Sleep Recovery",
                    "current_value": f"{sleep_hours} hrs/day",
                    "impact": "Sub-7-hour sleep elevates cortisol and reduces cognitive focus during analytical tasks.",
                    "action_item": "Set a consistent wind-down routine 45 minutes before bed to gain +30–45 minutes of sleep.",
                },
                {
                    "domain": "Physical Activity",
                    "current_value": f"{sport_sessions} sessions/week",
                    "impact": "Regular training supports metabolic health and acts as a strong buffer against work stress.",
                    "action_item": "Maintain 3 structured workouts per week and add light outdoor walks on rest days.",
                },
                {
                    "domain": "Stress Management",
                    "current_value": stress_level,
                    "impact": "Sustained elevated stress increases the risk of burnout and emotional spending.",
                    "action_item": "Schedule two 15-minute screen-free decompression blocks daily.",
                },
            ],
            "action_plan": [
                {
                    "step": "Automate monthly transfer of remaining savings into a dedicated high-yield or investment account.",
                    "horizon": "Short-term (within 30 days)",
                    "priority": "High",
                },
                {
                    "step": "Extend average sleep duration from 6.5 to 7.2 hours using a fixed evening shutdown alarm.",
                    "horizon": "Short-term (within 30 days)",
                    "priority": "High",
                },
                {
                    "step": "Build a 6-month emergency fund and review recurring subscriptions quarterly.",
                    "horizon": "Long-term (3-12 months)",
                    "priority": "Medium",
                },
            ],
        }
        st.session_state["audit_result"] = demo_report
        st.session_state["user_inputs"] = user_data
        st.session_state["run_source"] = "Interactive Demo"

    else:
        if not user_api_key:
            st.error("⚠️ Please enter your Gemini API Key in the sidebar before running a Live AI Audit.")
        else:
            system_prompt = (
                "You are an experienced financial analyst and healthy lifestyle coach. "
                "Analyze the user's input data objectively, empathetically, and practically. "
                "Identify cross-domain connections between finances and stress/lifestyle. "
                "Respond strictly in English."
            )
            with st.spinner("🤖 Gemini 3.8 Flash is auditing your finances and habits..."):
                try:
                    live_client = genai.Client(api_key=user_api_key)
                    response = live_client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=f"Perform a comprehensive audit of this data:\n{json.dumps(user_data)}",
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            response_mime_type="application/json",
                            response_schema=AuditReport,
                            temperature=0.2,
                        ),
                    )
                    st.session_state["audit_result"] = json.loads(response.text)
                    st.session_state["user_inputs"] = user_data
                    st.session_state["run_source"] = "Gemini 3.8 Flash (Live)"
                except Exception as e:
                    st.error(f"❌ Gemini API Error: {e}")

# --- STEP 5 & 6: PERSISTENT PANDAS TRANSFORMATION & PLOTLY DASHBOARD ---
if "audit_result" in st.session_state:
    audit_result = st.session_state["audit_result"]
    saved_inputs = st.session_state["user_inputs"]
    inc = saved_inputs["finances"]["net_income"]
    sav = saved_inputs["finances"]["monthly_savings"]
    tot_exp = saved_inputs["finances"]["total_expenses"]

    st.success(f"✅ Audit ready ({st.session_state['run_source']})")

    # 1. Pandas DataFrame & deterministic recalculation
    df_budget = pd.DataFrame(audit_result["budget_analysis"])
    if sav > 0 and inc > 0:
        savings_row = pd.DataFrame([{
            "category": "Savings & Reserve",
            "amount": float(sav),
            "share_percent": round((sav / inc) * 100, 1),
            "status": "Optimal",
            "recommendation": "Great job! Allocate this surplus toward investments or your emergency reserve.",
        }])
        df_budget = pd.concat([df_budget, savings_row], ignore_index=True)

    if inc > 0:
        df_budget["share_percent"] = ((df_budget["amount"] / inc) * 100).round(1)

    df_lifestyle = pd.DataFrame(audit_result["lifestyle_insights"])
    df_actions = pd.DataFrame(audit_result["action_plan"])

    # KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Health Score", f"{audit_result['overall_score']} / 100")
    col2.metric("Total Monthly Expenses", f"{tot_exp} €")
    col3.metric("Monthly Savings Surplus", f"{sav} €")

    st.info(f"**Auditor's Executive Summary:** {audit_result['executive_summary']}")

    # Plotly Charts
    st.subheader("📈 Visual Budget Analysis")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_donut = px.pie(
            df_budget,
            values="amount",
            names="category",
            hole=0.45,
            title="Net Monthly Income Allocation (€)",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label")
        fig_donut.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_chart2:
        status_colors = {
            "Optimal": "#2ecc71",
            "Warning": "#f39c12",
            "Critical": "#e74c3c",
        }
        fig_bar = px.bar(
            df_budget.sort_values("amount", ascending=True),
            x="amount",
            y="category",
            orientation="h",
            color="status",
            color_discrete_map=status_colors,
            text="amount",
            title="Expenses & Savings by Efficiency Status",
            labels={"amount": "Amount (€)", "category": "", "status": "Status"},
        )
        fig_bar.update_traces(
            texttemplate="%{text} €",
            textposition="outside",
            cliponaxis=False,
        )
        fig_bar.update_layout(margin=dict(t=40, b=0, l=0, r=65))
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tabs & CSV Export
    tab1, tab2, tab3 = st.tabs([
        "💰 Budget Breakdown",
        "🏃‍♂️ Lifestyle Audit",
        "🎯 Action Plan",
    ])

    with tab1:
        st.dataframe(
            df_budget,
            use_container_width=True,
            hide_index=True,
            column_config={
                "category": "Category",
                "amount": st.column_config.NumberColumn("Amount (€)", format="%.0f €"),
                "share_percent": st.column_config.NumberColumn("Income Share (%)", format="%.1f %%"),
                "status": "Status",
                "recommendation": st.column_config.TextColumn("AI Recommendation", width="large"),
            },
        )
        csv_data = df_budget.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Download Budget Audit (CSV)",
            data=csv_data,
            file_name="ai_lifestyle_budget_audit.csv",
            mime="text/csv",
        )

    with tab2:
        st.dataframe(
            df_lifestyle,
            use_container_width=True,
            hide_index=True,
            column_config={
                "domain": "Domain",
                "current_value": "Current Value",
                "impact": st.column_config.TextColumn("Health & Performance Impact", width="large"),
                "action_item": st.column_config.TextColumn("Actionable Step", width="large"),
            },
        )

    with tab3:
        st.dataframe(
            df_actions,
            use_container_width=True,
            hide_index=True,
            column_config={
                "step": st.column_config.TextColumn("Action Step", width="large"),
                "horizon": "Time Horizon",
                "priority": "Priority",
            },
        )