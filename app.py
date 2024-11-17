import streamlit as st
import pandas as pd
from services.google_sheets import connect_google_sheets, update_google_sheet
from services.search_api import SearchService
from models.llm_processing import LLMProcessor
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize services
processor = LLMProcessor()
search_service = SearchService()


def main():
    st.set_page_config(page_title="AI Data Extraction Dashboard", layout="wide")

    # Sidebar
    with st.sidebar:
        st.title("Data Extraction Tool")
        st.markdown("### Data Source")
        data_source = st.radio("Choose data source:", ["Upload CSV", "Google Sheets"])
        st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.markdown("---")

    # Footer
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>Built with ❤️ by Arya Sharma</div>
        """, unsafe_allow_html=True
    )

    # Main UI with tabs
    st.title("AI Agent Data Extraction Dashboard")
    tabs = st.tabs(["LLM Processing", "Raw Search Results"])

    data = None
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
        if uploaded_file:
            data = pd.read_csv(uploaded_file)
            st.success("CSV uploaded successfully.")
    elif data_source == "Google Sheets":
        sheet_url = st.text_input("Enter Google Sheets URL")
        if sheet_url:
            data = connect_google_sheets(sheet_url)
            st.success("Google Sheet connected successfully.")

    if data is not None:
        st.subheader("Data Preview")
        st.dataframe(data.head())

        # Entity column selection and prompt configuration
        entity_column = st.selectbox("Select the column with entities", data.columns)
        prompt_template = st.text_area("Prompt Template", "Get me the email address of {company}")

        if st.button("Start Processing"):
            with st.spinner("Processing..."):
                results = []
                entities = data[entity_column].tolist()

                # Perform search and LLM processing
                search_results_df = search_service.search_entities(entities, prompt_template)
                for entity in entities:
                    entity_results = search_results_df[search_results_df['entity'] == entity].to_dict('records')
                    llm_result = processor.process_search_results(entity, entity_results, prompt_template)
                    results.append({
                        'entity': entity,
                        'extracted_info': llm_result.get('extracted_info', 'Not found'),
                        'confidence': llm_result.get('confidence', 'LOW'),
                        'source': llm_result.get('source', 'None')
                    })

                # Tabular display for results
                processed_results_df = pd.DataFrame(results)

                with tabs[0]:  # LLM Processing Results
                    st.subheader("LLM Processed Results")
                    st.dataframe(processed_results_df)
                    processed_csv = processed_results_df.to_csv(index=False)
                    st.download_button("Download Processed Results", processed_csv, "processed_results.csv", "text/csv")

                with tabs[1]:  # Raw Search Results
                    st.subheader("Raw Search Results")
                    st.dataframe(search_results_df)
                    raw_csv = search_results_df.to_csv(index=False)
                    st.download_button("Download Raw Search Results", raw_csv, "raw_search_results.csv", "text/csv")


if __name__ == "__main__":
    main()