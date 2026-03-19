import streamlit as st
from fpdf import FPDF

# 1. Page Config & UI
st.set_page_config(page_title="Pro LRH Calculator", layout="centered")
st.title("📊 LRH Pro-Adjusted Bill Calculator")
st.markdown("Profit ko proportionaly Parts aur Job mein adjust karne wala system.")

# 2. Sidebar Settings (C6 to C11)
st.sidebar.header("⚙️ Tax & Commission Settings")
p_gst = st.sidebar.number_input("Parts GST % (C6)", value=18.0) / 100
p_it = st.sidebar.number_input("Parts IT % (C7)", value=5.5) / 100
j_bra = st.sidebar.number_input("Labor BRA % (C8)", value=16.0) / 100
j_it = st.sidebar.number_input("Labor IT % (C9)", value=11.0) / 100
comm_pct = st.sidebar.number_input("Total Commission % (C10+C11)", value=10.0) / 100

# 3. Manual Entry (D2, E2, F2)
st.subheader("📥 Expenditure & Profit Entry")
col1, col2, col3 = st.columns(3)
with col1:
    d2_parts = st.number_input("Parts Actual Cost (D2)", value=100000)
with col2:
    e2_jobs = st.number_input("Labor Actual Cost (E2)", value=50000)
with col3:
    f2_profit = st.number_input("Net Profit (F2)", value=15000)

# 4. Professional Accountant Logic
c2_net = d2_parts + e2_jobs + f2_profit
total_exp = d2_parts + e2_jobs

if total_exp > 0:
    # C3 and C4 based on expenditure only (to ensure 100% split of Gross Bill)
    c3_ratio = d2_parts / total_exp
    c4_ratio = e2_jobs / total_exp
    
    # Master Formula (C13)
    tax_factor = (c3_ratio * (p_gst + p_it)) + (c4_ratio * (j_bra + j_it))
    gross_bill = c2_net / ((1 - tax_factor) * (1 - comm_pct))
    
    # Adjusted Shares (Profit is now hidden inside these two)
    c15_adj_parts = gross_bill * c3_ratio
    c16_adj_jobs = gross_bill * c4_ratio
    
    # Back Verification
    tax_p = c15_adj_parts * (p_gst + p_it)
    tax_j = c16_adj_jobs * (j_bra + j_it)
    cheque = gross_bill - (tax_p + tax_j)
    final_net = cheque * (1 - comm_pct)

    # 5. Display Results
    st.divider()
    st.success(f"### TOTAL GROSS BILL: {gross_bill:,.2f} PKR")
    
    # Showing the split that adds up to 100% of Gross Bill
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.write(f"**Adjusted Gross Parts (C15):** {c15_adj_parts:,.2f}")
        st.write(f"**Tax on Parts:** {tax_p:,.2f}")
    with res_col2:
        st.write(f"**Adjusted Gross Job (C16):** {c16_adj_jobs:,.2f}")
        st.write(f"**Tax on Job:** {tax_j:,.2f}")
    
    st.info(f"**Sum of Splits (C15 + C16):** {(c15_adj_parts + c16_adj_jobs):,.2f} ✅")
    st.markdown(f"**Final Net in Hand (Verification):** {final_net:,.2f}")

    # 6. PDF Generation Function
    def create_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="REPAIR BILL REPORT (LRH)", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Actual Expenditure (Parts + Job): {(d2_parts + e2_jobs):,.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Allocated Profit: {f2_profit:,.2f}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=f"TOTAL GROSS BILL: {gross_bill:,.2f}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", size=11)
        pdf.cell(200, 8, txt=f"Line Item 1: Parts (Adjusted): {c15_adj_parts:,.2f}", ln=True)
        pdf.cell(200, 8, txt=f"Line Item 2: Labor (Adjusted): {c16_adj_jobs:,.2f}", ln=True)
        pdf.cell(200, 8, txt=f"Total Taxes to be Deducted: {(tax_p + tax_j):,.2f}", ln=True)
        pdf.cell(200, 8, txt=f"Estimated Cheque Amount: {cheque:,.2f}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"FINAL NET AFTER COMMISSION: {final_net:,.2f}", ln=True)
        
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📄 Generate PDF Summary"):
        pdf_bytes = create_pdf()
        st.download_button(label="📥 Download PDF", data=pdf_bytes, file_name="bill_summary.pdf", mime="application/pdf")

else:
    st.warning("Please enter Expenditure amounts to start calculation.")
