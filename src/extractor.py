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

def find_date(text: str) -> str:
    """
    Finds the invoice date in the extracted text.
    
    Searches for common date formats and prioritizes dates found near
    "date" keywords (invoice date, date de facturation, etc.).
    
    Args:
        text: The full text of the invoice.
        
    Returns:
        The date as a string or 'N/A' if not found.
    """
    # Common date patterns to match various formats
    date_patterns = [
        # DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY (most common in Europe)
        r'\b(\d{1,2}[/.\-]\d{1,2}[/.\-]\d{4})\b',
        # YYYY-MM-DD, YYYY/MM/DD (ISO format)
        r'\b(\d{4}[/.\-]\d{1,2}[/.\-]\d{1,2})\b',
        # Month DD, YYYY (e.g., "Sep 30, 2025", "January 15, 2025")
        r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b',
        # DD Month YYYY (e.g., "27 août 2025", "15 January 2025")
        r'\b(\d{1,2}\s+(?:[A-Za-zéèêàûô]+\.?)\s+\d{4})\b',
    ]
    
    found_dates = []
    
    # Keywords that typically indicate the invoice date
    date_keywords = [
        r'invoice\s+date\s*:?\s*',
        r"date\s+(?:de\s+)?(?:facturation|d['']émission)\s*:?\s*",  # French
        r'date\s*:?\s*',
        r'dated?\s*:?\s*',
        r'facture\s+du\s*:?\s*',  # French: invoice from
    ]
    
    # First priority: Look for dates near "date" keywords
    for keyword in date_keywords:
        for date_pattern in date_patterns:
            # Search for keyword followed by date (within 30 characters)
            pattern = keyword + r'.{0,30}?' + date_pattern
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract the date (last capturing group)
                date_str = match.group(match.lastindex)
                found_dates.append(('priority', date_str))
    
    # Second priority: Look at lines containing "date" keywords
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'\b(?:invoice\s+)?date|facturation|émission', line, re.IGNORECASE):
            # Check this line and next 2 lines
            for j in range(i, min(i + 3, len(lines))):
                for date_pattern in date_patterns:
                    dates = re.findall(date_pattern, lines[j], re.IGNORECASE)
                    for date_str in dates:
                        found_dates.append(('secondary', date_str))
    
    # Third priority: Look for dates anywhere in first 500 characters
    # (invoice dates are usually at the top)
    if not found_dates:
        for date_pattern in date_patterns:
            matches = re.finditer(date_pattern, text[:500], re.IGNORECASE)
            for match in matches:
                date_str = match.group(1)
                found_dates.append(('tertiary', date_str))
    
    if not found_dates:
        return 'N/A'
    
    # Return the highest priority date found
    # Priority order: priority > secondary > tertiary
    priority_order = {'priority': 0, 'secondary': 1, 'tertiary': 2}
    found_dates.sort(key=lambda x: priority_order[x[0]])
    
    return found_dates[0][1]

def find_vendor(text: str) -> str:
    """
    Finds the vendor/company name in the extracted text.
    
    Looks for company names using legal entity indicators (LLC, SARL, Inc, etc.)
    and other patterns typically associated with vendor information.
    
    Args:
        text: The full text of the invoice.
        
    Returns:
        The vendor name as a string or 'N/A' if not found.
    """
    found_vendors = []
    lines = text.split('\n')
    
    # Priority 1: Look for company names with legal entity indicators
    # Process line by line to avoid cross-line matches
    entity_pattern = r'\b([A-Z][A-Za-z0-9&\-\.]+(?:\s+[A-Z][A-Za-z0-9&\-\.]+){0,4}\s+(?:SARL|LLC|Inc\.?|Ltd\.?|Limited|B\.V\.?|GmbH|S\.A\.?|SE|Corporation|Corp\.?))\b'
    
    for line in lines:
        match = re.search(entity_pattern, line)
        if match:
            vendor = match.group(1).strip()
            # Filter out very short matches, common false positives, and lines with too many words
            word_count = len(vendor.split())
            if (len(vendor) > 5 and 
                word_count <= 6 and 
                not re.match(r'^\d', vendor) and
                not re.search(r'\b(Total|Invoice|Billing|Payment|Service|Description)\b', vendor, re.IGNORECASE)):
                found_vendors.append(('high_priority', vendor))
    
    # Priority 2: Look for lines near "émetteur" (issuer) or "from" keywords
    for i, line in enumerate(lines):
        if re.search(r'\b(?:émetteur|from|seller|vendor|billed?\s+by)\b', line, re.IGNORECASE):
            # Check next 2 lines for potential vendor names
            for j in range(i + 1, min(i + 3, len(lines))):
                vendor = lines[j].strip()
                # Look for capitalized names (at least 2 words or one word with 5+ chars)
                if vendor and len(vendor) > 4 and vendor[0].isupper():
                    # Exclude lines with numbers, dates, or common keywords
                    if not re.search(r'^\d|date|facture|invoice|total|address|street|road', vendor, re.IGNORECASE):
                        found_vendors.append(('medium_priority', vendor))
    
    # Priority 3: Look in first 30 lines for distinctive company names
    # (vendors are usually at the top)
    if not found_vendors:
        for i, line in enumerate(lines[:30]):
            vendor = line.strip()
            # Look for short, capitalized lines that might be company names
            # Must be 3-50 characters, start with uppercase, minimal numbers
            if (3 < len(vendor) < 50 and 
                vendor[0].isupper() and 
                vendor.replace(' ', '').replace('-', '').replace('&', '').isalpha() and
                not re.search(r'\b(invoice|facture|page|date|total|billing|account|details|summary|description|quantity|quantité|prix|price|tax|payment|balance|désignation|destinataire|émetteur|numéro|number|amount)\b', vendor, re.IGNORECASE)):
                # Bonus: if it's ALL CAPS or Title Case, more likely to be a company
                if vendor.isupper() or vendor.istitle():
                    found_vendors.append(('low_priority', vendor))
    
    if not found_vendors:
        return 'N/A'
    
    # Sort by priority and return the first one
    priority_order = {'high_priority': 0, 'medium_priority': 1, 'low_priority': 2}
    found_vendors.sort(key=lambda x: priority_order[x[0]])
    
    return found_vendors[0][1]
