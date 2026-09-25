"""
process_files.py — Part 3: many files, one after another, with a running total.

The same job as process_file.py, but the app now remembers what it has already
done: how many files have been processed, how many packages that came to, and a
one-line summary of each file — and it keeps remembering across uploads.

That is the hard part, and it is hard for a specific reason: every interaction
reruns this whole script from the top, so an ordinary variable like
`files_processed = 0` is reset to zero on every rerun. Anything that has to
survive a rerun lives in `st.session_state` instead, and is initialised only
once — the first time the script runs.

The other trap is the uploader itself. Once a file has been chosen it stays
chosen on every rerun, so an app that processes "whenever there is a file" would
count the same file again on every interaction. Processing happens on a button
click instead: `st.button` is True only on the one rerun the click caused.

Run it:  Run and Debug -> "Streamlit Run: Current File"   (see README Reference #1)
Test it: pytest tests/test_streamlit.py -k process_files
"""

import json

import streamlit as st

from packaging_parser import parse_packaging

st.title("Process Package Files")

if "files_processed" not in st.session_state:
    st.session_state.files_processed = 0
    st.session_state.packages_processed = 0
    st.session_state.history = []

uploaded_file = st.file_uploader("Upload package file:", key="package_file")
process_clicked = st.button("Process file", key="process")

if uploaded_file and process_clicked:
    text = uploaded_file.getvalue().decode("utf-8")
    packages = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        packages.append(parse_packaging(line))

    output_path = f"data/{uploaded_file.name.replace('.txt', '.json')}"
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(packages, json_file, indent=4)

    summary = f"{len(packages)} packages written to {output_path}"
    st.session_state.files_processed += 1
    st.session_state.packages_processed += len(packages)
    st.session_state.history.append(summary)

file_column, package_column = st.columns(2)
file_column.metric("Files processed", st.session_state.files_processed)
package_column.metric("Packages processed", st.session_state.packages_processed)

for summary in st.session_state.history:
    st.info(summary)
