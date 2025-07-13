import pandas as pd
from typing import Tuple
import sys
from pathlib import Path
import os

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from app.graph import classify_ticket

def validate_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    """Validate uploaded CSV has required columns."""
    required_columns = ['date', 'from_email', 'first_name', 'message']
    
    if df.empty:
        return False, "CSV file is empty"
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    if df['message'].isna().any():
        return False, "Some message fields are empty"
    
    return True, ""

def classify_tickets_streamlit(df: pd.DataFrame, progress_callback=None) -> pd.DataFrame:
    """Classify tickets using LangGraph workflow."""
    tickets = df['message'].tolist()
    total_tickets = len(tickets)
    
    categories = []
    for i, ticket in enumerate(tickets):
        try:
            result = classify_ticket(ticket)
            categories.append(result)
        except Exception as e:
            categories.append("Classification Error")
        
        if progress_callback:
            progress = (i + 1) / total_tickets
            progress_callback(progress)
    
    df_classified = df.copy()
    df_classified['category'] = categories
    
    return df_classified

def get_classification_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Get classification statistics."""
    counts = df['category'].value_counts()
    total = counts.sum()
    
    stats_df = pd.DataFrame({
        'Category': counts.index,
        'Count': counts.values,
        'Percentage': (counts.values / total * 100).round(1)
    })
    
    return stats_df

def prepare_download_data(df: pd.DataFrame) -> bytes:
    """Prepare classified data for download."""
    return df.to_csv(index=False).encode('utf-8')
