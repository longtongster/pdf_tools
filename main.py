"""
Code related to the reportlab library was taken from the following reference:
https://realpython.com/creating-modifying-pdf/
"""

import os
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import grey


def create_page_pdf(num, tmp, text):
    """
    This function creates an empty pdf with only a page number at the bottom and saves
    the result in tmp
    :param num: an integer that determines the number of pages to create in the pdf
    :param tmp: filename used to save the resulting pdf
    """
    c = canvas.Canvas(tmp, pagesize=A4)
    for i in range(1, num + 1):
        c.setFont("Times-Roman", 11)
        c.setFillColor(grey)
        # writing footer text to the bottom middle of the page
        c.drawString((210 // 2) * mm - 20 * mm, (4) * mm, text + f" page {i}")
        c.showPage()
    c.save()


def add_page_numbers(pdf_path, new_path, text):
    """
    Add page numbers and a footer to a pdf, saves the result to a new pdf
    :param pdf_path: source pdf
    :param new_path: name of destination pdf
    :param text: footer text
    """
    tmp = "__tmp.pdf"

    writer = PdfWriter()
    # 1. Create a reader object for the pdf to which we want to add page numbers
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        n = len(reader.pages)

        # 2. create new PDF that contains a footer and page numbers
        create_page_pdf(n, tmp, text)

        # 3. create a second reader for the new PDF
        with open(tmp, "rb") as ftmp:
            number_pdf = PdfReader(ftmp)
            # iterarte pages
            for p in range(n):
                # .pages is PageObject represents a single page within a PDF file
                page = reader.pages[p]
                number_layer = number_pdf.pages[p]
                # merge number page with the page containing the footer and page number in one page
                page.merge_page(number_layer)
                writer.add_page(page)

            # write result
            if len(writer.pages) > 0:
                print(new_path)
                with open(new_path, "wb") as f:
                    writer.write(f)
        # remove the pdf that just contains the page numbers
        # this is just a 'helper pdf'
        os.remove(tmp)

def merge_pdf_list(src_dir, dst_pdf_path):
    """
    merges a list of pdfs to one big pdf and adds a bookmark for each pdf
    :param src_dir: source directory that contains the pdfs to merge
    :param dst_pdf_path: destination file path to save the merged pdfs
    """

    input_path = Path(input_dir)
    writer = PdfWriter()   # instantiate a pdf writer
    bookmark_page_number = 0   # initiate the bookmark_page_number

    # go over each pdf in the src_dir and add it to the writer
    for path in input_path.glob("*.pdf"):
        with open(path, "rb") as fr:
            reader = PdfReader(fr)             # Bind the file to the pdf reader
            num_pages = len(reader.pages)      # Get number of pages
            for page_num in range(num_pages):
                page = reader.pages[page_num]  # Read a page
                writer.add_page(page)          # Write the page

        # After each file add a bookmark and adjust the bookmark_page_number
        writer.add_outline_item(title=path.name, page_number=bookmark_page_number)
        bookmark_page_number += num_pages

    # write the output to a pdf on disk
    with open(dst_pdf_path,"wb") as fw:
        writer.write(fw)


if __name__ == "__main__":
    input_dir = "files"
    target_path = "output/final.pdf"
    merge_pdf_list(input_dir, target_path)

    #print(os.listdir("./files"))
    footer_text = "MGC deck 06-03-2023"
    add_page_numbers(target_path, "output/output.pdf", footer_text)