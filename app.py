import streamlit as st
import fitz
import os
import tempfile

st.set_page_config(page_title="PDF Scanner", layout="centered")

st.title("PDF Scanner")
st.markdown("Upload your PDFs my love :)")


def highlight_terms(pdf_bytes, original_filename):
    doc = fitz.open("pdf", pdf_bytes)
    found = False

    search_terms = ["data", "and"]

    for term in search_terms:
        for page in doc:
            instances = page.search_for(term, quads=False)
            for inst in instances:
                highlight = page.add_highlight_annot(inst)
                highlight.update()
                found = True

    if not found:
        return None, None

    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    output_filename = f"{base_name}_highlighted.pdf"
    temp_path = os.path.join(tempfile.gettempdir(), output_filename)

    doc.save(temp_path)
    doc.close()

    with open(temp_path, "rb") as f:
        result_bytes = f.read()

    return result_bytes, temp_path, output_filename


uploaded_files = st.file_uploader("", type="pdf", accept_multiple_files=True)

if st.button("Highlight"):
    if not uploaded_files:
        st.warning("Please upload at least one PDF")
    else:
        for uploaded_file in uploaded_files:
            pdf_bytes = uploaded_file.read()
            uploaded_filename = "0_" + uploaded_file.name
            result_bytes, temp_path, output_filename = highlight_terms(pdf_bytes, uploaded_filename)

            if result_bytes:
                st.success(f"✅ Highlighted terms in **{uploaded_file.name}**")

                st.caption(f"Saved temporarily at: `{temp_path}`")
