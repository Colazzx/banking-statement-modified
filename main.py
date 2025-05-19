# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 15:52:16 2024
Modified on Mon May 25

@author: Caleb and Audric

New feature: crossout detection
"""
import subprocess
import os
import camelot as cam

def install_ghostscript():
    """Install Ghostscript if not already installed"""
    proc = subprocess.Popen('apt-get install -y ghostscript', shell=True, stdin=None, stdout=open(os.devnull,'wb'), stderr=subprocess.STDOUT, executable="/bin/bash")
    proc.communicate()

def extract_tables_from_pdf(pdf_path, page_numbers=None):
    """
    Extract tables from a PDF file.

    Args:
    - pdf_path: Path to the PDF file.
    - page_numbers: Comma-separated string of page numbers to extract tables from (optional).

    Returns:
    - List of DataFrames containing the extracted tables.
    """
    # Set pages to 'all' if no page_numbers are provided
    if page_numbers is None:
        page_numbers = "all"

    # Extract tables using Camelot
    try:
        tables = cam.read_pdf(pdf_path, pages=page_numbers, flavor='stream')
        return tables
    except Exception as e:
        raise e

    # Return the extracted tables
    return tables