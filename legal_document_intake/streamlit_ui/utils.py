"""
Utility functions for the Streamlit frontend.
Handles API communication and data formatting.
"""

import requests
import streamlit as st
from typing import Dict, Any, Optional
from pathlib import Path
import json


class APIClient:
    """Client for communicating with the FastAPI backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the FastAPI backend
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def health_check(self) -> Optional[Dict[str, Any]]:
        """Check API health status."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"API health check failed: {e}")
            return None
    
    def upload_document(self, file, document_type: str) -> Optional[Dict[str, Any]]:
        """
        Upload document to the backend.
        
        Args:
            file: Uploaded file object
            document_type: Type of document (employment_contract or payslip)
            
        Returns:
            Upload response or None if failed
        """
        try:
            # Prepare files for upload
            files = {
                'file': (file.name, file.getvalue(), file.type)
            }
            
            # Prepare data
            data = {
                'document_type': document_type
            }
            
            # Remove default Content-Type header for file upload
            headers = {k: v for k, v in self.session.headers.items() if k != 'Content-Type'}
            
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                data=data,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            st.error(f"Upload failed: {e}")
            return None
    
    def get_processing_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get processing status for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Status information or None if failed
        """
        try:
            response = self.session.get(f"{self.base_url}/status/{job_id}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Status check failed: {e}")
            return None
    
    def get_processing_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get processing results for a completed job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Processing results or None if failed
        """
        try:
            response = self.session.get(f"{self.base_url}/result/{job_id}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to get results: {e}")
            return None
    
    def download_pdf(self, job_id: str) -> Optional[bytes]:
        """
        Download generated PDF.
        
        Args:
            job_id: Job identifier
            
        Returns:
            PDF data as bytes or None if failed
        """
        try:
            response = self.session.get(f"{self.base_url}/download/{job_id}", timeout=30)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            st.error(f"PDF download failed: {e}")
            return None
    
    def list_jobs(self) -> Optional[list]:
        """
        List all jobs in the system.
        
        Returns:
            List of jobs or None if failed
        """
        try:
            response = self.session.get(f"{self.base_url}/jobs", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to list jobs: {e}")
            return None
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job and its associated files.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.delete(f"{self.base_url}/jobs/{job_id}", timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to delete job: {e}")
            return False


def format_currency(amount: float) -> str:
    """
    Format currency amount for display.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    if amount is None:
        return "N/A"
    
    try:
        return f"€{float(amount):,.2f}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(percentage: float) -> str:
    """
    Format percentage for display.
    
    Args:
        percentage: Percentage to format
        
    Returns:
        Formatted percentage string
    """
    if percentage is None:
        return "N/A"
    
    try:
        return f"{float(percentage):.1f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_date(date_value) -> str:
    """
    Format date for display.
    
    Args:
        date_value: Date value to format
        
    Returns:
        Formatted date string
    """
    if date_value is None:
        return "N/A"
    
    try:
        if isinstance(date_value, str):
            return date_value
        else:
            return str(date_value)
    except:
        return "N/A"


def validate_file_upload(file) -> bool:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        True if valid, False otherwise
    """
    if not file:
        return False
    
    # Check file size (10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        st.error(f"File too large. Maximum size: {max_size / (1024*1024):.1f}MB")
        return False
    
    # Check file extension
    allowed_extensions = {'.pdf', '.docx', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    file_extension = Path(file.name).suffix.lower()
    
    if file_extension not in allowed_extensions:
        st.error(f"Unsupported file type: {file_extension}")
        return False
    
    return True


def display_job_summary(jobs: list) -> None:
    """
    Display summary of jobs.
    
    Args:
        jobs: List of job information
    """
    if not jobs:
        st.info("No jobs found")
        return
    
    # Create DataFrame for display
    import pandas as pd
    
    job_data = []
    for job in jobs:
        job_data.append({
            'Job ID': job.get('job_id', 'N/A')[:8] + '...',
            'Status': job.get('status', 'N/A'),
            'Current Node': job.get('current_node', 'N/A'),
            'Has Error': 'Yes' if job.get('error_message') else 'No'
        })
    
    df = pd.DataFrame(job_data)
    st.dataframe(df, use_container_width=True)


def create_status_indicator(status: str) -> str:
    """
    Create a status indicator with appropriate emoji.
    
    Args:
        status: Status string
        
    Returns:
        Status with emoji
    """
    status_map = {
        'pending': '⏳ Pending',
        'processing': '🔄 Processing',
        'completed': '✅ Completed',
        'failed': '❌ Failed',
        'unknown': '❓ Unknown'
    }
    
    return status_map.get(status, f'❓ {status}')


def export_data_to_csv(data: Dict[str, Any], filename: str) -> bytes:
    """
    Export data to CSV format.
    
    Args:
        data: Data to export
        filename: Filename for the CSV
        
    Returns:
        CSV data as bytes
    """
    import pandas as pd
    from io import StringIO
    
    # Flatten the data for CSV
    flattened_data = []
    for key, value in data.items():
        flattened_data.append({
            'Field': key,
            'Value': str(value) if value is not None else 'N/A'
        })
    
    df = pd.DataFrame(flattened_data)
    
    # Convert to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return csv_buffer.getvalue().encode('utf-8')


def display_error_message(error: str, details: str = None) -> None:
    """
    Display formatted error message.
    
    Args:
        error: Error message
        details: Additional error details
    """
    st.error(f"❌ {error}")
    
    if details:
        with st.expander("Error Details"):
            st.code(details)


def display_success_message(message: str, details: str = None) -> None:
    """
    Display formatted success message.
    
    Args:
        message: Success message
        details: Additional details
    """
    st.success(f"✅ {message}")
    
    if details:
        with st.expander("Details"):
            st.info(details)


def create_download_filename(document_type: str, job_id: str, extension: str) -> str:
    """
    Create a standardized filename for downloads.
    
    Args:
        document_type: Type of document
        job_id: Job identifier
        extension: File extension
        
    Returns:
        Formatted filename
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{document_type}_{job_id[:8]}_{timestamp}.{extension.lstrip('.')}"