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
            raw_text += page.get_text()
            raw_text += "\n"

    return raw_text

def find_total(text: str) -> str:
    """
    Finds the total amount in the extracted text of an invoice.

    This function searches for common invoice total patterns and returns
    the highest number found near "total" keywords.

    Args:
        text: The full text of the invoice.

    Returns:
        The total amount as a formatted string or 'N/A' if not found.
    """
    # Pattern to find any currency amount (with or without currency symbols)
    # Matches formats like: €123.45, $1,234.56, 123.45, 1 234,56, etc.
    # Also handles encoding issues (� for €)
    amount_pattern = r'[€$£¥₹�]?\s*\d{1,3}(?:[.,\s]\d{3})*[.,]\d{2}'
    
    # Keywords that typically indicate the total amount
    total_keywords = [
        r'total\s+(?:in\s+[A-Z]{3}\s+)?',  # "Total in EUR", "Total"
        r'total\s*:?\s*',                    # "Total:", "Total"
        r'montant\s+ttc\s*:?\s*',           # French: "Montant TTC"
        r'amount\s+due\s*:?\s*',            # "Amount Due"
        r'balance\s+due\s*:?\s*',           # "Balance Due"
        r'grand\s+total\s*:?\s*',           # "Grand Total"
        r'net\s+total\s*:?\s*',             # "Net Total"
    ]
    
    found_numbers = []
    
    # Search for amounts near total keywords
    for keyword in total_keywords:
        # Look for keyword followed by amount (within reasonable distance)
        pattern = keyword + r'.{0,20}?' + f'({amount_pattern})'
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            potential_number_str = match.group(1)
            found_numbers.append(potential_number_str)
    
    # Also look for lines near "total" keywords
    # Prioritize amounts AFTER "Total" keyword (actual totals)
    # over amounts BEFORE it (often subtotals or gross amounts)
    lines = text.split('\n')
    priority_numbers = []  # Amounts found after "Total"
    secondary_numbers = []  # Amounts found before "Total"
    
    for i, line in enumerate(lines):
        if re.search(r'\btotal\b', line, re.IGNORECASE):
            # Check same line and lines after first (these are usually the actual totals)
            for j in range(i, min(i + 4, len(lines))):
                amounts = re.findall(amount_pattern, lines[j])
                priority_numbers.extend(amounts)
            
            # Also check lines before (but these are lower priority)
            for j in range(max(0, i - 2), i):
                amounts = re.findall(amount_pattern, lines[j])
                secondary_numbers.extend(amounts)
    
    # Prefer priority numbers (after Total) over secondary (before Total)
    if priority_numbers:
        found_numbers.extend(priority_numbers)
    else:
        found_numbers.extend(secondary_numbers)
    
    if not found_numbers:
        return 'N/A'
    
    # Convert all found numbers to floats
    cleaned_numbers = []
    for num_str in found_numbers:
        try:
            # Remove currency symbols and clean up (including � for encoding issues)
            cleaned = re.sub(r'[€$£¥₹�\s]', '', num_str)
            # Handle both comma and dot as decimal separators
            # If there are multiple separators, the last one is the decimal
            if ',' in cleaned and '.' in cleaned:
                # Both present: remove thousand separator, keep decimal
                if cleaned.rindex(',') > cleaned.rindex('.'):
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Only comma: assume decimal separator if it's the last separator
                cleaned = cleaned.replace(',', '.')
            
            cleaned_numbers.append(float(cleaned))
        except (ValueError, AttributeError):
            continue
    
    if not cleaned_numbers:
        return 'N/A'
    
    # Return the highest amount found (typically the grand total)
    total = max(cleaned_numbers)
    return f"{total:.2f}"