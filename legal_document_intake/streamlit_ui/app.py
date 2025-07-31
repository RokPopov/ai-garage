import streamlit as st
import time
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

from utils import APIClient, format_currency, format_percentage, validate_file_upload

load_dotenv()

st.set_page_config(
    page_title="Legal Document Intake",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #2E86AB 0%, #A23B72 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
}

.status-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #2E86AB;
    margin: 1rem 0;
    color: #333333;
}

.success-card {
    background: #d4edda;
    border-left-color: #28a745;
    color: #155724;
}

.error-card {
    background: #f8d7da;
    border-left-color: #dc3545;
    color: #721c24;
}

.processing-card {
    background: #fff3cd;
    border-left-color: #ffc107;
    color: #856404;
}

.data-section {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 1rem 0;
}

.metric-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    margin: 0.5rem;
}

.progress-container {
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

API_BASE_URL = f"http://localhost:{os.getenv('API_PORT', '8000')}"
api_client = APIClient(API_BASE_URL)

if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'document_type' not in st.session_state:
    st.session_state.document_type = None

def main():
    """Main Streamlit application."""
    
    st.markdown("""
    <div class="main-header">
        <h1>📋 Legal Document Intake System</h1>
        <p>Upload employment contracts and payslips for automated data extraction</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📊 System Status")
        
        health_status = api_client.health_check()
        if health_status:
            st.success("✅ System Ready")
            
            jobs_by_status = health_status.get('jobs_by_status', {})
            active_jobs = health_status.get('active_jobs', 0)
            total_jobs = health_status.get('total_jobs', 0)
            
            if total_jobs > 0:
                st.metric("Active Jobs", active_jobs)
                st.metric("Total Jobs", total_jobs)
                
                with st.expander("Job Details"):
                    for status, count in jobs_by_status.items():
                        if count > 0:
                            status_emoji = {
                                'pending': '⏳',
                                'processing': '🔄', 
                                'completed': '✅',
                                'failed': '❌'
                            }.get(status, '❓')
                            st.write(f"{status_emoji} {status.title()}: {count}")
            else:
                st.info("No jobs processed yet")
        else:
            st.error("❌ System Unavailable")
            st.warning("Please ensure the processing service is running")
        
        st.divider()
        
        st.header("💼 Doc Management")
        if st.button("🔄 Refresh Status"):
            st.rerun()
        
        if st.button("🗑️ Clear Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Document")
        
        uploaded_file = st.file_uploader(
            "Choose a document file",
            type=['pdf', 'docx', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'],
            help="Supported formats: PDF, DOCX, PNG, JPG, JPEG, TIFF, BMP"
        )
        
        document_type = st.selectbox(
            "Document Type",
            ["employment_contract", "payslip"],
            format_func=lambda x: "Employment Contract" if x == "employment_contract" else "Payslip"
        )
        
        if uploaded_file is not None:
            if validate_file_upload(uploaded_file):
                if st.button("🚀 Process Document", type="primary"):
                    process_document(uploaded_file, document_type)
            else:
                st.error("Invalid file format or size")
    
    with col2:
        st.header("📈 Processing Status")
        
        if st.session_state.job_id:
            display_processing_status()
        else:
            st.info("Upload a document to see processing status")
    
    if st.session_state.processing_complete and st.session_state.extracted_data:
        st.header("📋 Extracted Data")
        display_extracted_data()
    
    if st.session_state.processing_complete and st.session_state.job_id:
        st.header("📥 Download Results")
        display_download_section()

def process_document(uploaded_file, document_type):
    """Process uploaded document."""
    try:
        with st.spinner("Uploading document..."):
            response = api_client.upload_document(uploaded_file, document_type)
            
            if response:
                st.session_state.job_id = response['job_id']
                st.session_state.document_type = document_type
                st.session_state.processing_complete = False
                st.session_state.extracted_data = None
                
                st.success(f"✅ Document uploaded successfully! Process ID: {response['job_id']}")
                st.rerun()
            else:
                st.error("❌ Failed to upload document")
    
    except Exception as e:
        st.error(f"❌ Upload error: {str(e)}")

def display_processing_status():
    """Display current processing status."""
    if not st.session_state.job_id:
        return
    
    try:
        status = api_client.get_processing_status(st.session_state.job_id)
        
        if status:
            current_status = status.get('status', 'unknown')
            current_node = status.get('current_node')
            
            if current_status == 'completed':
                st.markdown(f"""
                <div class="status-card success-card">
                    <h4>✅ Processing Complete</h4>
                    <p>Process ID: {st.session_state.job_id}</p>
                    <p>Status: {current_status}</p>
                </div>
                """, unsafe_allow_html=True)
                
                get_processing_results()
                
            elif current_status == 'failed':
                error_msg = status.get('error_message', 'Unknown error')
                st.markdown(f"""
                <div class="status-card error-card">
                    <h4>❌ Processing Failed</h4>
                    <p>Process ID: {st.session_state.job_id}</p>
                    <p>Error: {error_msg}</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif current_status == 'processing':
                current_step_display = current_node if current_node else 'Starting...'
                st.markdown(f"""
                <div class="status-card processing-card">
                    <h4>⏳ Processing...</h4>
                    <p>Process ID: {st.session_state.job_id}</p>
                    <p>Current step: {current_step_display}</p>
                </div>
                """, unsafe_allow_html=True)
                
                time.sleep(2)
                st.rerun()
                
            elif current_status == 'pending':
                st.markdown(f"""
                <div class="status-card processing-card">
                    <h4>⏳ Pending...</h4>
                    <p>Process ID: {st.session_state.job_id}</p>
                    <p>Your document is queued for processing</p>
                </div>
                """, unsafe_allow_html=True)
                
                time.sleep(2)
                st.rerun()
            
            else:
                # Handle any other status
                current_step_display = current_node if current_node else 'N/A'
                st.markdown(f"""
                <div class="status-card">
                    <h4>📋 Status: {current_status}</h4>
                    <p>Process ID: {st.session_state.job_id}</p>
                    <p>Current step: {current_step_display}</p>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.error("❌ Could not retrieve processing status")
    
    except Exception as e:
        st.error(f"❌ Status error: {str(e)}")

def get_processing_results():
    """Get and store processing results."""
    if st.session_state.processing_complete:
        return
    
    try:
        results = api_client.get_processing_results(st.session_state.job_id)
        
        if results and results.get('success'):
            st.session_state.extracted_data = results.get('extracted_data')
            st.session_state.processing_complete = True
        
    except Exception as e:
        st.error(f"❌ Error getting results: {str(e)}")

def display_extracted_data():
    """Display extracted data in an editable format."""
    if not st.session_state.extracted_data:
        return
    
    data = st.session_state.extracted_data
    document_type = st.session_state.document_type
    
    if document_type == "employment_contract":
        display_employment_contract_data(data)
    elif document_type == "payslip":
        display_payslip_data(data)

def display_employment_contract_data(data: Dict[str, Any]):
    """Display employment contract data."""
    st.subheader("👤 Employee Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Full Name", value=data.get('employee_full_name', ''), key="emp_name")
        st.text_input("Job Title", value=data.get('job_title', ''), key="job_title")
        st.text_input("Start Date", value=str(data.get('employment_start_date', '')), key="start_date")
        st.text_input("Contract Type", value=data.get('contract_type', ''), key="contract_type")
    
    with col2:
        st.text_area("Address", value=data.get('employee_address', ''), key="address")
        st.text_input("Birth Date", value=str(data.get('employee_date_of_birth', '')), key="birth_date")
        st.text_input("Weekly Hours", value=str(data.get('weekly_working_hours', '')), key="weekly_hours")
        st.text_input("Probation Period", value=data.get('probation_period', ''), key="probation")
    
    st.subheader("💰 Compensation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Monthly Salary", format_currency(data.get('gross_monthly_salary_eur', 0)))
        st.metric("Holiday Allowance %", format_percentage(data.get('holiday_allowance_percentage', 0)))
    
    with col2:
        st.metric("Pension %", format_percentage(data.get('pension_contribution_percentage', 0)))
    
    st.subheader("🏢 Company Information")
    st.text_input("Employer Name", value=data.get('employer_name', ''), key="employer")
    st.text_area("Benefits", value=data.get('other_benefits', ''), key="benefits")

def display_payslip_data(data: Dict[str, Any]):
    """Display payslip data."""
    st.subheader("👤 Employee Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Employee Name", value=data.get('employee_name', ''), key="emp_name")
        st.text_input("Employee Number", value=data.get('employee_number', ''), key="emp_number")
        st.text_input("IBAN", value=data.get('iban', ''), key="iban")
        st.text_input("Contract Type", value=data.get('contract_type', ''), key="contract_type")
    
    with col2:
        st.text_input("Birth Date", value=str(data.get('date_of_birth', '')), key="birth_date")
        st.text_input("Hire Date", value=str(data.get('hire_date', '')), key="hire_date")
        st.text_input("Weekly Hours", value=str(data.get('weekly_hours', '')), key="weekly_hours")
        st.text_input("Part-time %", value=str(data.get('parttime_percentage', '')), key="parttime_percentage")
    
    st.subheader("💰 Current Period")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Gross Salary", format_currency(data.get('gross_salary_period', 0)))
        st.metric("Holiday Allowance", format_currency(data.get('holiday_allowance', 0)))
    
    with col2:
        st.metric("Tax Withheld", format_currency(data.get('wage_tax_withheld', 0)))
        st.metric("ZVW Contribution", format_currency(data.get('zvw_employer_contribution', 0)))
    
    with col3:
        st.metric("Net Salary", format_currency(data.get('net_salary_paid', 0)))
        st.metric("Work Days", str(data.get('work_days_this_period', 0)))
    
    st.subheader("📊 Year-to-Date")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Fiscal Wage YTD", format_currency(data.get('fiscal_wage_to_date', 0)))
        st.metric("Social Security YTD", format_currency(data.get('social_security_wage_to_date', 0)))
    
    with col2:
        st.metric("Annual Gross", format_currency(data.get('annual_gross_salary', 0)))
        st.metric("Tax Credit YTD", format_currency(data.get('cumulative_tax_credit', 0)))

def display_download_section():
    """Display download options."""
    try:
        pdf_data = api_client.download_pdf(st.session_state.job_id)
        
        if pdf_data:
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_data,
                file_name=f"{st.session_state.document_type}_{st.session_state.job_id}.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.error("❌ Failed to download PDF")
    
    except Exception as e:
        st.error(f"❌ Download error: {str(e)}")

if __name__ == "__main__":
    main()