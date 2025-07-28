import fitz  # PyMuPDF
import json
import os
import re

def extract_outline_from_text(pdf_path):
    doc = fitz.open(pdf_path)
    custom_outline = []

    # Patterns
    numbered_heading_pattern = re.compile(r"^(\d+(\.\d+)*)(\.?)\s+([A-Z][a-zA-Z0-9\-\s\(\)]{2,})$")
    number_only_pattern = re.compile(r"^(\d+(\.\d+)*)(\.?)$")
    title_only_pattern = re.compile(r"^([A-Z][a-zA-Z0-9\-\s\(\)]{2,})$")
    unnumbered_headings = [
        "Abstract", "Introduction", "Related Works", "Methodology",
        "Results", "Conclusion", "References", "Acknowledgements"
    ]
    unnumbered_heading_pattern = re.compile(
        r"^({})$".format("|".join(re.escape(h) for h in unnumbered_headings)), re.IGNORECASE
    )

    VERTICAL_THRESHOLD = 25
    pending_number_block = None

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[1], b[0]))  # Sort by vertical and then horizontal position

        for block in blocks:
            text = block[4].strip()
            y0, y1 = block[1], block[3]

            if not text:
                continue

            # Unnumbered heading
            if unnumbered_heading_pattern.match(text):
                custom_outline.append({
                    "level": "H1",
                    "text": text,
                    "page": page_num + 1
                })
                pending_number_block = None
                continue

            # Number-only block (e.g., "1", "2.3")
            if number_only_pattern.match(text):
                pending_number_block = {
                    "number": text,
                    "y1": y1,
                    "page": page_num + 1
                }
                continue

            # Combine number + title if vertically close
            if pending_number_block and (abs(y0 - pending_number_block["y1"]) < VERTICAL_THRESHOLD):
                if title_only_pattern.match(text):
                    full_text = f"{pending_number_block['number']} {text}"
                    level = full_text.count('.') + 1
                    custom_outline.append({
                        "level": f"H{level}",
                        "text": full_text.strip(),
                        "page": pending_number_block['page']
                    })
                    pending_number_block = None
                    continue

            # Complete numbered heading in one line
            match = numbered_heading_pattern.match(text)
            if match:
                number_part = match.group(1)
                level = number_part.count('.') + 1
                custom_outline.append({
                    "level": f"H{level}",
                    "text": text,
                    "page": page_num + 1
                })
                pending_number_block = None
                continue

            pending_number_block = None  # Reset if not matched

    doc.close()
    title = doc.metadata.get("title") or os.path.basename(pdf_path)
    return {
        "title": title,
        "outline": custom_outline
    }

def main():
    input_folder = "input"
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith(".pdf"):
            continue

        pdf_path = os.path.join(input_folder, filename)
        print(f"\n>>> Extracting outline for: {filename}")
        try:
            result = extract_outline_from_text(pdf_path)
            output_file = os.path.splitext(filename)[0] + "_outline.json"
            output_path = os.path.join(output_folder, output_file)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"✔ Saved outline to {output_file}")
        except Exception as e:
            print(f"✖ Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
