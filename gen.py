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

text_offset_x = 10.0
text_offset_y = 23.0


def draw_grid(pdf: canvas.Canvas):
    for x in range(4):
        line_x = card_start_side + card_width * x
        line_y_b = letter[1] - card_start_top
        line_y_e = letter[1] - card_stop_bottom
        pdf.line(line_x, line_y_b, line_x, line_y_e)
    for y in range(4):
        line_x_b = card_start_side
        line_x_e = card_stop_side
        line_y = letter[1] - (card_start_top + card_height * y)
        pdf.line(line_x_b, line_y, line_x_e, line_y)


def write_page(pdf: canvas.Canvas, page):
    draw_grid(pdf)
    for row_i in range(0, len(page), 3):
        row = page[row_i:row_i+3]
        for i in range(len(row)):
            start_x = text_offset_x + card_start_side + card_width * i
            start_y = text_offset_y + card_start_top + card_height * (row_i // 3)
            start_y = letter[1] - start_y
            pdf.drawString(start_x, start_y, str((row_i, i, row[i])))


if __name__ == "__main__":
    file = canvas.Canvas("test.pdf", pagesize=letter)
    write_page(file, list(range(9)))
    file.showPage()
    file.save()
