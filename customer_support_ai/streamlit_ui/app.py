import os
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

import streamlit_ui.utils as utils

load_dotenv()

st.set_page_config(
    page_title="Support Ticket Classifier",
    page_icon="🎫",
    layout="centered"
)

def main():
    st.title("🎫 Support Ticket Classifier")

    st.markdown("""
    Upload a CSV file with customer support tickets and get them automatically classified 
    using **LangGraph + Instructor + Pydantic**.

    **Required columns:** `date`, `from_email`, `first_name`, `message`
    """)

    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv",
        help="Upload a CSV with the required columns"
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            is_valid, error_message = utils.validate_csv(df)

            if not is_valid:
                st.error(f"❌ {error_message}")
                return

            st.success(f"✅ Loaded {len(df)} tickets successfully!")

            with st.expander("👀 Preview Data", expanded=False):
                st.dataframe(df.head(), use_container_width=True)

            if st.button("🚀 Classify Tickets", type="primary", use_container_width=True):
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    st.error("❌ Please set OPENAI_API_KEY in your .env file")
                    return

                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(progress):
                    progress_bar.progress(progress)
                    status_text.text(f"Processing... {progress:.0%}")

                try:
                    df_classified = utils.classify_tickets_streamlit(df, update_progress)
                    st.session_state.classified_df = df_classified

                    progress_bar.progress(1.0)
                    status_text.text("✅ Classification complete!")

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    return

        except Exception as e:
            st.error(f"❌ Error reading CSV: {str(e)}")

    if 'classified_df' in st.session_state:
        df_classified = st.session_state.classified_df

        st.markdown("---")
        st.subheader("📊 Results")

        stats_df = utils.get_classification_stats(df_classified)

        st.markdown("**Category Breakdown**")
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

        st.markdown("**Distribution**")
        fig = px.pie(
            stats_df, 
            values='Count', 
            names='Category',
            title=""
        )
        fig.update_layout(showlegend=True, height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Classified Tickets**")

        display_df = df_classified[['first_name', 'message', 'category']].copy()
        display_df['message'] = display_df['message'].str[:80] + '...'

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        csv_data = utils.prepare_download_data(df_classified)
        st.download_button(
            label="📥 Download Full Results",
            data=csv_data,
            file_name="classified_tickets.csv",
            mime="text/csv",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
