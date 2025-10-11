import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.extractor import *

if __name__ == "__main__":
    func = sys.argv[1]
    arg = sys.argv[2]
    
    if func == "find_total":
        print(find_total(extract_text(arg)))
    elif func == "find_date":
        print(find_date(extract_text(arg)))
    elif func == "extract_text":
        print(extract_text(arg))
    elif func == "extract_invoice_data":
        print(extract_invoice_data(arg))

