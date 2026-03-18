import streamlit as st
from fpdf import FPDF

# ... (Sidebar settings wahi rahein ge) ...

# Main Inputs
st.subheader("Manual Inputs")
col1, col2, col3 = st.columns(3)
with col1:
    d2_parts = st.number_input("Parts Actual Cost (D2)", value=100000)
with col2:
    e2_jobs = st.number_input("Job/Labor Actual Cost (E2)", value=50000)
with col3:
    f2_profit = st.number_input("Profit (F2)", value=15000)

# --- EXACT EXCEL LOGIC ---
# C2 = D2 + E2 + F2
required_net_c2 = d2_parts + e2_jobs + f2_profit

if required_net_c2 > 0:
    # C3 = D2 / C2 (Parts Ratio relative to Net)
    # C4 = E2 / C2 (Job Ratio relative to Net)
    c3_ratio_parts = d2_parts / required_net_c2
    c4_ratio_jobs = e2_jobs / required_net_c2
    
    # C13 = C2 / ((1 - (C3*(C6+C7) + C4*(C8+C9))) * (1 - (C10+C11)))
    # Note: C6, C7, C8, C9, C10, C11 are tax/comm percentages
    tax_factor = (c3_ratio_parts * (p_gst + p_it)) + (c4_ratio_jobs * (j_bra + j_it))
    comm_factor = (comm_pct) # Ye C10 + C11 hai
    
    gross_bill_c13 = required_net_c2 / ((1 - tax_factor) * (1 - comm_factor))
    
    # Verification Steps (As per your Excel rows)
    c15_gross_parts = gross_bill_c13 * c3_ratio_parts
    c16_gross_jobs = gross_bill_c13 * c4_ratio_jobs
    
    c17_tax_parts = c15_gross_parts * (p_gst + p_it)
    c18_tax_jobs = c16_gross_jobs * (j_bra + j_it)
    
    c19_cheque = gross_bill_c13 - (c17_tax_parts + c18_tax_jobs)
    c20_comm = c19_cheque * comm_factor
    c21_final_net = c19_cheque - c20_comm

    # --- RESULTS DISPLAY ---
    st.divider()
    st.metric("TOTAL GROSS BILL (C13)", f"{gross_bill_c13:,.2f}")
    
    st.subheader("Back Verification (Exactly like Excel)")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.write(f"**Gross Parts (C15):** {c15_gross_parts:,.2f}")
        st.write(f"**Tax on Parts (C17):** {c17_tax_parts:,.2f}")
        st.info(f"**Cheque Amount (C19):** {c19_cheque:,.2f}")
    with v_col2:
        st.write(f"**Gross Jobs (C16):** {c16_gross_jobs:,.2f}")
        st.write(f"**Tax on Jobs (C18):** {c18_tax_jobs:,.2f}")
        st.success(f"**Final Result (C21):** {c21_final_net:,.2f}")
