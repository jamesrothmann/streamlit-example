import streamlit as st
from sentence_transformers import SentenceTransformer, util
import json
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from os.path import exists
from IPython.display import HTML, display
import numpy as np
import math

model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1')


# Section 1: Upload epub or json file
st.header('Upload epub or json file')
file = st.file_uploader('Upload your file here')

if file is not None:
    # Check file type and process accordingly
    ext = os.path.splitext(file)[1]
    if ext == '.epub':
        # Process epub file
        pass
    elif ext == '.json':
        # Process json file
        with open(file) as f:
            data = json.load(f)
        # Print first 10 entries from the file
        st.write('Here is a preview of your json file:')
        st.json(data[:10])

# Section 2: Search form
st.header('Search Form')
search_term = st.text_input('Enter your search term')
if st.button('Ask my book'):
    # Search book based on the provided search term
    pass
