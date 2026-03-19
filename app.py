import streamlit as st
from fpdf import FPDF
import datetime

# 1. Page Configuration
st.set_page_config(page_title="Professional Bill Analyst", page_icon="⚖️", layout="centered")

# Professional Styling (Green Theme)
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #1b5e20; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2e7d32; border: none; }
    </style>
    """, unsafe_allow_html=True)

# Header with Current Date & Time
now = datetime.datetime.now().strftime("%d-%b-%Y | %I:%M %p")
st.title("⚖️ Professional Bill & Tax Analyst")
st.caption(f"📅 Calculation Date & Time: {now}")

# 2. Sidebar: Global Tax Settings
with st.sidebar:
    st.header("📋 Tax Configuration")
    p_gst = st.number_input("GST on Parts (%)", value=18.0) / 100
    p_it = st.number_input("Income Tax on Parts (%)", value=5.5) / 100
    j_bra = st.number_input("BRA Tax on Labor (%)", value=16.0) / 100
    j_it = st.number_input("Income Tax on Labor (%)", value=11.0) / 100
    comm_pct = st.number_input("Service Commission (%)", value=10.0) / 100

# 3. Main Inputs
st.subheader("📥 Manual Entry")
col1, col2, col3 = st.columns(3)
with col1:
    parts_cost = st.number_input("Actual Parts Cost", value=100000)
with col2:
    labor_cost = st.number_input("Actual Labor Cost", value=50000)
with col3:
    target_profit = st.number_input("Targeted Profit", value=15000)

# 4. Calculation Logic (Proportional)
required_net = parts_cost + labor_cost + target_profit
total_exp = parts_cost + labor_cost

if total_exp > 0:
    ratio_parts = parts_cost / total_exp
    ratio_labor = labor_cost / total_exp
    tax_factor = (ratio_parts * (p_gst + p_it)) + (ratio_labor * (j_bra + j_it))
    
    # Master Formula
    gross_bill = required_net / ((1 - tax_factor) * (1 - comm_pct))
    
    # Adjusted Amounts
    adj_gross_parts = gross_bill * ratio_parts
    adj_gross_labor = gross_bill * ratio_labor
    
    # Separated Taxes
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
        st.metric("NET CASH RECEIVABLE", f"{final_hand_cash:,.2f} PKR")

    # 6. Detailed Audit Table (Separated Taxes)
    with st.expander("📝 Detailed Audit Trail (Verification)"):
        st.table({
            "Description": [
                "Adjusted Parts (with profit)", 
                "Adjusted Labor (with profit)", 
                "Tax on Parts (GST+IT)", 
                "Tax on Labor (BRA+IT)", 
                "Total Deducted Taxes",
                "Cheque Amount (After Taxes)", 
                "Service Commission Fee"
            ],
            "Amount (PKR)": [
                f"{adj_gross_parts:,.2f}", 
                f"{adj_gross_labor:,.2f}", 
                f"{tax_on_p:,.2f}", 
                f"{tax_on_l:,.2f}", 
                f"{(tax_on_p + tax_on_l):,.2f}",
                f"{cheque_amount:,.2f}", 
                f"{commission_amt:,.2f}"
            ]
        })

    # 7. Professional PDF Function
    def create_audit_pdf():
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(27, 94, 32)
        pdf.cell(200, 15, txt="DETAILED BILL ANALYSIS REPORT", ln=True, align='C')
        
        # Timestamp in PDF
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(100)
        pdf.cell(200, 5, txt=f"Report Generated: {now}", ln=True, align='C')
        pdf.ln(10)
        
        # Section 1: Inputs
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0)
        pdf.cell(200, 10, txt="1. EXPENDITURE SUMMARY", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(100, 8, txt=f"Parts Cost: {parts_cost:,.2f}")
        pdf.cell(100, 8, txt=f"Labor Cost: {labor_cost:,.2f}", ln=True)
        pdf.cell(100, 8, txt=f"Profit Margin: {target_profit:,.2f}", ln=True)
        pdf.ln(5)
        
        # Section 2: Main Result
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 12, txt=f"TOTAL GROSS BILL: {gross_bill:,.2f} PKR", ln=True)
        pdf.ln(5)
        
        # Section 3: Detailed Deductions
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="3. TAX & DEDUCTION BREAKDOWN", ln=True)
        pdf.set_font("Arial", size=11)
        
        items = [
            ("Adjusted Parts Share:", adj_gross_parts),
            ("Adjusted Labor Share:", adj_gross_labor),
            (f"Less: Tax on Parts ({(p_gst+p_it)*100}%):", -tax_on_p),
            (f"Less: Tax on Labor ({(j_bra+j_it)*100}%):", -tax_on_l),
            ("Cheque Amount (After Taxes):", cheque_amount),
            (f"Less: Commission ({comm_pct*100}%):", -commission_amt),
        ]
        
        for desc, val in items:
            pdf.cell(130, 8, txt=desc)
            # Use red color for negative values
            if val < 0: pdf.set_text_color(200, 0, 0)
            pdf.cell(50, 8, txt=f"{abs(val):,.2f}", ln=True, align='R')
            pdf.set_text_color(0)
            
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(27, 94, 32)
        pdf.cell(130, 12, txt="FINAL NET RECEIVABLE:")
        pdf.cell(50, 12, txt=f"{final_hand_cash:,.2f} PKR", ln=True, align='R')
        
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📥 Download Final Audit PDF"):
        pdf_bytes = create_audit_pdf()
        st.download_button(label="Click to Download PDF Report", data=pdf_bytes, file_name=f"Report_{datetime.datetime.now().strftime('%d%m%y_%H%M')}.pdf", mime="application/pdf")

else:
    st.warning("Enter expenditure amounts to start.")
