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

# Logic Calculations
required_net = part_val + job_val + profit_val
parts_ratio = part_val / (part_val + job_val) if (part_val + job_val) > 0 else 0
job_ratio = job_val / (part_val + job_val) if (part_val + job_val) > 0 else 0

gross_bill = required_net / 0.702 
gross_parts = gross_bill * parts_ratio
gross_jobs = gross_bill * job_ratio

tax_on_parts = (gross_parts * parts_gst_pct) + (gross_parts * parts_it_pct)
tax_on_jobs = (gross_jobs * labor_bra_pct) + (gross_jobs * labor_it_pct)

cheque_amount = gross_bill - (tax_on_parts + tax_on_jobs)
commission_amt = cheque_amount * comm_pct
final_net = cheque_amount - commission_amt

# Display Results
st.subheader("Results")
res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric("Gross Bill", f"{gross_bill:,.2f}")
    st.write(f"Tax on Parts: {tax_on_parts:,.2f}")
    st.write(f"Tax on Jobs: {tax_on_jobs:,.2f}")
with res_col2:
    st.metric("Final Net Result", f"{final_net:,.2f}")
    st.write(f"Cheque Amount: {cheque_amount:,.2f}")
    st.write(f"Commission: {commission_amt:,.2f}")

# PDF Function
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="INVOICE REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Parts Amount: {part_val}", ln=True)
    pdf.cell(200, 10, txt=f"Job Amount: {job_val}", ln=True)
    pdf.cell(200, 10, txt=f"Profit: {profit_val}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Gross Bill: {gross_bill:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Taxes: {(tax_on_parts + tax_on_jobs):,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Cheque Amount: {cheque_amount:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Final Net: {final_net:,.2f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

if st.button("Generate PDF Invoice"):
    pdf_bytes = create_pdf()
    st.download_button(label="📥 Download PDF", data=pdf_bytes, file_name="invoice.pdf", mime="application/pdf")
