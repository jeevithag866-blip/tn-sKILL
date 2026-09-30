import sys
from pathlib import Path

import requests
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT)
    )


from app.exporters import (
    create_docx,
    create_pdf,
    create_txt,
)


# ---------------------------------------------------------
# Streamlit configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

st.markdown(
    """
<style>

.main-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    margin-top: 0;
}

.preview {
    background: #111827;
    color: #f9fafb;
    padding: 24px;
    border-radius: 14px;
    max-height: 620px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: Georgia, serif;
    line-height: 1.65;
}

.notice {
    padding: 12px 16px;
    border-radius: 10px;
    background: #fff7ed;
    border: 1px solid #fed7aa;
}

</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Logo
# ---------------------------------------------------------

left, center, right = st.columns(
    [1, 2, 1]
)

with center:

    st.markdown(
        """
        <div style="
            text-align: center;
            font-size: 60px;
            margin-bottom: 10px;
        ">
            ⚖️
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">'
    'LegalEase'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Document Generator'
    '</div>',
    unsafe_allow_html=True,
)

st.write("")


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header(
        "Configuration"
    )

    backend_url = st.text_input(
        "FastAPI backend URL",
        value="http://127.0.0.1:8000",
    ).rstrip("/")

    st.caption(
        "Start the FastAPI server before "
        "generating documents."
    )

    st.divider()

    st.markdown(
        "**Supported examples**"
    )

    st.write(
        "Agreement, Contract, NDA, "
        "Lease Agreement, Employment "
        "Offer Letter"
    )

    st.divider()

    st.markdown(
        '<div class="notice">'
        '<b>Important:</b> LegalEase creates '
        'drafting aids, not legal advice. '
        'Review generated documents before use.'
        '</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Input section
# ---------------------------------------------------------

st.subheader(
    "1. Document details"
)


with st.form(
    "document_form"
):

    document_type = st.text_input(
        "Document Type",
        placeholder=(
            "Example: Freelance Work Contract"
        ),
    )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=110,
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=150,
    )

    dates = st.text_input(
        "Effective Date",
        placeholder=(
            "Example: April 10, 2025"
        ),
    )

    generate = st.form_submit_button(
        "⚖️ Generate Document",
        use_container_width=True,
    )


# ---------------------------------------------------------
# Generate document
# ---------------------------------------------------------

if generate:

    if not all(
        [
            document_type.strip(),
            parties.strip(),
            terms.strip(),
            dates.strip(),
        ]
    ):

        st.error(
            "Please complete all four fields."
        )

    else:

        payload = {
            "document_type":
                document_type.strip(),

            "parties":
                parties.strip(),

            "terms":
                terms.strip(),

            "dates":
                dates.strip(),
        }

        try:

            with st.spinner(
                "Generating your legal draft..."
            ):

                response = requests.post(
                    f"{backend_url}/generate",
                    json=payload,
                    timeout=100,
                )

            if response.ok:

                data = response.json()

                st.session_state.document = (
                    data["document"]
                )

                st.session_state.doc_type = (
                    document_type.strip()
                )

                st.session_state.terms = (
                    terms.strip()
                )

                st.session_state.model = (
                    data.get(
                        "model",
                        ""
                    )
                )

                st.session_state.demo_mode = (
                    data.get(
                        "demo_mode",
                        False
                    )
                )

                if data.get("demo_mode"):

                    st.success(
                        "Document generated successfully. "
                        "Demo mode is active because no "
                        "Gemini API key is configured."
                    )

                else:

                    st.success(
                        "Document generated successfully."
                    )

            else:

                try:

                    detail = response.json().get(
                        "detail",
                        response.text,
                    )

                except Exception:

                    detail = response.text

                st.error(
                    f"Backend error "
                    f"({response.status_code}): "
                    f"{detail}"
                )

        except requests.RequestException as exc:

            st.error(
                "Could not connect to FastAPI. "
                f"Make sure the backend is running "
                f"at {backend_url}. "
                f"Details: {exc}"
            )


# ---------------------------------------------------------
# Preview and editing
# ---------------------------------------------------------

if "document" in st.session_state:

    st.divider()

    st.subheader(
        "2. Preview and edit"
    )

    meta = (
        f"Model: "
        f"{st.session_state.get('model', 'unknown')}"
    )

    if st.session_state.get(
        "demo_mode"
    ):

        meta += (
            " | Demo template"
        )

    st.caption(meta)

    st.markdown(
        f'<div class="preview">'
        f'{st.session_state.document}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    edited = st.text_area(
        "Editable Document",
        value=st.session_state.document,
        height=520,
        key="edited_document",
    )

    st.session_state.document = edited


    # -----------------------------------------------------
    # Downloads
    # -----------------------------------------------------

    st.subheader(
        "3. Download"
    )

    col1, col2, col3 = st.columns(
        3
    )

    txt_data = create_txt(
        edited
    )

    docx_data = create_docx(
        edited,
        st.session_state.get(
            "doc_type",
            "Legal Document"
        ),
        st.session_state.get(
            "terms",
            ""
        ),
    )

    pdf_data = create_pdf(
        edited,
        st.session_state.get(
            "doc_type",
            "Legal Document"
        ),
    )


    # Safe filename

    safe_name = "".join(
        c
        if c.isalnum() or c in "-_"
        else "_"
        for c in st.session_state.get(
            "doc_type",
            "document"
        )
    ).strip("_")

    if not safe_name:
        safe_name = "document"


    with col1:

        st.download_button(
            "⬇️ Download TXT",
            data=txt_data,
            file_name=f"{safe_name}.txt",
            mime="text/plain",
            use_container_width=True,
        )


    with col2:

        st.download_button(
            "⬇️ Download DOCX",
            data=docx_data,
            file_name=f"{safe_name}.docx",
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            use_container_width=True,
        )


    with col3:

        st.download_button(
            "⬇️ Download PDF",
            data=pdf_data,
            file_name=f"{safe_name}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )