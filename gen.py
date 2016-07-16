from copy import deepcopy

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

page_width, page_height = letter

card_start_top = 0.25 * inch
card_start_side = 0.5 * inch
card_height = 3.5 * inch
card_width = 2.5 * inch
card_stop_side = card_start_side + card_width * 3
card_stop_bottom = card_start_top + card_height * 3

text_offset_x = 11.0
text_offset_y = 12.0

style = deepcopy(getSampleStyleSheet()["Normal"])
style.fontSize = 15
style.leading = 18

licensing = "Cards Against Humanity is a trademark of Cards Against Humanity, LLC. \
Cards Against Humanity is distributed under a Creative Commons BY-NC-SA 2.0 license."


def not_special(card):
    return not card.startswith("//") and card != "\n"


def draw_grid(pdf: Canvas):
    for x in range(4):
        line_x = card_start_side + card_width * x
        line_y_b = page_height - card_start_top
        line_y_e = page_height - card_stop_bottom
        pdf.line(line_x, line_y_b, line_x, line_y_e)
    for y in range(4):
        line_x_b = card_start_side
        line_x_e = card_stop_side
        line_y = page_height - (card_start_top + card_height * y)
        pdf.line(line_x_b, line_y, line_x_e, line_y)


def write_page(pdf: Canvas, page):
    draw_grid(pdf)
    pdf.setFont("Times-Roman", 8, 10)
    pdf.drawCentredString(page_width / 2, page_height - 13, licensing)
    for row_i in range(0, len(page), 3):
        row = page[row_i:row_i+3]
        for i in range(len(row)):
            start_x = card_start_side + card_width * i
            start_y = card_start_top + card_height * (row_i // 3)

            end_x = start_x + card_width
            end_y = start_y + card_height

            start_x += text_offset_x
            start_y += text_offset_y
            start_y = page_height - start_y

            end_x -= text_offset_x
            end_y -= text_offset_y
            end_y = page_height - end_y

            card_p = Paragraph("<b>{}</b>".format(row[i]), style)
            size = card_p.wrap(abs(end_x - start_x), abs(end_y - start_y))
            card_p.drawOn(pdf, start_x, start_y - size[1])
    pdf.showPage()


def write_file(cards, filename):
    if not cards:
        return
    file = Canvas(filename, pagesize=letter)
    try:
        for page_start in range(0, len(cards), 9):
            write_page(file, cards[page_start:page_start + 9])
    finally:
        file.save()


if __name__ == "__main__":
    with open("cards/whites") as whites:
        white_cards = [card.strip() for card in whites if not_special(card)]

    with open("cards/blacks") as blacks:
        black_cards = [card.strip() for card in blacks if not_special(card)]

    write_file(white_cards, "test_white.pdf")
    write_file(black_cards, "test_black.pdf")
