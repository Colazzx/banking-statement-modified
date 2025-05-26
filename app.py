# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 15:36:56 2024
Modified on Mon May 25 12:00:00 2025

@author: Caleb and Aul

New feature: crossout detection
"""
import streamlit as st
import pandas as pd
import os
from main import extract_tables_from_pdf
from postprocessing import postprocessing
# from crossout_detection import detect_red_markings_in_image, identify_crossed_out_rows, extract_table_with_visual_analysis
import tempfile

def process_pdf(pdf_path, output_path, page_numbers=None):
    try:
        # Extract tables from the PDF
        tables = extract_tables_from_pdf(pdf_path, page_numbers)

        # Post-process the tables
        combined_df, other_tables = postprocessing(tables)
    

        # Save to Excel
        with pd.ExcelWriter(output_path) as writer:
            combined_df.to_excel(writer, index=False, sheet_name="Combined Data")
            for i, table in enumerate(other_tables):
                sheet_name = f"Other Table {i + 1}"
                table.to_excel(writer, index=False, sheet_name=sheet_name)

        return combined_df, other_tables
    except Exception as e:
        raise e


# Streamlit App
st.title("SME OCR Prototype")

# File uploader
input_pdf = st.file_uploader("Upload PDF here", type="pdf")

# Page selection options
st.markdown("### Page Selection")
all_pages = st.checkbox("Process all pages", value=True)
page_number = None

if not all_pages:
    page_number = st.text_input("Enter specific page numbers (comma-separated, e.g., 1,2,3)", value="1")

if input_pdf is not None:

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the uploaded PDF to the temporary directory
        input_path = os.path.join(temp_dir, "input.pdf")
        with open(input_path, "wb") as f:
            f.write(input_pdf.read())

        # Set the output file path
        output_file_name = "output.xlsx"
        output_path = os.path.join(temp_dir, output_file_name)

        # Process the PDF file
        with st.spinner("Processing the PDF..."):
            try:
                # Convert page input to list, or set to None for all pages
                page_numbers = None if all_pages else [int(page.strip()) for page in page_number.split(",")]
          
                combined_df, other_tables = process_pdf(input_path, output_path, page_numbers)
                st.success("Processing complete!")

                # Display combined DataFrame
                st.subheader("Combined Data")
                st.dataframe(combined_df)

                # Provide a download link for the output file
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="Download Excel File",
                        data=f,
                        file_name=output_file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
