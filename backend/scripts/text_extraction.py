import pdfplumber

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            count = 1
            for page in pdf.pages:
                print(f"processing page : {count}")
                page_text = page.extract_text()
                if page_text:
                    text += page_text+"\n"
                count += 1
    except Exception as e:
        print(f"Error in extracting text : {e}")
        return None
    
    return text


# Save to file
pdf_path = "../data/harrypotter_book.pdf"
book_text = extract_text_from_pdf(pdf_path)
if book_text:
    with open("book_text.txt","w",encoding="utf-8") as f:
        f.write(book_text)
                