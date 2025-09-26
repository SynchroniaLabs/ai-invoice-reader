import pymupdf

def extract_invoice_data(pdf_path: str) -> dict:
    """
    Extracts invoice data from a PDF file.
    """
    pass

def extract_text(pdf_path: str) -> str:
    """
    Extracts text from a PDF file.
    """
    raw_text = ""

    with pymupdf.open(pdf_path) as pdf:
        for page in pdf:
            raw_text += page.extract_text()
            raw_text += "\n"

    return raw_text




    

    




