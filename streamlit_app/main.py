"""
BizFlow - Streamlit Frontend
Modern dark-mode SaaS UI for business request intake automation.
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

# ─────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="BizFlow — AI Business Intake",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FLASK_URL = "http://localhost:5000"

SAMPLE_REQUEST = """Subject: Refund request for failed payment

Hello Team,

I am Priya Sharma from Acme Corp. We made a payment of INR 42,000 on 10-May-2026 for invoice INV-9081, but the transaction failed and the amount was still deducted from our bank account.

Please process the refund as soon as possible.

Customer ID: CUST-7781
Payment Reference: PAY-44291
Contact Email: priya@acmecorp.com

Regards,
Priya"""

# ─────────────────────────────────────────
#  CUSTOM CSS — Dark SaaS aesthetic
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #080C14 !important;
    color: #E2E8F0 !important;
    font-family: 'Syne', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stDecoration"] { display: none; }
.stDeployButton { display: none; }

/* ── Main container ── */
.main .block-container {
    padding: 2rem 3rem 4rem 3rem;
    max-width: 1280px;
}

/* ── Header ── */
.bizflow-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 0.5rem;
}
.bizflow-logo {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, #00D4FF, #7C3AED);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
    box-shadow: 0 0 24px rgba(0,212,255,0.3);
}
.bizflow-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    background: linear-gradient(135deg, #00D4FF 0%, #7C3AED 60%, #F472B6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    margin: 0;
}
.bizflow-subtitle {
    color: #64748B;
    font-size: 0.9rem;
    font-weight: 400;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Divider ── */
.biz-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #1E293B 20%, #334155 50%, #1E293B 80%, transparent);
    margin: 1.5rem 0;
}

/* ── Cards ── */
.biz-card {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.biz-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00D4FF, #7C3AED);
    opacity: 0.6;
}
.biz-card-title {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #64748B;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.biz-card-value {
    font-size: 1.5rem;
    font-weight: 800;
    color: #F1F5F9;
}
.biz-card-sub {
    font-size: 0.8rem;
    color: #475569;
    margin-top: 0.25rem;
}

/* ── Status Badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.05em;
}
.badge-green  { background: rgba(16,185,129,0.12); color: #10B981; border: 1px solid rgba(16,185,129,0.25); }
.badge-yellow { background: rgba(245,158,11,0.12); color: #F59E0B; border: 1px solid rgba(245,158,11,0.25); }
.badge-red    { background: rgba(239,68,68,0.12);  color: #EF4444; border: 1px solid rgba(239,68,68,0.25); }
.badge-blue   { background: rgba(0,212,255,0.12);  color: #00D4FF; border: 1px solid rgba(0,212,255,0.25); }
.badge-purple { background: rgba(124,58,237,0.12); color: #A78BFA; border: 1px solid rgba(124,58,237,0.25); }

/* ── Section headers ── */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #CBD5E1;
    margin: 1.5rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-header span.icon {
    width: 32px; height: 32px;
    background: #1E293B;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

/* ── Field grid ── */
.field-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
    margin: 0.5rem 0;
}
.field-item {
    background: #0A1628;
    border: 1px solid #1E293B;
    border-radius: 10px;
    padding: 0.75rem 1rem;
}
.field-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569;
    margin-bottom: 4px;
}
.field-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: #E2E8F0;
    word-break: break-all;
}
.field-value.null-val { color: #334155; font-style: italic; }

/* ── Validation items ── */
.val-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 8px;
    margin-bottom: 6px;
    font-size: 0.85rem;
}
.val-item.error   { background: rgba(239,68,68,0.08); border-left: 3px solid #EF4444; color: #FCA5A5; }
.val-item.warning { background: rgba(245,158,11,0.08); border-left: 3px solid #F59E0B; color: #FCD34D; }
.val-item.success { background: rgba(16,185,129,0.08); border-left: 3px solid #10B981; color: #6EE7B7; }

/* ── Risk bar ── */
.risk-bar-bg {
    background: #1E293B;
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
    margin: 0.5rem 0;
}
.risk-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.8s ease;
}

/* ── Trace timeline ── */
.trace-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 0;
    border-bottom: 1px solid #0F172A;
}
.trace-icon {
    width: 36px; height: 36px;
    background: #1E293B;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}
.trace-label { font-size: 0.9rem; color: #CBD5E1; font-weight: 600; flex: 1; }
.trace-time  { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #475569; }

/* ── Recommendation card ── */
.rec-card {
    background: linear-gradient(135deg, rgba(0,212,255,0.05), rgba(124,58,237,0.08));
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-top: 0.5rem;
}
.rec-action {
    font-size: 1.3rem;
    font-weight: 800;
    color: #00D4FF;
    margin-bottom: 0.5rem;
}
.rec-reason { color: #94A3B8; font-size: 0.9rem; line-height: 1.6; }

/* ── Streamlit textarea override ── */
.stTextArea textarea {
    background: #0A1628 !important;
    border: 1px solid #1E293B !important;
    border-radius: 12px !important;
    color: #E2E8F0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
    resize: vertical;
}
.stTextArea textarea:focus {
    border-color: #00D4FF !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.15) !important;
}

/* ── Streamlit button overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #00D4FF, #7C3AED) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: #1E293B !important;
    color: #00D4FF !important;
    border: 1px solid rgba(0,212,255,0.25) !important;
    border-radius: 10px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── Metric card row ── */
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
    flex-wrap: wrap;
}
.metric-card {
    flex: 1;
    min-width: 140px;
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
}
.metric-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #475569; margin-bottom: 6px; }
.metric-value { font-size: 1.4rem; font-weight: 800; color: #F1F5F9; }
.metric-sub   { font-size: 0.75rem; color: #64748B; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

def fmt_timestamp(iso_str: str) -> str:
    """Format ISO timestamp to readable string."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S.%f")[:-3]
    except Exception:
        return iso_str


