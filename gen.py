from img_size import get_image_size

from copy import deepcopy

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

page_width, page_height = letter
front = deepcopy(getSampleStyleSheet()["Normal"])
back = deepcopy(getSampleStyleSheet()["Normal"])
back.fontName = "Helvetica-Bold"

# Options
card_width = 2.5
card_height = 3.5
text_offset_x = 10.0
text_offset_y = 10.0
blank = 5
phrase = "Calling All Heretics"
front.fontSize = 14
back.fontSize = 35
img_name = "cards.png"
img_w = 30

# Defining parameters from options
card_width *= inch
card_height *= inch

cards_wide = int(page_width // card_width)
cards_high = int(page_height // card_height)

card_start_top = (page_height - card_height * cards_high) / 2
card_start_side = (page_width - card_width * cards_wide) / 2

card_stop_side = card_start_side + card_width * cards_wide
card_stop_bottom = card_start_top + card_height * cards_high

grid = cards_wide * cards_high

blank = "_" * blank

# Remaining as true as possible to the ratio of the image.
src_img = get_image_size(img_name)
if src_img:
    src_img_w, src_img_h = src_img
    img_h = round(img_w * src_img_h / src_img_w)
else:
    img_h = img_w

assert ''.join(i[0] for i in phrase.split()) == "CAH"
phrase_font_size = 7
front.leading = round(front.fontSize * 1.2)
back.leading = round(back.fontSize * 1.2)


def not_special(card):
    return not card.startswith("//") and card != "\n"


def process_card(card):
    return card.strip()


def process_white(card):
    return "<b>{}</b>".format(process_card(card)) if card else ""


def process_black(card):
    card = process_card(card)
    processed = blank if card.startswith("_") else ""
    processed += blank.join([x for x in card.split("_") if x])
    return "<b>{}</b>".format(processed + blank if card.endswith("_") else processed)


def draw_grid(pdf: Canvas):
    for x in range(cards_wide + 1):
        line_x = card_start_side + card_width * x
        line_y_b = page_height - card_start_top
        line_y_e = page_height - card_stop_bottom
        pdf.line(line_x, line_y_b, line_x, line_y_e)
    for y in range(cards_high + 1):
        line_x_b = card_start_side
        line_x_e = card_stop_side
        line_y = page_height - (card_start_top + card_height * y)
        pdf.line(line_x_b, line_y, line_x_e, line_y)


def write_page(pdf: Canvas, page, image=True):
    pdf.setFont("Helvetica-Bold", phrase_font_size)
    for row_i in range(0, len(page), cards_wide):
        row = page[row_i:row_i + cards_wide]
        for i in range(len(row)):
            start_x = card_start_side + card_width * i
            start_y = card_start_top + card_height * (row_i // cards_wide)

            end_x = start_x + card_width
            end_y = start_y + card_height

            start_x += text_offset_x
            start_y += text_offset_y
            start_y = page_height - start_y

            end_x -= text_offset_x
            end_y -= text_offset_y
            end_y = page_height - end_y

            if image:
                pdf.drawImage("cards.png", start_x, end_y, img_w, img_h)
                pdf.drawString(start_x + img_w + 5, end_y + img_h // 2 - phrase_font_size // 2, phrase)

            card_p = row[i] if isinstance(row[i], Paragraph) else Paragraph(row[i], front)
            size = card_p.wrap(abs(end_x - start_x), abs(end_y - start_y))
            card_p.drawOn(pdf, start_x, start_y - size[1])
    pdf.showPage()


def write_file(cards, filename):
    if not cards:
        return
    file = Canvas(filename, pagesize=letter)
    try:
        for page_start in range(0, len(cards), grid):
            draw_grid(file)
            write_page(file, cards[page_start:page_start + grid])
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
        white_cards = [process_white(card) for card in whites if not_special(card)]

    with open("card_lists/blacks") as blacks:
        black_cards = [process_black(card) for card in blacks if not_special(card)]

    write_file(white_cards, "card_pdf/test_white.pdf")
    write_file(black_cards, "card_pdf/test_black.pdf")
    write_back()
