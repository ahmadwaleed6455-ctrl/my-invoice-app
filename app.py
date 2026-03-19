import streamlit as st
from fpdf import FPDF
import datetime

# 1. Page Configuration & Professional Styling
st.set_page_config(page_title="Professional Bill Analyst", page_icon="⚖️", layout="centered")

# TYPO FIXED HERE: changed unsafe_allow_code to unsafe_allow_html
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #1b5e20; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2e7d32; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Professional Bill & Tax Analyst")
st.markdown("Reverse-calculate total bills with proportional profit allocation.")

# 2. Sidebar: Global Tax Settings
with st.sidebar:
    st.header("📋 Tax Configuration")
    st.subheader("Parts Taxes")
    p_gst = st.number_input("GST on Parts (%)", value=18.0) / 100
    p_it = st.number_input("Income Tax on Parts (%)", value=5.5) / 100
    
    st.subheader("Labor/Job Taxes")
    j_bra = st.number_input("BRA Tax (%)", value=16.0) / 100
    j_it = st.number_input("Income Tax on Labor (%)", value=11.0) / 100
    
    st.subheader("Service Fees")
    comm_pct = st.number_input("Total Commission (%)", value=10.0) / 100

# 3. Main Inputs
st.subheader("📥 Manual Entry (Base Figures)")
col1, col2, col3 = st.columns(3)
with col1:
    parts_cost = st.number_input("Actual Parts Cost", value=100000)
with col2:
    labor_cost = st.number_input("Actual Labor Cost", value=50000)
with col3:
    target_profit = st.number_input("Targeted Profit", value=15000)

# 4. Core Proportional Logic
required_net = parts_cost + labor_cost + target_profit
total_exp = parts_cost + labor_cost

if total_exp > 0:
    # Ratios based on actual expenditure
    ratio_parts = parts_cost / total_exp
    ratio_labor = labor_cost / total_exp
    
    # Dynamic Tax Factor
    tax_factor = (ratio_parts * (p_gst + p_it)) + (ratio_labor * (j_bra + j_it))
    
    # Master Gross Bill Formula
    gross_bill = required_net / ((1 - tax_factor) * (1 - comm_pct))
    
    # Adjusted Amounts (Profit hidden inside)
    adj_gross_parts = gross_bill * ratio_parts
    adj_gross_labor = gross_bill * ratio_labor
    
    # Verification
    tax_on_p = adj_gross_parts * (p_gst + p_it)
    tax_on_l = adj_gross_labor * (j_bra + j_it)
    cheque_amount = gross_bill - (tax_on_p + tax_on_l)
    commission_amt = cheque_amount * comm_pct
    final_hand_cash = cheque_amount - commission_amt

    # 5. Dashboard Results
    st.divider()
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("TOTAL GROSS BILL", f"{gross_bill:,.2f} PKR")
    with res_col2:
        st.metric("NET CASH IN HAND", f"{final_hand_cash:,.2f} PKR")

# 6. Detailed Audit Trail (Separated Taxes)
    with st.expander("📝 Detailed Audit Trail"):
        st.table({
            "Description": [
                "Gross Parts Amount (Profit Adjusted)", 
                "Gross Labor Amount (Profit Adjusted)", 
                "Tax on Parts (GST + IT)", 
                "Tax on Labor (BRA + IT)", 
                "Net Cheque Amount (After Taxes)", 
                "Service Commission Fee"
            ],
            "Amount (PKR)": [
                f"{adj_gross_parts:,.2f}", 
                f"{adj_gross_labor:,.2f}", 
                f"{tax_on_p:,.2f}", 
                f"{tax_on_l:,.2f}", 
                f"{cheque_amount:,.2f}", 
                f"{commission_amt:,.2f}"
            ]
        })
  # 7. Professional PDF Function
    def create_audit_pdf():
        pdf = FPDF()
        pdf.add_page()
        
        # Header Styling
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(27, 94, 32)
        pdf.cell(200, 15, txt="DETAILED BILL ANALYSIS REPORT", ln=True, align='C')
        pdf.ln(5)
        
        # Inputs Section
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0)
        pdf.cell(200, 10, txt="1. BASE EXPENDITURE SUMMARY", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(100, 8, txt=f"Actual Parts Cost: {parts_cost:,.2f}")
        pdf.cell(100, 8, txt=f"Actual Labor Cost: {labor_cost:,.2f}", ln=True)
        pdf.cell(100, 8, txt=f"Allocated Profit: {target_profit:,.2f}", ln=True)
        pdf.ln(5)
        
        # Main Result
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 12, txt=f"TOTAL GROSS BILL AMOUNT: {gross_bill:,.2f}", ln=True)
        pdf.ln(5)
        
        # Detailed Back-Verification
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="2. TAX & DEDUCTION BREAKDOWN (VERIFICATION)", ln=True)
        pdf.set_font("Arial", size=11)
        
        # Table-style layout
        pdf.cell(130, 8, txt="Adjusted Gross Parts (Including Profit Share):")
        pdf.cell(50, 8, txt=f"{adj_gross_parts:,.2f}", ln=True, align='R')
        
        pdf.cell(130, 8, txt="Adjusted Gross Labor (Including Profit Share):")
        pdf.cell(50, 8, txt=f"{adj_gross_labor:,.2f}", ln=True, align='R')
        
        pdf.set_text_color(200, 0, 0) # Red for Deductions
        pdf.cell(130, 8, txt=f"Less: Taxes on Parts ({(p_gst+p_it)*100}%):")
        pdf.cell(50, 8, txt=f"- {tax_on_p:,.2f}", ln=True, align='R')
        
        pdf.cell(130, 8, txt=f"Less: Taxes on Labor ({(j_bra+j_it)*100}%):")
        pdf.cell(50, 8, txt=f"- {tax_on_l:,.2f}", ln=True, align='R')
        
        pdf.set_text_color(0)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(130, 10, txt="Net Cheque Amount:")
        pdf.cell(50, 10, txt=f"{cheque_amount:,.2f}", ln=True, align='R')
        
        pdf.set_font("Arial", size=11)
        pdf.cell(130, 8, txt=f"Less: Service Commission ({comm_pct*100}%):")
        pdf.cell(50, 8, txt=f"- {commission_amt:,.2f}", ln=True, align='R')
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(27, 94, 32)
        pdf.cell(130, 12, txt="FINAL NET RECEIVABLE:")
        pdf.cell(50, 12, txt=f"{final_hand_cash:,.2f}", ln=True, align='R')
        
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📥 Download Audit Report PDF"):
        pdf_bytes = create_audit_pdf()
        st.download_button(label="Download Now", data=pdf_bytes, file_name="bill_analysis.pdf", mime="application/pdf")

else:
    st.warning("Enter amounts to generate the analysis.")
