import streamlit as st
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Invoice Generator", layout="centered")
st.title("📊 Invoice & Tax Calculator")

# Sidebar Settings
st.sidebar.header("Tax & Commission Settings")
parts_gst_pct = st.sidebar.number_input("Parts GST %", value=18.0) / 100
parts_it_pct = st.sidebar.number_input("Parts IT %", value=5.5) / 100
labor_bra_pct = st.sidebar.number_input("Labor BRA %", value=16.0) / 100
labor_it_pct = st.sidebar.number_input("Labor IT %", value=11.0) / 100
comm_pct = st.sidebar.number_input("Total Commission %", value=10.0) / 100

# Main Inputs
st.subheader("Manual Inputs")
col1, col2, col3 = st.columns(3)
with col1:
    part_val = st.number_input("Parts Amount", value=120000)
with col2:
    job_val = st.number_input("Job/Labor Amount", value=30000)
with col3:
    profit_val = st.number_input("Profit Amount", value=15000)

# Logic Calculations (Dynamic Fix)
required_net = part_val + job_val + profit_val
total_exp = part_val + job_val

if total_exp > 0:
    parts_ratio = part_val / total_exp
    job_ratio = job_val / total_exp
    
    # Ye hai asal dynamic math:
    tax_eff = (parts_ratio * (parts_gst_pct + parts_it_pct)) + (job_ratio * (labor_bra_pct + labor_it_pct))
    
    # Formula according to your Back-Processing logic:
    # Gross = Net / ((1 - Taxes) * (1 - Commission))
    gross_bill = required_net / ((1 - tax_eff) * (1 - comm_pct))
    
    gross_parts = gross_bill * parts_ratio
    gross_jobs = gross_bill * job_ratio
    
    tax_on_parts = gross_parts * (parts_gst_pct + parts_it_pct)
    tax_on_jobs = gross_jobs * (labor_bra_pct + labor_it_pct)
    
    cheque_amount = gross_bill - (tax_on_parts + tax_on_jobs)
    commission_amt = cheque_amount * comm_pct
    final_net = cheque_amount - commission_amt
else:
    st.error("Please enter Parts or Job amounts.")
    st.stop()

# Display Results
st.subheader("Results")
res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric("Gross Bill (Bill pe likhein)", f"{gross_bill:,.2f}")
    st.write(f"Tax on Parts: {tax_on_parts:,.2f}")
    st.write(f"Tax on Jobs: {tax_on_jobs:,.2f}")
with res_col2:
    st.metric("Final Net (Apka Hath Mein)", f"{final_net:,.2f}")
    st.write(f"Cheque Amount (Taxes ke baad): {cheque_amount:,.2f}")
    st.write(f"Commission (10%): {commission_amt:,.2f}")

# PDF Function (Minor Latin-1 fix for PKR symbol)
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="INVOICE REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Parts Expense: {part_val:,}", ln=True)
    pdf.cell(200, 10, txt=f"Job/Labor Expense: {job_val:,}", ln=True)
    pdf.cell(200, 10, txt=f"Profit: {profit_val:,}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Gross Bill Amount: {gross_bill:,.2f}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Total Taxes Deducted: {(tax_on_parts + tax_on_jobs):,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Cheque Amount: {cheque_amount:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Commission (10%): {commission_amt:,.2f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Final Net Result: {final_net:,.2f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 Generate PDF Invoice"):
    pdf_bytes = create_pdf()
    st.download_button(label="📥 Download PDF Report", data=pdf_bytes, file_name="invoice_report.pdf", mime="application/pdf")
