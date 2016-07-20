from pdf_gen import set_style, process_blacks, process_whites, write_file, write_back

import click
from configparser import ConfigParser
from os.path import basename, dirname, exists, isdir, join, splitext

hc_defaults = [5,                       # blank
               2.5,                     # width
               3.5,                     # height
               10,                      # side_margin
               10,                      # top_margin
               "Calling All Heretics",  # title
               14,                      # front_fs
               35,                      # back_fs
               "cards.png",             # icon
               30,                      # icon_width
               '']                      # output


def load_defaults():
    blank, width, height, side_margin, top_margin, title, front_fs, back_fs, icon, icon_width, output = hc_defaults

    config = ConfigParser()
    config.read("cli.cfg")
    if "DEFAULTS" in config:
        defaults = config["DEFAULTS"]
        blank = int(defaults.get("blank", repr(blank)))
        width = float(defaults.get("width", repr(width)))
        height = float(defaults.get("height", repr(height)))
        side_margin = int(defaults.get("side_margin", repr(side_margin)))
        top_margin = int(defaults.get("top_margin", repr(top_margin)))
        title = defaults.get("title", title)
        front_fs = int(defaults.get("front_fs", repr(front_fs)))
        back_fs = int(defaults.get("back_fs", repr(back_fs)))
        icon = defaults.get("icon", icon)
        icon_width = int(defaults.get("icon_width", repr(icon_width)))
        output = defaults.get("output", output)

    return blank, width, height, side_margin, top_margin, title, \
        front_fs, back_fs, icon, icon_width, output


def validate_output(ctx, param, value):
    if value == '':
        return value
    if exists(value):
        if isdir(value):
            return value
        else:
            raise click.BadParameter(repr(value) + " already exists and is not a directory")
    else:
        raise click.BadParameter(repr(value) + " does not exist")


def validate_positive(ctx, param, value):
    if value <= 0:
        raise click.BadParameter(param.name + " needs to be at positive number")
    return value


def validate_blank(ctx, param, value):
    if value <= 0:
        raise click.BadParameter(param.name + " needs to be at least 0")
    return "_" * value


class TitleType(click.ParamType):
    name = "title"

    def convert(self, value, param, ctx):
        # FIXME when it's actually checking a title with --release-title-restrict enabled, ctx.params is empty. WTF
        if "release_title_restrict" in ctx.params and ctx.params["release_title_restrict"]:
            return value
        value = value.strip()
        if [i[0] for i in value.split()] == ['C', 'A', 'H']:
            return value
        else:
            self.fail(repr(value) + " is not a valid title. Please have it be an acronym of CAH")


TITLE_TYPE = TitleType()

default_blank, default_width, default_height, default_side_margin, default_top_margin, default_title, \
    default_front_fs, default_back_fs, default_icon, default_icon_width, default_output = load_defaults()

blank_help = "Number of underscores to normalize the size of the blank spaces to in the black cards. \
Meant to prevent you from pulling your hair out making sure all the blank marks are the same. Defaults to {}. \
If set to 0, no normalizing will be done".format(hc_defaults[0])
width_help = "Width of each card in inches. Defaults to {}".format(hc_defaults[1])
height_help = "Height of each card in inches. Defaults to {}".format(hc_defaults[2])
sm_help = "Left and right card print margin in pixels. Defaults to {}".format(hc_defaults[3])
tm_help = "Top and bottom card print margin in pixels. Defaults to {}".format(hc_defaults[4])
title_help = "The game title to be printed on the back and the bottom of the front of all the cards. \
Make sure it's an acronym of CAH. Note that the original game phrase is trademarked. \
Defaults to {}".format(hc_defaults[5])
release_title_restrict_help = "If enabled, will not restrict the title to an acronym of CAH. \
The title will be exactly as given. WARNING it currently does not work. If anyone knows the python click library, \
can you help me out?"
font_size_help = "Font size of the text printed on the card. \
Does not automatically check whether a huge message will print correctly on the card. Please check your output files. \
Defaults to {}"
icon_help = "Image file to be used as the icon on the front of the card. Defaults to {}".format(hc_defaults[8])
icon_width_help = "Pixel width to print the icon on the front of the card. \
Height is scaled to match original ratio if possible. Defaults to {}".format(hc_defaults[9])
output_help = "Output directory to write the pdf files. Defaults to {} directory"


@click.group()
def cli():
    """Generate a Cards Against Humanity™ style pdf to be printed and cut into cards.

    The white and black commands are the standard front face content generators, given files that are lists of the
    contents of the cards. The output is written to [input_filename].pdf and will replace any preexisting file.
    If the --output option is supplied, the file will be written to that directory, instead of the same as the input
    files.

    The black command has an option --blank which allows you to normalize all occurrences of underscores to a
    specified length of underscore, or set it to 0 to ignore normalizing.

    The back command prints the back of the cards as a one-page pdf, meant to be printed on the reverse side of the
    cards.

    I have tried to get the hard-coded defaults as close as possible to the normal game cards, except obviously the
    title which is in fact a registered trademark of Cards Against Humanity LLC.
    """


