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
text_offset_y = 11.0

front = deepcopy(getSampleStyleSheet()["Normal"])
front.fontSize = 15
front.leading = 18

back = deepcopy(getSampleStyleSheet()["Normal"])
back.fontName = "Helvetica-Bold"
back.fontSize = 35
back.leading = 42

phrase = "Calling All Heretics"
assert ''.join(i[0] for i in phrase.split()) == "CAH"


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


def write_page(pdf: Canvas, page, image=True):
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

            if image:
                pdf.drawImage("cards.png", start_x, end_y, 30, 21)

            card_p = row[i] if isinstance(row[i], Paragraph) else Paragraph("<b>{}</b>".format(row[i]), front)
            size = card_p.wrap(abs(end_x - start_x), abs(end_y - start_y))
            card_p.drawOn(pdf, start_x, start_y - size[1])
    pdf.showPage()


def write_file(cards, filename):
    if not cards:
        return
    file = Canvas(filename, pagesize=letter)
    try:
        for page_start in range(0, len(cards), 9):
            draw_grid(file)
            write_page(file, cards[page_start:page_start + 9])
    finally:
        file.save()


def write_back():
    file = Canvas("card_pdf/back.pdf", pagesize=letter)
    try:
        write_page(file, [Paragraph("<br/>".join(phrase.split()), back) for _ in range(9)], False)
    finally:
        file.save()


if __name__ == "__main__":
    with open("card_lists/whites") as whites:
        white_cards = [card.strip() for card in whites if not_special(card)]

    with open("card_lists/blacks") as blacks:
        black_cards = [card.strip() for card in blacks if not_special(card)]

    write_file(white_cards, "card_pdf/test_white.pdf")
    write_file(black_cards, "card_pdf/test_black.pdf")
    write_back()
