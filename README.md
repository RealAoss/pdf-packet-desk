# PDF Packet Desk

Assemble selected pages from multiple PDFs into a single local document. Add inputs, choose ranges, rearrange the rows and save to a new PDF. Source documents stay intact.

## Run from source

Use Python 3.10+ with Tkinter. Install the PDF library with `python -m pip install pypdf`, then run `python app.py`.

## Try it

Add a cover document followed by a report. For the report, choose **Edit pages** and enter `4, 1-3`. The output contains the cover followed by report pages 4, 1, 2 and 3. Repeated pages are permitted. Encrypted PDFs require an unlocked input copy. This tool assembles pages; document-level bookmarks, interactive form behavior and digital signatures are outside its scope.
