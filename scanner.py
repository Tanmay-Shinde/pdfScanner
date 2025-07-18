import fitz
import os


def highlight_search_terms(input_folder):
    output_folder = input_folder + "_highlighted/"
    os.makedirs(output_folder, exist_ok=True)

    search_terms = ["data", "and"]

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename.replace(".pdf", "_highlighted.pdf"))

            doc = fitz.open(input_file)
            found = False

            for search_term in search_terms:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text_instances = page.search_for(search_term)

                    for inst in text_instances:
                        found = True
                        highlight = page.add_highlight_annot(inst)
                        highlight.update()

            if found:
                doc.save(output_file)

            doc.close()


if __name__ == "__main__":
    files_folder = "../../Desktop/files"

    highlight_search_terms(files_folder)
