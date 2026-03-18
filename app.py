import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="LRH Invoice Calculator", layout="centered")
st.title("📊 Ward Repair Bill Calculator")

# --- SIDEBAR: Tax & Commission Settings ---
st.sidebar.header("Taxes & Commissions (%)")
# C6, C7, C8, C9, C10, C11 mapping
p_gst = st.sidebar.number_input("Parts GST % (C6)", value=18.0) / 100
p_it = st.sidebar.number_input("Parts IT % (C7)", value=5.5) / 100
j_bra = st.sidebar.number_input("Labor BRA % (C8)", value=16.0) / 100
j_it = st.sidebar.number_input("Labor IT % (C9)", value=11.0) / 100
comm_pct = st.sidebar.number_input("Total Commission % (C10+C11)", value=10.0) / 100

# --- MAIN INPUTS: D2, E2, F2 ---
st.subheader("Manual Expenditure Inputs")
col1, col2, col3 = st.columns(3)
with col1:
    d2_parts = st.number_input("Parts Actual Cost (D2)", value=100000)
with col2:
    e2_jobs = st.number_input("Labor Actual Cost (E2)", value=50000)
with col3:
    f2_profit = st.number_input("Net Profit (F2)", value=15000)

# --- CALCULATION LOGIC: Exactly as per your Excel ---

# C2 = D2 + E2 + F2
c2_net_required = d2_parts + e2_jobs + f2_profit

if c2_net_required > 0:
    # C3 = D2 / C2
    c3_ratio_parts = d2_parts / c2_net_required
    # C4 = E2 / C2
    c4_ratio_jobs = e2_jobs / c2_net_required
    
    # Formula Calculation (C13)
    # tax_factor = C3*(C6+C7) + C4*(C8+C9)
    tax_factor = (c3_ratio_parts * (p_gst + p_it)) + (c4_ratio_jobs * (j_bra + j_it))
    
    # C13 = C2 / ((1 - tax_factor) * (1 - comm_pct))
    c13_gross_bill = c2_net_required / ((1 - tax_factor) * (1 - comm_pct))
    
    # --- BACK VERIFICATION STEPS ---
    c15_gross_parts = c13_gross_bill * c3_ratio_parts
    c16_gross_jobs = c13_gross_bill * c4_ratio_jobs
    
    c17_tax_parts = c15_gross_parts * (p_gst + p_it)
    c18_tax_jobs = c16_gross_jobs * (j_bra + j_it)
    
    c19_cheque = c13_gross_bill - (c17_tax_parts + c18_tax_jobs)
    c20_comm = c19_cheque * comm_pct
    c21_final_result = c19_cheque - c20_comm

    # --- DISPLAY RESULTS ---
    st.divider()
    st.success(f"### TOTAL GROSS BILL (C13): {c13_gross_bill:,.2f} PKR")
    
    with st.expander("🔍 Show Back-Verification (Excel Steps)"):
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.write(f"**Gross Parts (C15):** {c15_gross_parts:,.2f}")
            st.write(f"**Tax on Parts (C17):** {c17_tax_parts:,.2f}")
            st.info(f"**Cheque Amount (C19):** {c19_cheque:,.2f}")
        with v_col2:
            st.write(f"**Gross Jobs (C16):** {c16_gross_jobs:,.2f}")
            st.write(f"**Tax on Jobs (C18):** {c18_tax_jobs:,.2f}")
            st.write(f"**Commission (C20):** {c20_comm:,.2f}")
            st.success(f"**Final Net (C21):** {c21_final_result:,.2f}")

else:
    st.warning("Please enter valid expenditure amounts to calculate.")
