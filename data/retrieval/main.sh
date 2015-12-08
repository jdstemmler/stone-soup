#!/bin/bash

echo "Executing NYTimesCooking Metadata Retrieval"
python ${CAPSTONE_DIR}/data-retrieval/get_nytimes_metadata.py 19000101

echo "Extracting NYTimes Metadata to File"
python ${CAPSTONE_DIR}/data-retrieval/extract_nytimes_urls.py

echo "Executing NYTimesCooking Document Retrieval"
python ${CAPSTONE_DIR}/data-retrieval/get_nytimes_recipes.py