import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Invoice Generator", layout="centered")
st.title("📊 LRH Invoice & Tax Calculator")

# Sidebar for Taxes (Excel ke mutabiq)
st.sidebar.header("Tax Rates")
p_gst = st.sidebar.number_input("Parts GST %", value=18.0) / 100
p_it = st.sidebar.number_input("Parts IT %", value=5.5) / 100
j_bra = st.sidebar.number_input("Labor BRA %", value=16.0) / 100
j_it = st.sidebar.number_input("Labor IT %", value=11.0) / 100
comm_pct = st.sidebar.number_input("Commission %", value=10.0) / 100

# Main Inputs (New Excel values)
st.subheader("Manual Inputs")
col1, col2, col3 = st.columns(3)
with col1:
    part_val = st.number_input("Parts Actual Cost", value=100000)
with col2:
    job_val = st.number_input("Job/Labor Actual Cost", value=50000)
with col3:
    profit_val = st.number_input("Net Profit (Target)", value=15000)

# 1. Required Net
required_net = part_val + job_val + profit_val

# 2. Ratios Calculation
total_exp = part_val + job_val
if total_exp > 0:
    p_ratio = part_val / total_exp
    j_ratio = job_val / total_exp
    
    # 3. Dynamic Tax Factor (Excel logic)
    # Tax_Eff = (Parts_Ratio * 23.5%) + (Job_Ratio * 27%)
    tax_eff = (p_ratio * (p_gst + p_it)) + (j_ratio * (j_bra + j_it))
    
    # 4. Master Formula to match 251,333 result
    # Gross = Required_Net / ((1 - Tax_Eff) * (1 - Comm))
    gross_bill = required_net / ((1 - tax_eff) * (1 - comm_pct))
    
    # 5. Verification Steps (Back Processing)
    gross_parts = gross_bill * p_ratio
    gross_jobs = gross_bill * j_ratio
    
    tax_on_parts = gross_parts * (p_gst + p_it)
    tax_on_jobs = gross_jobs * (j_bra + j_it)
    
    cheque_amt = gross_bill - (tax_on_parts + tax_on_jobs)
    commission_amt = cheque_amt * comm_pct
    final_net = cheque_amt - commission_amt

    # Results Display
    st.divider()
    res1, res2 = st.columns(2)
    with res1:
        st.metric("Total Gross Bill", f"{gross_bill:,.2f}")
        st.write(f"Parts Share in Bill: {gross_parts:,.2f}")
        st.write(f"Jobs Share in Bill: {gross_jobs:,.2f}")
    with res2:
        st.metric("Final Net Result", f"{final_net:,.2f}")
        st.write(f"Cheque Amount: {cheque_amt:,.2f}")
        st.write(f"Commission (10%): {commission_amt:,.2f}")

    # PDF Generator
    def create_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="WARD REPAIR INVOICE REPORT", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(100, 10, txt=f"Actual Expenditure: {total_exp:,}")
        pdf.cell(100, 10, txt=f"Target Profit: {profit_val:,}", ln=True)
        pdf.divider = pdf.line(10, 45, 200, 45)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"GROSS BILL AMOUNT: {gross_bill:,.2f}", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(200, 8, txt=f"Taxes Deducted: {(tax_on_parts+tax_on_jobs):,.2f}", ln=True)
        pdf.cell(200, 8, txt=f"Cheque Amount (Taxes ke baad): {cheque_amt:,.2f}", ln=True)
        pdf.cell(200, 8, txt=f"Commission (10%): {commission_amt:,.2f}", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=f"FINAL NET IN HAND: {final_net:,.2f}", ln=True)
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📥 Generate PDF Report"):
        pdf_bytes = create_pdf()
        st.download_button(label="Click to Download PDF", data=pdf_bytes, file_name="bill_report.pdf", mime="application/pdf")

else:
    st.warning("Please enter valid expense amounts.")
