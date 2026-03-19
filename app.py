import streamlit as st
from fpdf import FPDF
import datetime

# 1. Page Configuration & UI Beautification
st.set_page_config(page_title="Professional Bill Calculator", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2e7d32; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_code=True)

st.title("⚖️ Professional Bill & Tax Analyst")
st.markdown("Reverse-calculate your total bill based on required net profit and expenses.")

# 2. Sidebar: Global Tax & Commission Settings
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
    st.info("These settings apply globally to the calculation below.")

# 3. Main Inputs: Expenditure & Profit
st.subheader("📥 Manual Entry (Base Figures)")
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        parts_cost = st.number_input("Parts Expenditure", value=100000, help="Actual cost of parts")
    with col2:
        labor_cost = st.number_input("Labor/Service Cost", value=50000, help="Actual cost of labor/jobs")
    with col3:
        target_profit = st.number_input("Required Profit", value=15000, help="Your targeted net profit")

# 4. Core Logic: Proportional Allocation
required_net = parts_cost + labor_cost + target_profit
total_exp = parts_cost + labor_cost

if total_exp > 0:
    # Ratios based on expenditure
    ratio_parts = parts_cost / total_exp
    ratio_labor = labor_cost / total_exp
    
    # Effective Tax Factor
    tax_factor = (ratio_parts * (p_gst + p_it)) + (ratio_labor * (j_bra + j_it))
    
    # Gross Bill Calculation
    gross_bill = required_net / ((1 - tax_factor) * (1 - comm_pct))
    
    # Adjusted Shares (Profit merged proportionally)
    adj_gross_parts = gross_bill * ratio_parts
    adj_gross_labor = gross_bill * ratio_labor
    
    # Back-Verification
    tax_on_p = adj_gross_parts * (p_gst + p_it)
    tax_on_l = adj_gross_labor * (j_bra + j_it)
    cheque_amount = gross_bill - (tax_on_p + tax_on_l)
    commission_amt = cheque_amount * comm_pct
    final_hand_cash = cheque_amount - commission_amt

    # 5. Visual Results Display
    st.divider()
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("TOTAL BILL VALUE (GROSS)", f"{gross_bill:,.2f} PKR")
    with res_col2:
        st.metric("NET RECEIVABLE (FINAL)", f"{final_hand_cash:,.2f} PKR")

    # 6. Detailed Audit Breakdown
    with st.expander("📝 View Detailed Audit Breakdown"):
        st.write("Profit has been adjusted proportionally into Parts and Labor shares.")
        st.table({
            "Description": ["Adjusted Parts Share", "Adjusted Labor Share", "Tax Deducted (Parts)", "Tax Deducted (Labor)", "Service Commission"],
            "Amount (PKR)": [f"{adj_gross_parts:,.2f}", f"{adj_gross_labor:,.2f}", f"{tax_on_p:,.2f}", f"{tax_on_l:,.2f}", f"{commission_amt:,.2f}"]
        })

    # 7. PDF Report Generator
    def create_professional_pdf():
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(46, 125, 50) # Greenish
        pdf.cell(200, 15, txt="BILL VERIFICATION REPORT", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(100)
        pdf.cell(200, 5, txt=f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
        pdf.ln(10)
        
        # Section 1: Inputs
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0)
        pdf.cell(200, 10, txt=" 1. INPUT SUMMARY", ln=True, fill=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(100, 10, txt=f"Actual Parts Cost: {parts_cost:,.2f}")
        pdf.cell(100, 10, txt=f"Actual Labor Cost: {labor_cost:,.2f}", ln=True)
        pdf.cell(100, 10, txt=f"Target Profit: {target_profit:,.2f}")
        pdf.cell(100, 10, txt=f"Total Required Net: {required_net:,.2f}", ln=True)
        pdf.ln(5)
        
        # Section 2: Bill Value
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=" 2. CALCULATED BILL VALUE", ln=True, fill=True)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(25, 118, 210) # Blue
        pdf.cell(200, 15, txt=f"TOTAL GROSS BILL: {gross_bill:,.2f} PKR", ln=True)
        
        # Section 3: Detailed Deductions
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0)
        pdf.cell(200, 10, txt=" 3. DEDUCTION & BACK-VERIFICATION", ln=True, fill=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(130, 8, txt="Adjusted Parts Share (Profit included):")
        pdf.cell(50, 8, txt=f"{adj_gross_parts:,.2f}", ln=True, align='R')
        pdf.cell(130, 8, txt="Adjusted Labor Share (Profit included):")
        pdf.cell(50, 8, txt=f"{adj_gross_labor:,.2f}", ln=True, align='R')
        pdf.cell(130, 8, txt=f"Taxes on Parts ({(p_gst+p_it)*100}%):")
        pdf.cell(50, 8, txt=f"- {tax_on_p:,.2f}", ln=True, align='R')
        pdf.cell(130, 8, txt=f"Taxes on Labor ({(j_bra+j_it)*100}%):")
        pdf.cell(50, 8, txt=f"- {tax_on_l:,.2f}", ln=True, align='R')
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(130, 10, txt="Cheque Amount (After Taxes):")
        pdf.cell(50, 10, txt=f"{cheque_amount:,.2f}", ln=True, align='R')
        pdf.set_font("Arial", size=11)
        pdf.cell(130, 8, txt=f"Service Commission ({comm_pct*100}%):")
        pdf.cell(50, 8, txt=f"- {commission_amt:,.2f}", ln=True, align='R')
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(46, 125, 50)
        pdf.cell(130, 12, txt="FINAL NET IN HAND:")
        pdf.cell(50, 12, txt=f"{final_hand_cash:,.2f} PKR", ln=True, align='R')
        
        return pdf.output(dest='S').encode('latin-1')

    # Download Button
    st.divider()
    if st.button("📥 Generate & Download Professional PDF"):
        pdf_out = create_professional_pdf()
        st.download_button(
            label="Download Final Invoice Report",
            data=pdf_out,
            file_name=f"Tax_Analysis_{int(gross_bill)}.pdf",
            mime="application/pdf"
        )
else:
    st.warning("Please enter expenses to view the calculation.")
