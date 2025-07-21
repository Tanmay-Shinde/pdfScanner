import streamlit as st
import fitz
import os
import re

st.set_page_config(page_title="PDF Scanner", layout="wide")
st.title("PDF Scanner")
st.markdown("Upload PDFs")

SEARCH_TERMS = ["Gender-Inclusive Policies", "Gender Inclusive Policies", "gender equality", "gender equity", "gender",
                "women's empowerment", "gender-sensitive", "gender-responsive", "gender-transformative", "women",
                "gender mainstreaming", "Participation", "Leadership", "women's participation", "women in leadership",
                "female participation", "Adaptation", "Resilience", "gender-sensitive adaptation", "women's resilience",
                "gender-equitable resilience", "Livelihoods", "Capacity Building", "women's livelihoods", "woman",
                "gender-responsive livelihoods", "women's access to finance", "Social Inclusion", "Justice",
                "gender justice", "gender-based vulnerabilities", "social equity", "climate justice for women",
                "gendered approach", "feminist approach", "rights of women", "gender equity in climate action",
                "skills development for women", "capacity building for women", "empowering women",
                "women's training programs", "economic empowerment of women", "women's climate-smart agriculture",
                "women's rights", "gendered impacts", "gender-inclusive adaptation", "women in adaptation",
                "gendered vulnerabilities", "women and climate resilience", "gender-balanced governance",
                "inclusive decision-making", "women-led initiatives", "women's roles", "female leaders",
                "gender-based analysis", "gender-disaggregated data"]

OUTPUT_FOLDER = os.path.join(os.getcwd(), "highlighted_pdfs")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def extract_paragraphs(text):
    return re.split(r"\n\s*\n|(?<=\.)\s{2,}", text)


def find_matching_paragraphs(text, terms):
    paragraphs = extract_paragraphs(text)
    matches = []
    for para in paragraphs:
        for term in terms:
            if re.search(rf"\b{re.escape(term)}\b", para, re.IGNORECASE):
                matches.append((term, para.strip()))
    return matches


def highlight_and_extract(pdf_bytes, original_filename):
    doc = fitz.open("pdf", pdf_bytes)
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    output_filename = f"{base_name}_highlighted.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    term_data = []

    for page_number, page in enumerate(doc, start=1):
        page_text = page.get_text()
        matched_paragraphs = find_matching_paragraphs(page_text, SEARCH_TERMS)

        for term, para in matched_paragraphs:
            term_data.append({
                "doc": base_name,
                "page": page_number,
                "term": term,
                "paragraph": para
            })

        for term in SEARCH_TERMS:
            instances = page.search_for(term, quads=False)
            for inst in instances:
                highlight = page.add_highlight_annot(inst)
                highlight.update()

    doc.save(output_path)
    doc.close()

    with open(output_path, "rb") as f:
        result_bytes = f.read()

    return result_bytes, output_filename, term_data


uploaded_files = st.file_uploader("", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Highlight & Extract"):
        all_term_data = []
        for uploaded_file in uploaded_files:
            pdf_bytes = uploaded_file.read()
            uploaded_filename = "0_" + uploaded_file.name
            result_bytes, out_name, term_data = highlight_and_extract(pdf_bytes, uploaded_filename)

            all_term_data.extend(term_data)

            if result_bytes:
                st.success(f"Highlighted terms in **{uploaded_file.name}**")

                st.download_button(
                    label="Download Highlighted PDF",
                    data=result_bytes,
                    file_name=out_name,
                    mime="application/pdf",
                )

                st.markdown("---")
                st.subheader("Extracted Paragraphs")
                for match in all_term_data:
                    with st.expander(f"{match['doc']} | Page {match['page']} | Term: '{match['term']}'"):
                        st.markdown(f"**Term:** {match['term']}")
                        st.markdown(f"**Paragraph:** {match['paragraph']}")
