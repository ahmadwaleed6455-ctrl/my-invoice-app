import streamlit as st
from fpdf import FPDF
import base64

st.set_page_config(page_title="Invoice & PDF Generator", layout="centered")
st.title("📊 Ward Repair Bill & PDF Generator")

# --- SIDEBAR: Tax & Commission Settings ---
st.sidebar.header("Taxes & Commissions (%)")
p_gst = st.sidebar.number_input("Parts GST % (C6)", value=18.0) / 100
p_it = st.sidebar.number_input("Parts IT % (C7)", value=5.5) / 100
j_bra = st.sidebar.number_input("Labor BRA % (C8)", value=16.0) / 100
j_it = st.sidebar.number_input("Labor IT % (C9)", value=11.0) / 100
comm_pct = st.sidebar.number_input("Total Commission % (C10+C11)", value=10.0) / 100

# --- MAIN INPUTS ---
st.subheader("Manual Expenditure Inputs")
col1, col2, col3 = st.columns(3)
with col1:
    d2_parts = st.number_input("Parts Actual Cost (D2)", value=100000)
with col2:
    e2_jobs = st.number_input("Labor Actual Cost (E2)", value=50000)
with col3:
    f2_profit = st.number_input("Net Profit (F2)", value=15000)

# --- CALCULATION LOGIC (Exact Excel Formulas) ---
c2_net_required = d2_parts + e2_jobs + f2_profit

if c2_net_required > 0:
    c3_ratio_parts = d2_parts / c2_net_required
    c4_ratio_jobs = e2_jobs / c2_net_required
    
    # Master Formula (C13)
    tax_factor = (c3_ratio_parts * (p_gst + p_it)) + (c4_ratio_jobs * (j_bra + j_it))
    c13_gross_bill = c2_net_required / ((1 - tax_factor) * (1 - comm_pct))
    
    # Verification Steps
    c15_gross_parts = c13_gross_bill * c3_ratio_parts
    c16_gross_jobs = c13_gross_bill * c4_ratio_jobs
    c17_tax_parts = c15_gross_parts * (p_gst + p_it)
    c18_tax_jobs = c16_gross_jobs * (j_bra + j_it)
    c19_cheque = c13_gross_bill - (c17_tax_parts + c18_tax_jobs)
    c20_comm = c19_cheque * comm_pct
    c21_final_result = c19_cheque - c20_comm

    # --- UI DISPLAY ---
    st.divider()
    st.success(f"### TOTAL GROSS BILL (C13): {c13_gross_bill:,.2f} PKR")
    
    with st.expander("🔍 Show Detailed Breakdown (Excel Steps)"):
        v1, v2 = st.columns(2)
        with v1:
            st.write(f"**Gross Parts (C15):** {c15_gross_parts:,.2f}")
            st.write(f"**Tax on Parts (C17):** {c17_tax_parts:,.2f}")
            st.info(f"**Cheque (C19):** {c19_cheque:,.2f}")
        with v2:
            st.write(f"**Gross Jobs (C16):** {c16_gross_jobs:,.2f}")
            st.write(f"**Tax on Jobs (C18):** {c18_tax_jobs:,.2f}")
            st.success(f"**Final Net (C21):** {c21_final_result:,.2f}")

    # --- PDF GENERATION FUNCTION ---
    def generate_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="WARD REPAIR - INVOICE REPORT", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Parts Expenditure (D2): {d2_parts:,.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Labor Expenditure (E2): {e2_jobs:,.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Target Profit (F2): {f2_profit:,.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Required Net (C2): {c2_net_required:,.2f}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"TOTAL GROSS BILL (C13): {c13_gross_bill:,.2f}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", size=11)
        pdf.cell(200, 8, txt=f"Gross Parts (C15): {c15_gross_parts:,.2f}", ln=True)
        pdf.cell(200, 8, txt=f"Gross Jobs (C16): {c16_gross_jobs:,.2f}", ln=True)
        pdf.cell(200, 8, txt=f"Total Taxes (C17+C18): {(c17_tax_parts+c18_tax_jobs):,.2f}", ln=True)
        pdf.cell(200, 8, txt=f"Cheque Amount (C19): {c19_cheque:,.2f}", ln=True)
        pdf.cell(200, 8, txt=f"Commission (C20): {c20_comm:,.2f}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=f"FINAL NET RESULT (C21): {c21_final_result:,.2f}", ln=True)
        
        return pdf.output(dest='S').encode('latin-1')

    # PDF Download Button
    st.divider()
    if st.button("📄 Generate & Download PDF"):
        try:
            pdf_data = generate_pdf()
            st.download_button(
                label="📥 Click here to Download PDF",
                data=pdf_data,
                file_name=f"Invoice_{c13_gross_bill:.0f}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF Error: {e}")

else:
    st.warning("Please enter valid amounts to calculate.")
