import pymupdf
import re

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

def find_total(text: str) -> str:
    """
    Finds the total amount in the extracted text of an invoice.

    This function searches for various regex patterns associated with "total" amounts,
    extracts all potential numbers, and returns the highest one, which is
    typically the grand total.

    Args:
        text: The full text of the invoice.

    Returns:
        The total amount as a formatted string or 'N/A' if not found.
    """
    # List of regex patterns to find the total amount.
    # They handle different keywords, currency symbols (€, $), and number formats.
    patterns = [
        # Pattern for keywords like TOTAL, Montant TTC, Amount Due, etc.
        r"(?:Total|TOTAL|Montant\sTTC|Amount\sDue|Solde)\s*:?\s*([€$]?\s*\d{1,3}(?:[.,\s]\d{3})*[.,]\d{2})",
        # A more general pattern looking for a large number at the end of a line
        r"([€$]?\s*\d{1,3}(?:[.,\s]\d{3})*[.,]\d{2})$"
    ]

    found_numbers = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Extract the captured group which contains the number
            potential_number_str = match.group(1)
            
            # Clean the string to convert it to a float
            try:
                # Remove currency symbols and spaces, replace comma with dot for conversion
                cleaned_number_str = potential_number_str.replace('€', '').replace('$', '').replace(' ', '').replace(',', '.')
                found_numbers.append(float(cleaned_number_str))
            except ValueError:
                # Handle cases where conversion might fail
                continue

    if not found_numbers:
        return 'N/A'

    # The grand total is almost always the highest number found
    total = max(found_numbers)
    
    # Return as a string formatted to two decimal places
    return f"{total:.2f}"