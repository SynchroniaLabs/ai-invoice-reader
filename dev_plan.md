## Phase 1: Setup & Foundations 🏗️

First, let's get our workshop in order. A clean setup prevents headaches later.

1.  **Project Structure:** Create a main folder `ai-invoice-reader`. Inside, create a `src` folder where our Python code will live.
2.  **Virtual Environment:** In your terminal, navigate into `ai-invoice-reader` and create a virtual environment: `python -m venv venv`. Activate it.
3.  **Install Our Tools:** With the environment active, run this command to install everything we need:
    ```bash
    pip install FreeSimpleGUI PyMuPDF pandas pyperclip
    ```
      * **`pyperclip`** is a neat little library that will let us copy the final data to the clipboard, which is perfect for our "Copy to Excel" button.

-----

## Phase 2: The Core Logic - The Extractor 🧠

This is the "AI" brain of our app. We'll build this logic in a file named `src/extractor.py`. The goal is one main function, `extract_invoice_data(pdf_path)`, which will do all the work and return a dictionary of the results.

1.  **Read the PDF:** Create a function that takes a `pdf_path`. Inside, use **PyMuPDF** to open the PDF file, iterate through its pages, and extract all the raw text into a single string variable. This gives us the raw material to work with.
2.  **Find the Data with "AI" (Regular Expressions):** This is where the magic happens. We'll create small, focused functions for each piece of data we want. Regular Expressions (regex) are patterns we use to search for specific text formats.
      * **Find the Total:** Write a function `find_total(text)`. It will search the text for keywords like "Total," "Total Due," or "Amount," followed by a currency symbol (€ or $) and a number pattern (e.g., `\d+\.\d{2}`). This is our most important and reliable extraction.
      * **Find the Date:** Write a function `find_date(text)`. It will search for common date formats like `DD/MM/YYYY`, `Month DD, YYYY`, etc.
      * **Find the Vendor:** This one is trickier. For our simple version, a good starting point is to assume the vendor's name is in the first few lines of the text. Write a function `find_vendor(text)` that just returns the first non-empty line from the document.
3.  **Assemble the Data:** In your main `extract_invoice_data` function, call these smaller functions. Have it return a Python dictionary like: `{'vendor': 'Vendor Name', 'date': '26/09/2025', 'total': '199.99'}`. If a piece of data isn't found, it should return 'N/A'.

-----

## Phase 3: The User Interface 🖥️

Now let's build the user-facing part in a file named `src/main.py`. This is what the user will see and interact with.

1.  **Design the Layout:** Using **PySimpleGUI**, define the layout. Keep it clean:
      * A title and a short instruction line: "Drag & Drop a PDF invoice below or browse to select a file."
      * An input field for the file path with a "Browse" button next to it.
      * A main **"Extract Data"** button.
      * Clearly labeled, read-only output fields for "Vendor," "Date," and "Total."
      * A **"Copy to Excel"** button that is initially disabled.
2.  **Create the Event Loop:** Write the standard `while True` loop that reads events from the window. This will handle all the button clicks and interactions.

-----

## Phase 4: Integration - Making It Work 🔗

This is where we connect the UI to our extractor brain inside `main.py`.

1.  **Handle File Selection:** In the event loop, if the user clicks **"Browse"**, use `sg.popup_get_file` to let them select a PDF. When they choose one, update the file path input field in the window.
2.  **Trigger Extraction:** When the user clicks **"Extract Data"**:
      * Get the PDF path from the input field.
      * Call the `extract_invoice_data()` function from your `extractor.py` file.
      * **Important:** Wrap this call in a `try...except` block. If the extractor fails (e.g., the PDF is corrupted or the data isn't found), show a user-friendly error popup.
3.  **Display the Results:** If the extraction is successful, use the window's `update` method to fill in the "Vendor," "Date," and "Total" output fields with the data you got back.
4.  **Enable the Copy Button:** After a successful extraction, enable the "Copy to Excel" button so the user can click it.
5.  **Handle the Copy Action:** When the user clicks **"Copy to Excel"**:
      * Take the extracted data from the output fields.
      * Format it into a simple, tab-separated string (`vendor\tdate\ttotal`).
      * Use **`pyperclip.copy()`** to place this string onto the user's clipboard.
      * Show a final success popup: `Data copied to clipboard!`

-----

## Phase 5: Final Touches & Delivery 🚀

Let's polish it up and prepare it for the world.

1.  **Error Handling:** Go back through your code and make sure it handles problems gracefully. What happens if the user selects a non-PDF file? What if the PDF has no text? Show clear error messages.
2.  **Create a Simple Executable:** To make it easy for anyone to use (without needing Python), we can package it. Install PyInstaller with `pip install pyinstaller`. Then, from your terminal, run `pyinstaller --onefile --windowed src/main.py`. This will create a single `.exe` file in a new `dist` folder. This is your distributable app.
3.  **Write the README:** Create a fantastic `README.md` file. Include a GIF of the app in action, clear installation/usage instructions (or a link to the executable), and the crucial "This is a simple demo; contact us for a full-featured solution" section to drive leads.

That's the plan. Follow it step-by-step, focusing on one phase at a time, and you'll have a professional, high-value demo app ready to go. Let me know if you hit any snags.