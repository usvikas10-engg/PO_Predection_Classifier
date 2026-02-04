import streamlit as st
import json
from datetime import datetime
from classifier import classify_po

st.set_page_config(page_title="PO Category Classifier", layout="wide")

st.markdown(
    """
    <style>
      :root {
        --accent: #60a5fa;
        --accent-2: #34d399;
        --ink: #e2e8f0;
        --muted: #94a3b8;
        --panel: #0f172a;
        --bg: #0b1220;
        --border: #1e293b;
      }
      .block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; }
      [data-testid="stAppViewContainer"] { background: var(--bg); }
      [data-testid="stHeader"] { background: transparent; }

      .hero-wrap {
        background:
          radial-gradient(600px 120px at 12% -25%,
rgba(96,165,250,0.35), transparent 70%),
          linear-gradient(135deg, #0f172a 0%, #0b1220 60%, #111827 100%);
        border: 1px solid var(--border);
        padding: 20px 22px 22px 22px;
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        animation: fade-in 500ms ease-out;
      }
      .hero-wrap h1 { margin: 0; color: var(--ink); font-size: 30px;
letter-spacing: -0.3px; }
      .hero-wrap p { margin: 6px 0 0 0; color: #cbd5f5; }
      .pill {
        display: inline-block; padding: 4px 10px; margin-right: 6px;
        border-radius: 999px; font-size: 12px;
        background: rgba(96,165,250,0.16); color: #dbeafe;
      }
      .muted { color: var(--muted); font-size: 12px; }

      /* Card styling for Streamlit containers */
      div[data-testid="stVerticalBlockBorderWrapper"] >
div[data-testid="stVerticalBlock"] {
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px 18px;
        background: var(--panel);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
        animation: float-in 420ms ease-out;
      }

      /* Inputs */
      textarea, input {
        border-radius: 12px !important;
        background: #0b1220 !important;
        color: #e2e8f0 !important;
        border: 1px solid #1f2937 !important;
      }

      /* Buttons */
      div.stButton > button {
        border-radius: 12px;
        border: 1px solid #1f2937;
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        color: #e2e8f0;
        font-weight: 600;
        padding: 0.65rem 1rem;
        transition: transform 140ms ease, box-shadow 140ms ease,
border-color 140ms ease;
      }
      div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 24px rgba(0, 0, 0, 0.35);
        border-color: rgba(96,165,250,0.5);
      }
      div.stButton > button[kind="primary"] {
        background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
        border-color: rgba(96,165,250,0.6);
      }

      /* Sidebar */
      section[data-testid="stSidebar"] { background: #0f172a; }
      section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        border-radius: 14px;
      }

      /* Animations */
      @keyframes fade-in {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes float-in {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-wrap">
      <span class="pill">L1</span><span class="pill">L2</span><span
class="pill">L3</span>
      <h1>PO Category Classifier</h1>
      <p>Classify purchase orders into a consistent taxonomy with a
clean JSON output.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "po_description" not in st.session_state:
    st.session_state.po_description = ""
if "supplier" not in st.session_state:
    st.session_state.supplier = ""
if "history" not in st.session_state:
    st.session_state.history = []

examples = [
    {
        "label": "Office supplies - printer paper",
        "po_description": "Purchase 10 cases of A4 printer paper,80gsm, white.",
        "supplier": "Staples",
    },
    {
        "label": "IT hardware - laptops",
        "po_description": "Procure 15 Dell Latitude laptops with 16GBRAM and 512GB SSD.",
        "supplier": "Dell",
    },
    {
        "label": "Facilities - cleaning services",
        "po_description": "Monthly janitorial services for HQ,includes nightly cleaning and waste removal.",
        "supplier": "CleanCo",
    },
]

with st.sidebar:
    st.subheader("Quick Start")
    st.caption("Load a sample and run the classifier in seconds.")
    example_labels = ["Select an example..."] + [e["label"] for e in examples]
    selected_example = st.selectbox("Examples", example_labels, index=0)
    if st.button("Use example"):
        if selected_example != "Select an example...":
            chosen = next(e for e in examples if e["label"] == selected_example)
            st.session_state.po_description = chosen["po_description"]
            st.session_state.supplier = chosen["supplier"]
    st.markdown("---")
    st.subheader("Tips")
    st.markdown("- Include product/service type and quantity.")
    st.markdown("- Add supplier name when known.")
    st.markdown("- Use plain language for best results.")

left, right = st.columns([2, 1])
with left:
    with st.container(border=True):
        st.subheader("Input")
        po_description = st.text_area(
            "PO Description",
            height=160,
            key="po_description",
            placeholder="e.g., Procure 15 Dell Latitude laptops with16GB RAM and 512GB SSD.",
        )
        supplier = st.text_input(
            "Supplier (optional)",
            key="supplier",
            placeholder="e.g., Dell",
        )
        st.markdown( "<span class='muted'>We only store history in your currentsession.</span>",
            unsafe_allow_html=True,
        )

with right:
    with st.container(border=True):
        st.subheader("Actions")
        st.caption("One click to classify and download.")
        classify_clicked = st.button("Classify",
use_container_width=True, type="primary")
        st.markdown("<span class='muted'>Results appear below with a downloadable JSON file.</span>",
            unsafe_allow_html=True,
        )

def _extract_key(data, keys):
    for k in data.keys():
        if k.lower() in keys:
            return data[k]
    return None

st.markdown("---")
if classify_clicked:
    if not po_description.strip():
        st.warning("Please enter a PO Description to classify.")
    elif len(po_description.strip()) < 5:
        st.warning("PO Description is too short. Please add a bit more detail.")
    else:
        with st.spinner("Classifying..."):
            try:
                result = classify_po(po_description, supplier)
            except Exception as exc:
                st.error("Classification failed. Please check your APIkey and try again.")
                st.text(str(exc))
                st.stop()

        parsed = None
        try:
            parsed = json.loads(result)
        except Exception:
            st.error("Model response was not valid JSON. Showing rawoutput below.")
            st.text(result)
            st.stop()

        if isinstance(parsed, dict):
            l1 = _extract_key(parsed, {"l1", "level1", "category_l1"})
            l2 = _extract_key(parsed, {"l2", "level2", "category_l2"})
            l3 = _extract_key(parsed, {"l3", "level3", "category_l3"})
            confidence = _extract_key(parsed, {"confidence", "score",
"probability"})

            st.subheader("Summary")
            cols = st.columns(4)
            cols[0].metric("L1", l1 if l1 else "—")
            cols[1].metric("L2", l2 if l2 else "—")
            cols[2].metric("L3", l3 if l3 else "—")
            cols[3].metric("Confidence", confidence if confidence is
not None else "—")

            st.subheader("Raw JSON")
            st.json(parsed)
        else:
            st.subheader("Raw Output")
            st.text(result)

        st.download_button(
            label="Download result as JSON",
            data=json.dumps(parsed, indent=2),
            file_name="po_classification.json",
            mime="application/json",
        )

        st.session_state.history.insert(
            0,
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "po_description": po_description.strip(),
                "supplier": supplier.strip() if supplier else "",
                "result": parsed,
            },
        )

if st.session_state.history:
    st.subheader("History")
    if st.button("Clear history"):
        st.session_state.history = []
    else:
        for item in st.session_state.history[:10]:
            with st.expander(f"{item['timestamp']} —{item['po_description'][:60]}"):
                st.text(f"Supplier: {item['supplier'] or 'Not provided'}")
                st.json(item["result"])
