from img_size import get_image_size

from copy import deepcopy

from reportlab.lib.colors import black
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

page_width, page_height = letter
front = deepcopy(getSampleStyleSheet()["Normal"])
back = deepcopy(getSampleStyleSheet()["Normal"])
back.fontName = "Helvetica-Bold"
title_font_size = 7


def card_back(title, grid):
    return [Paragraph("<br/>".join(title.split()), back) for _ in range(grid)]


def set_style(font_size, is_front):
    if is_front:
        front.fontSize = font_size
        front.leading = round(front.fontSize * 1.2)
    else:
        back.fontSize = font_size
        back.leading = round(back.fontSize * 1.2)


def process_grid(card_wdt, card_hgt):
    card_wdt *= inch
    card_hgt *= inch

    cards_wide = int(page_width // card_wdt)
    cards_high = int(page_height // card_hgt)

    grid_start_top = (page_height - card_hgt * cards_high) / 2
    grid_start_left = (page_width - card_wdt * cards_wide) / 2

    grid_stop_right = grid_start_left + card_wdt * cards_wide
    grid_stop_bottom = grid_start_top + card_hgt * cards_high

    grid = cards_wide * cards_high

    return card_wdt, card_hgt, cards_wide, cards_high,\
        grid_start_top, grid_start_left, grid_stop_right, grid_stop_bottom, grid


def not_special(card):
    return not card.startswith("//") and card != "\n"


def process_card(card):
    return card.strip()


def process_white(card):
    return "<b>{}</b>".format(process_card(card)) if card else ""


def process_black(card, blank):
    card = process_card(card)
    if blank:
        processed = blank if card.startswith("_") else ""
        processed += blank.join([x for x in card.split("_") if x])
        card = processed + blank if card.endswith("_") else processed
    return "<b>{}</b>".format(card)


def process_whites(cards):
    return [process_white(card) for card in cards if not_special(card)]


def process_blacks(cards, normalize):
    return [process_black(card, normalize) for card in cards if not_special(card)]


def draw_grid(pdf: Canvas, *options):
    card_wdt, card_hgt, cards_wide, cards_high,\
        grid_start_left, grid_start_top, grid_stop_right, grid_stop_bottom = options
    for x in range(cards_wide + 1):
        line_x = grid_start_left + card_wdt * x
        line_y_b = page_height - grid_start_top
        line_y_e = page_height - grid_stop_bottom
        pdf.line(line_x, line_y_b, line_x, line_y_e)
    for y in range(cards_high + 1):
        line_x_b = grid_start_left
        line_x_e = grid_stop_right
        line_y = page_height - (grid_start_top + card_hgt * y)
        pdf.line(line_x_b, line_y, line_x_e, line_y)


def write_page(pdf: Canvas, page, has_image, card_wdt, card_hgt, cards_wide, grid_start_left, grid_start_top,
               margin_x, margin_y, icon_fn, icon_w, icon_h, title, stripe_color=None, stripe_text=None):
    pdf.setFont("Helvetica-Bold", title_font_size if has_image else int(margin_y) - 1)
    for row_i in range(0, len(page), cards_wide):
        row = page[row_i:row_i + cards_wide]
        for i in range(len(row)):
            start_x = grid_start_left + card_wdt * i
            start_y = grid_start_top + card_hgt * (row_i // cards_wide)

            end_x = start_x + card_wdt
            end_y = start_y + card_hgt

            start_x += margin_x
            start_y += margin_y
            start_y = page_height - start_y

            end_x -= margin_x
            end_y -= margin_y
            end_y = page_height - end_y

            if has_image:
                pdf.drawImage(icon_fn, start_x, end_y, icon_w, icon_h)
                pdf.drawString(start_x + icon_w + 5, end_y + icon_h // 2 - title_font_size // 2, title)
            elif stripe_color and stripe_text is not None:
                pdf.setFillColor(stripe_color)
                pdf.rect(start_x - margin_x, end_y - margin_y, card_wdt, margin_y, fill=1)
                pdf.setFillColor(black)
                pdf.drawString(start_x, end_y - round(margin_y * 0.8), stripe_text)

            card_p = row[i] if isinstance(row[i], Paragraph) else Paragraph(row[i], front)
            size = card_p.wrap(abs(end_x - start_x), abs(end_y - start_y))
            card_p.drawOn(pdf, start_x, start_y - size[1])

    pdf.showPage()


def write_file(cards, output_fn, card_wdt, card_hgt, margin_x, margin_y, title, icon_fn, icon_w,
               stripe_color=None, stripe_text='', duplex=False):
    card_wdt, card_hgt, cards_wide, cards_high, \
        grid_start_top, grid_start_left, grid_stop_right, grid_stop_bottom, grid = process_grid(card_wdt, card_hgt)

    src_img = get_image_size(icon_fn)
    if src_img:
        src_img_w, src_img_h = src_img
        icon_h = round(icon_w * src_img_h / src_img_w)
    else:
        icon_h = icon_w

    if not cards:
        return

    file = Canvas(output_fn, pagesize=letter)
    try:
        for page_start in range(0, len(cards), grid):
            if stripe_color:
                file.setStrokeColor(black)
            draw_grid(file, card_wdt, card_hgt, cards_wide, cards_high,
                      grid_start_left, grid_start_top, grid_stop_right, grid_stop_bottom)
            write_page(file, cards[page_start:page_start + grid], True,
                       card_wdt, card_hgt, cards_wide, grid_start_left, grid_start_top, margin_x, margin_y,
                       icon_fn, icon_w, icon_h, title)
            if duplex:
                if stripe_color:
                    file.setStrokeColor(stripe_color)
                write_page(file, card_back(title, grid), False, card_wdt, card_hgt, cards_wide,
                           grid_start_left, grid_start_top, margin_x, margin_y, "", 0, 0, title,
                           stripe_color, stripe_text)
    finally:
        file.save()


def write_back(output_fn, card_wdt, card_hgt, margin_x, margin_y, title, stripe_color=None, stripe_text=None):
    card_wdt, card_hgt, cards_wide, cards_high,\
        grid_start_top, grid_start_left, grid_stop_right, grid_stop_bottom, grid = process_grid(card_wdt, card_hgt)

    file = Canvas(output_fn, pagesize=letter)
    try:
        if stripe_color:
            file.setStrokeColor(stripe_color)
        write_page(file, card_back(title, grid), False, card_wdt, card_hgt, cards_wide,
                   grid_start_left, grid_start_top, margin_x, margin_y, "", 0, 0, title, stripe_color, stripe_text)
    finally:
        file.save()


if __name__ == '__main__':
    from reportlab.lib.colors import crimson
    set_style(35, False)
    write_back("cards/test_back.pdf", 2.5, 3.5, 10.0, 10.0, "Calling All Heretics", crimson, "Test pack 1")
