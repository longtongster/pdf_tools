"""
Code related to the reportlab library was taken from the following reference:
https://realpython.com/creating-modifying-pdf/
"""

# TODO: Think about the exact flow that is required and make sure the parameters align with this
# TODO: Blank page should be created as temporary file and removed afterwards
# TODO: there should be only one final output with page numbers

import os
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from argparse import ArgumentParser

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import grey


def create_page_pdf(num:int, tmp:str, text:str):
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
        c.drawString((210 // 2) * mm - 20 * mm, (4) * mm, text + f" page {i} of {num}")
        c.showPage()
    c.save()


def add_page_numbers(pdf_path:str, new_path:str, text:str):
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


def create_blank_page(dst_pdf_path:str):
    """
    Creates a blank pdf page of A4 format and writes it to disk
    :param dst_pdf_path: the file path for the newly created blank pdf
    """
    with open(dst_pdf_path, "wb") as f:
        writer = PdfWriter()
        writer.add_blank_page(210 * mm, 279 * mm)
        writer.write(f)


def merge_pdf_list_2(src_dir:str, dst_pdf_path:str):
    """
    merges a list of pdfs to one big pdf and adds a bookmark for each pdf
    :param src_dir: source directory that contains the pdfs to merge
    :param dst_pdf_path: destination file path to save the merged pdfs
    """

    input_path = Path(src_dir)
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

def merge_pdf_list(src_dir:str, dst_pdf_path:str, blank_path:str=None):
    """
    merges a list of pdfs to one big pdf and adds a bookmark for each pdf
    :param src_dir: source directory that contains the pdfs to merge
    :param dst_pdf_path: destination file path to save the merged pdfs
    :param blank_path: if provided the function will create a blank page and add it between each pdf that is merged
    """
    input_path = Path(src_dir)
    merger = PdfMerger()   # instantiate a pdf writer

    # if blank_path is provided create a blank pdf
    if blank_path:
        create_blank_page((blank_path))

    # go over each pdf in the src_dir and append it to the merger
    for path in input_path.glob("*.pdf"):
        with open(path, "rb") as f:
            merger.append(f, str(path))
            # if there is a blank_path add a blank page
            if blank_path:
                with open(blank_path,"rb") as fb:
                    merger.append(fb)
                    fb.close()
    # write all pdfs in the merger to dst_pdf_path
    with open(dst_pdf_path, "wb") as fw:
        merger.write(fw)

    # delete the blank page to keep a clean working space
    os.remove(blank_path)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=str,
                        help="directory path that contains the pdfs to be converted")

    parser.add_argument("--output-path", required=True, type=str,
                        help="file path to which file with merged pdfs should be written")

    args = parser.parse_args()
    print(args)

    #input_dir = "./files"
    #target_path = "./output/final.pdf"
    #target_path2 = "./output/final2.pdf"
    blank_page = "./output/blank.pdf"
    merge_pdf_list(args.input_dir, args.output_path, blank_page)
    #create_blank_page(blank_page)

    #print(os.listdir("./files"))
    footer_text = "MGC deck 06-03-2023"
    add_page_numbers(args.output_path, "output/output.pdf", footer_text)