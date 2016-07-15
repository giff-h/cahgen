from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# FIXME change all numbers from inches to whatever
card_start_top = 0.25 * inch
card_start_side = 0.5 * inch
card_height = 3.5 * inch
card_width = 2.5 * inch
card_stop_side = card_start_side + card_width * 3
card_stop_bottom = card_start_top + card_height * 3


def draw_grid(pdf: canvas.Canvas):
    for x in range(4):
        pdf.line(card_start_side + card_width * x, card_start_top,
                 (11 * inch) - card_start_side + card_width * x, card_stop_bottom)
    for y in range(4):
        pdf.line(card_start_side, card_start_top + card_height * y,
                 card_stop_side,  card_start_top + card_height * y)


def write_page(pdf: canvas.Canvas, page):
    draw_grid(pdf)
    for row_i in range(0, len(page), 3):
        row = page[row_i:row_i+3]
        for i in range(len(row)):
            start_x = card_start_side + card_width * i
            start_y = card_start_top + card_height * (row_i // 3)
            pdf.drawString(100, 100, "Hello")
            pdf.drawString(100, 300, "There")
            pdf.drawString(start_x, start_y, str((start_x / inch, start_y / inch)))


if __name__ == "__main__":
    file = canvas.Canvas("test.pdf", pagesize=letter)
    write_page(file, list(range(9)))
    file.showPage()
    file.save()