@cli.command(short_help="process white card lists")
@click.option("--width", default=default_width, callback=validate_positive, help=width_help)
@click.option("--height", default=default_height, callback=validate_positive, help=height_help)
@click.option("--side-margin", default=default_side_margin, callback=validate_positive, help=sm_help)
@click.option("--top-margin", default=default_top_margin, callback=validate_positive, help=tm_help)
@click.option("--title", type=TITLE_TYPE, default=default_title, help=title_help)
@click.option("--release-title-restrict", is_flag=True, help=release_title_restrict_help)
@click.option("--font-size", default=default_front_fs, callback=validate_positive,
              help=font_size_help.format(hc_defaults[6]))
@click.option("--icon", type=click.Path(exists=True), default=default_icon, help=icon_help)
@click.option("--icon-width", default=default_icon_width, callback=validate_positive, help=icon_width_help)
@click.option("--output", type=click.Path(), default=default_output, callback=validate_output,
              help=output_help.format("the same"))
@click.argument("lists", nargs=-1, type=click.File())
def white(width, height, side_margin, top_margin, title, release_title_restrict,
          font_size, icon, icon_width, output, lists):
    """Standard white card generator, given files that are lists of the contents of the cards.
    The output is written to [input_filename].pdf and will replace any preexisting file.
    If the --output option is supplied, the file will be written to that directory, instead of the same as the input
    files."""

    set_style(font_size, True)
    for file in lists:
        cards = process_whites(file.readlines())
        output = join(output if output else dirname(file.name), splitext(basename(file.name))[0] + ".pdf")
        write_file(cards, output, width, height, side_margin, top_margin, title, icon, icon_width)


@cli.command(short_help="process black card lists")
@click.option("--blank", default=default_blank, callback=validate_blank, help=blank_help)
@click.option("--width", default=default_width, callback=validate_positive, help=width_help)
@click.option("--height", default=default_height, callback=validate_positive, help=height_help)
@click.option("--side-margin", default=default_side_margin, callback=validate_positive, help=sm_help)
@click.option("--top-margin", default=default_top_margin, callback=validate_positive, help=tm_help)
@click.option("--title", type=TITLE_TYPE, default=default_title, help=title_help)
@click.option("--release-title-restrict", is_flag=True, help=release_title_restrict_help)
@click.option("--font-size", default=default_front_fs, callback=validate_positive,
              help=font_size_help.format(hc_defaults[6]))
@click.option("--icon", type=click.Path(exists=True), default=default_icon, help=icon_help)
@click.option("--icon-width", default=default_icon_width, callback=validate_positive, help=icon_width_help)
@click.option("--output", type=click.Path(), default=default_output, callback=validate_output,
              help=output_help.format("the same"))
@click.argument("lists", nargs=-1, type=click.File())
def black(blank, width, height, side_margin, top_margin, title, release_title_restrict,
          font_size, icon, icon_width, output, lists):
    """Standard black card generator, given files that are lists of the contents of the cards.
    The output is written to [input_filename].pdf and will replace any preexisting file.
    If the --output option is supplied, the file will be written to that directory, instead of the same as the input
    files."""

    set_style(font_size, True)
    for file in lists:
        output = join(output if output else dirname(file.name), splitext(basename(file.name))[0] + ".pdf")
        cards = process_blacks(file.readlines(), blank)
        write_file(cards, output, width, height, side_margin, top_margin, title, icon, icon_width)


@cli.command(short_help="print single page of card backs")
@click.option("--width", default=default_width, callback=validate_positive, help=width_help)
@click.option("--height", default=default_height, callback=validate_positive, help=height_help)
@click.option("--side-margin", default=default_side_margin, callback=validate_positive, help=sm_help)
@click.option("--top-margin", default=default_top_margin, callback=validate_positive, help=tm_help)
@click.option("--title", type=TITLE_TYPE, default=default_title, help=title_help)
@click.option("--release-title-restrict", is_flag=True, help=release_title_restrict_help)
@click.option("--font-size", default=default_back_fs, callback=validate_positive,
              help=font_size_help.format(hc_defaults[7]))
@click.option("--output", type=click.Path(), default=default_output, callback=validate_output,
              help=output_help.format("current"))
def back(width, height, side_margin, top_margin, title, release_title_restrict, font_size, output):
    """Prints the back of the cards as a one-page pdf, meant to be printed on the reverse side of the cards.
    Writes to back.pdf, in the --output directory if supplied or current directory otherwise"""

    set_style(font_size, False)
    output = join(output if output else "./", "back.pdf")
    write_back(output, width, height, side_margin, top_margin, title)


if __name__ == "__main__":
    cli()
