from pdf_gen import set_style, process_blacks, process_whites, write_file, write_back

import click


def validate_positive(ctx, param, value):
    if value <= 0:
        raise click.BadParameter(param + " needs to be at positive number")
    return value


def validate_blank(ctx, param, value):
    if value <= 0:
        raise click.BadParameter("blank needs to be at least 0")
    return "_" * 5


class TitleType(click.ParamType):
    name = "title"

    def convert(self, value, param, ctx):
        value = value.strip()
        try:
            assert [i[0] for i in value.split()] == ['C', 'A', 'H']
        except AssertionError:
            self.fail(value + " is not a valid title. Please have it be an acronym of CAH")


TITLE_TYPE = TitleType()

default_width = 2.5
default_height = 3.5
default_side_margin = 10
default_top_margin = 10
default_title = "Calling All Heretics"
default_front_fs = 14
default_back_fs = 35

width_help = "Width of each card in inches. Defaults to {}".format(default_width)
height_help = "Height of each card in inches. Defaults to 3.5"
tm_help = "Top and bottom card print margin in pixels. Defaults to 10"
sm_help = "Left and right card print margin in pixels. Defaults to 10"
blank_help = "Number of underscores to normalize the size of the blank spaces to in the black cards. \
Meant to prevent you from pulling your hair out making sure all the blank marks are the same. Defaults to 5. \
If set to 0, no normalizing will be done"
title_help = "The game title to be printed on the back and the bottom of the front of all the cards. \
Make sure it's an acronym of CAH. Remember that the phrase Cards Against Humanity is copywright."
font_size_help = "Font size of the text printed on the card. \
Does not automatically check whether a huge message will print correctly on the card. Please check your output files. \
Defaults to {}"
icon_help = "Image file to be used as the icon on the front of the card. Defaults to cards.png"
icon_width_help = "Pixel width to print the icon on the front of the card. \
Height is scaled to match original ratio if possible. Defaults to 30"
list_help = "File(s) containing lists of card contents"


@click.group()
def cli():
    """Generate a Cards Against Humanity™ style pdf to be printed and cut into cards.

    The white and black commands are the standard front face content generators, given files that are lists of
    the contents of the cards. The output is written to [input_filename].pdf

    The black command has an option --blank which allows you to normalize all occurrences of underscores to a
    specified length of underscore, or set it to 0 to ignore normalizing.

    The back command prints the back of the cards as a one-page pdf, meant to be printed on the reverse side of the
    cards.

    I have tried to get the hard-coded defaults as close as possible to the normal game cards, except obviously the
    title which is in fact a registered trademark of Cards Against Humanity LLC.
    """


@cli.command()
@click.option("--width", default=2.5, callback=validate_positive, help=width_help)
@click.option("--height", default=3.5, callback=validate_positive, help=height_help)
@click.option("--side-margin", default=10, callback=validate_positive, help=sm_help)
@click.option("--top-margin", default=10, callback=validate_positive, help=tm_help)
@click.option("--title", type=TITLE_TYPE, default="Calling All Heretics", help=title_help)
@click.option("--font-size", default=default_front_fs, callback=validate_positive,
              help=font_size_help.format(default_front_fs))
@click.option("--icon", type=click.Path(exists=True), default="cards.png", help=icon_help)
@click.option("--icon-width", default=30, callback=validate_positive, help=icon_width_help)
@click.argument("lists", nargs=-1, type=click.Path(exists=True))
def white(width, height, side_margin, top_margin, title, font_size, icon, icon_width, lists):
    """Standard white card generator, given files that are lists of the contents of the cards.
    The output is written to [input_filename].pdf"""

    set_style(font_size, True)
    for cards in lists:
        with open(cards) as file:
            cards = process_whites(file)
        write_file(cards, cards + ".pdf", width, height, side_margin, top_margin, title, icon, icon_width)


@cli.command()
@click.option("--blank", default=5, callback=validate_blank, help=blank_help)
@click.option("--width", default=2.5, callback=validate_positive, help=width_help)
@click.option("--height", default=3.5, callback=validate_positive, help=height_help)
@click.option("--side-margin", default=10, callback=validate_positive, help=sm_help)
@click.option("--top-margin", default=10, callback=validate_positive, help=tm_help)
@click.option("--title", type=TITLE_TYPE, default="Calling All Heretics", help=title_help)
@click.option("--font-size", default=default_front_fs, callback=validate_positive,
              help=font_size_help.format(default_front_fs))
@click.option("--icon", type=click.Path(exists=True), default="cards.png", help=icon_help)
@click.option("--icon-width", default=30, callback=validate_positive, help=icon_width_help)
@click.argument("lists", nargs=-1, type=click.Path(exists=True))
def black(blank, width, height, side_margin, top_margin, title, font_size, icon, icon_width, lists):
    """Standard white card generator, given files that are lists of the contents of the cards.
    The output is written to [input_filename].pdf"""

    set_style(font_size, True)
    for cards in lists:
        with open(cards) as file:
            cards = process_blacks(file, blank)
        write_file(cards, cards + ".pdf", width, height, side_margin, top_margin, title, icon, icon_width)


@cli.command()
@click.option("--width", default=2.5, callback=validate_positive, help=width_help)
@click.option("--height", default=3.5, callback=validate_positive, help=height_help)
@click.option("--side-margin", default=10, callback=validate_positive, help=sm_help)
@click.option("--top-margin", default=10, callback=validate_positive, help=tm_help)
@click.option("--title", type=TITLE_TYPE, default="Calling All Heretics", help=title_help)
@click.option("--font-size", default=default_back_fs, callback=validate_positive,
              help=font_size_help.format(default_back_fs))
def back(width, height, side_margin, top_margin, title, font_size):
    """Prints the back of the cards as a one-page pdf, meant to be printed on the reverse side of the cards."""

    set_style(font_size, False)
    write_back(width, height, side_margin, top_margin, title)


if __name__ == "__main__":
    cli()