def priority_color(priority: str) -> str:
    mapping = {"High": "red", "Medium": "yellow", "Low": "green"}
    return mapping.get(priority, "blue")


def validation_status_color(status: str) -> str:
    mapping = {"complete": "green", "warning": "yellow", "incomplete": "red"}
    return mapping.get(status, "blue")


def confidence_color(conf: str) -> str:
    mapping = {"High": "green", "Medium": "yellow", "Low": "red"}
    return mapping.get(conf, "blue")


def risk_bar_color(score: int) -> str:
    if score >= 60:
        return "#EF4444"
    elif score >= 35:
        return "#F59E0B"
    return "#10B981"


def call_backend(request_text: str) -> dict:
    """Call the Flask backend API."""
    resp = requests.post(
        f"{FLASK_URL}/process-request",
        json={"request_text": request_text},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def render_field_grid(extracted: dict):
    """Render extracted fields in a nice grid."""
    display_fields = {
        "customer_name": "Customer Name",
        "company_name": "Company",
        "amount": "Amount",
        "invoice_id": "Invoice ID",
        "payment_reference": "Payment Ref",
        "customer_id": "Customer ID",
        "email": "Email",
        "dates": "Dates",
        "issue_summary": "Issue Summary",
    }
    items_html = ""
    for key, label in display_fields.items():
        val = extracted.get(key)
        if isinstance(val, list):
            display = ", ".join(val) if val else None
        else:
            display = val

        if display and str(display).lower() not in ("null", "none", ""):
            val_class = "field-value"
            display_str = str(display)
        else:
            val_class = "field-value null-val"
            display_str = "—"

        # Issue summary gets full width
        width = "grid-column: 1 / -1;" if key == "issue_summary" else ""
        items_html += f"""
        <div class="field-item" style="{width}">
            <div class="field-label">{label}</div>
            <div class="{val_class}">{display_str}</div>
        </div>"""

    st.markdown(f'<div class="field-grid">{items_html}</div>', unsafe_allow_html=True)


def render_validation(validation: dict):
    """Render validation results."""
    status = validation["status"]
    status_color = validation_status_color(status)
    status_icon = {"complete": "✓", "warning": "⚠", "incomplete": "✗"}.get(status, "?")

    st.markdown(
        f'<span class="badge badge-{status_color}">{status_icon} {status.upper()}</span>',
        unsafe_allow_html=True,
    )

    # Errors
    for err in validation.get("errors", []):
        st.markdown(f'<div class="val-item error">✗ {err}</div>', unsafe_allow_html=True)

    # Missing fields
    for field in validation.get("missing_fields", []):
        st.markdown(
            f'<div class="val-item error">Missing required field: <strong>{field.replace("_", " ").title()}</strong></div>',
            unsafe_allow_html=True,
        )

    # Warnings
    for warn in validation.get("warnings", []):
        st.markdown(f'<div class="val-item warning">⚠ {warn}</div>', unsafe_allow_html=True)

    if status == "complete":
        st.markdown(
            '<div class="val-item success">✓ All required fields present. Ready to process.</div>',
            unsafe_allow_html=True,
        )


def render_risk(risk: dict):
    """Render risk assessment."""
    score = risk["risk_score"]
    priority = risk["priority"]
    bar_color = risk_bar_color(score)
    p_color = priority_color(priority)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Priority Level</div>
            <div class="metric-value"><span class="badge badge-{p_color}">{priority}</span></div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Risk Score</div>
            <div class="metric-value" style="color:{bar_color}">{score}<span style="font-size:0.8rem;color:#475569"> / 100</span></div>
            <div class="risk-bar-bg">
                <div class="risk-bar-fill" style="width:{score}%;background:{bar_color}"></div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Trigger reasons
    if risk.get("trigger_reasons"):
        st.markdown('<div class="biz-card-title">⚡ Trigger Reasons</div>', unsafe_allow_html=True)
        for reason in risk["trigger_reasons"]:
            st.markdown(
                f'<div class="val-item warning">→ {reason}</div>',
                unsafe_allow_html=True,
            )


def render_trace(trace: list):
    """Render the workflow trace timeline."""
    html = ""
    for step in trace:
        html += f"""
        <div class="trace-item">
            <div class="trace-icon">{step['icon']}</div>
            <div class="trace-label">{step['label']}</div>
            <div class="trace-time">{fmt_timestamp(step['timestamp'])}</div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="bizflow-header">
    <div class="bizflow-logo">⚡</div>
    <div>
        <div class="bizflow-title">BizFlow</div>
        <div class="bizflow-subtitle">AI-Powered Business Request Intake</div>
    </div>
</div>
<div class="biz-divider"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  INPUT SECTION
# ─────────────────────────────────────────
col_input, col_results = st.columns([1, 1.4], gap="large")

with col_input:
    st.markdown('<div class="section-header"><span class="icon">📝</span> Request Input</div>', unsafe_allow_html=True)

    request_text = st.text_area(
        label="",
        placeholder="Paste your business request here...",
        height=280,
        key="request_input",
        label_visibility="collapsed",
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        run_clicked = st.button("⚡ Process Request", use_container_width=True)
    with col_btn2:
        sample_clicked = st.button("📋 Load Sample", use_container_width=True)

    if sample_clicked:
        st.session_state["request_input"] = SAMPLE_REQUEST
        st.rerun()

    # Status panel
    if "last_result" in st.session_state:
        res = st.session_state["last_result"]
        cls = res.get("classification", {})
        risk = res.get("risk_assessment", {})
        st.markdown('<div class="biz-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header"><span class="icon">📊</span> Quick Summary</div>', unsafe_allow_html=True)

        p_color = priority_color(risk.get("priority", "Low"))
        c_color = confidence_color(cls.get("confidence", "Low"))
        v_color = validation_status_color(res.get("validation", {}).get("status", "incomplete"))

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-label">Category</div>
                <div style="font-size:0.9rem;font-weight:700;color:#CBD5E1;margin-top:4px">{cls.get('category','—')}</div>
                <span class="badge badge-{c_color}" style="margin-top:6px">{cls.get('confidence','—')}</span>
            </div>
            <div class="metric-card">
                <div class="metric-label">Priority</div>
                <span class="badge badge-{p_color}" style="margin-top:4px;font-size:1rem">{risk.get('priority','—')}</span>
                <div class="metric-sub">Score: {risk.get('risk_score',0)}/100</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Validation</div>
                <span class="badge badge-{v_color}" style="margin-top:4px">{res.get('validation',{}).get('status','—').upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Export
    if "last_result" in st.session_state:
        st.markdown('<div class="biz-divider"></div>', unsafe_allow_html=True)
        json_bytes = json.dumps(st.session_state["last_result"], indent=2, default=str).encode("utf-8")
        st.download_button(
            label="⬇ Export JSON",
            data=json_bytes,
            file_name=f"bizflow_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )

# ─────────────────────────────────────────
#  PROCESS & SHOW RESULTS
# ─────────────────────────────────────────
with col_results:
    if run_clicked:
        if not request_text or not request_text.strip():
            st.error("⚠️ Please enter a request before processing.")
        else:
            with st.spinner("Processing through AI workflow..."):
                progress_placeholder = st.empty()
                steps = [
                    "📨 Receiving request...",
                    "🏷️ Classifying with Gemini...",
                    "🔍 Extracting information...",
                    "✅ Validating fields...",
                    "⚠️ Assessing risk...",
                    "💡 Generating recommendation...",
                ]
                for step in steps:
                    progress_placeholder.markdown(
                        f'<div class="val-item warning">{step}</div>',
                        unsafe_allow_html=True,
                    )
                    time.sleep(0.3)
                progress_placeholder.empty()

                try:
                    result = call_backend(request_text)
                    st.session_state["last_result"] = result
                    st.rerun()
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to BizFlow backend. Is the Flask server running on port 5000?")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        cls = result.get("classification", {})
        extracted = result.get("extracted_data", {})
        validation = result.get("validation", {})
        risk = result.get("risk_assessment", {})
        recommendation = result.get("recommendation", {})
        trace = result.get("workflow_trace", [])

        # ── Classification ──
        st.markdown('<div class="section-header"><span class="icon">🏷️</span> Classification</div>', unsafe_allow_html=True)
        c_color = confidence_color(cls.get("confidence", "Low"))
        st.markdown(f"""
        <div class="biz-card">
            <div class="biz-card-title">REQUEST CATEGORY</div>
            <div class="biz-card-value">{cls.get('category', '—')}</div>
            <div style="margin-top:10px">
                <span class="badge badge-{c_color}">Confidence: {cls.get('confidence','—')}</span>
            </div>
            <div style="margin-top:12px;color:#64748B;font-size:0.85rem;line-height:1.5">
                {cls.get('reasoning', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Extracted Info ──
        st.markdown('<div class="section-header"><span class="icon">🔍</span> Extracted Information</div>', unsafe_allow_html=True)
        st.markdown('<div class="biz-card">', unsafe_allow_html=True)
        render_field_grid(extracted)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Validation ──
        st.markdown('<div class="section-header"><span class="icon">✅</span> Validation Results</div>', unsafe_allow_html=True)
        st.markdown('<div class="biz-card">', unsafe_allow_html=True)
        render_validation(validation)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Risk ──
        st.markdown('<div class="section-header"><span class="icon">⚠️</span> Risk Assessment</div>', unsafe_allow_html=True)
        st.markdown('<div class="biz-card">', unsafe_allow_html=True)
        render_risk(risk)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Recommendation ──
        st.markdown('<div class="section-header"><span class="icon">💡</span> Recommended Action</div>', unsafe_allow_html=True)
        auto_badge = (
            '<span class="badge badge-green">✓ Auto-Processable</span>'
            if recommendation.get("auto_processable")
            else '<span class="badge badge-yellow">⚠ Manual Review Required</span>'
        )
        st.markdown(f"""
        <div class="rec-card">
            <div class="rec-action">→ {recommendation.get('action', '—')}</div>
            <div style="margin:8px 0">{auto_badge}</div>
            <div class="rec-reason">{recommendation.get('reason', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Workflow Trace ──
        st.markdown('<div class="section-header"><span class="icon">🔄</span> Workflow Trace</div>', unsafe_allow_html=True)
        st.markdown('<div class="biz-card">', unsafe_allow_html=True)
        render_trace(trace)
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Empty state
        st.markdown("""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 5rem 2rem;
            color: #334155;
            text-align: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #475569; margin-bottom: 0.5rem;">
                Ready to Process
            </div>
            <div style="font-size: 0.9rem; color: #334155; max-width: 300px; line-height: 1.6;">
                Enter a business request on the left and click <strong style="color:#64748B">Process Request</strong> to run the full AI intake workflow.
            </div>
        </div>
        """, unsafe_allow_html=True)
