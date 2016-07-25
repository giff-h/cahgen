from pdf_gen import old_set_style, old_process_blacks, old_process_whites, old_write_file, old_write_back
from gui import run

import click
from configparser import ConfigParser
from os.path import basename, dirname, exists, isdir, join, realpath, splitext
from reportlab.lib.colors import getAllNamedColors, HexColor

hc_defaults = {"blank": 5,
               "width": 2.5,
               "height": 3.5,
               "side_margin": 10,
               "top_margin": 10,
               "title": "Calling All Heretics",
               "front_fs": 14,
               "back_fs": 35,
               "icon": join(dirname(realpath(__file__)), "cards.png"),
               "icon_width": 30,
               "stripe_color": '',
               "stripe_text": '',
               "output": ''}
colors = getAllNamedColors()
default_config_fn = "cahgen.cfg"
loaded_defaults = dict()


def load_defaults(loaded, config_fn=default_config_fn):
    config = ConfigParser()
    config.read(config_fn)
    if "DEFAULTS" in config:
        defaults = config["DEFAULTS"]
        for param in hc_defaults.keys():
            param_type = type(hc_defaults[param])
            loaded[param] = param_type(defaults.get(param, hc_defaults[param]))
    else:
        for k, v in hc_defaults.items():
            loaded[k] = v


def validate_stripe_color(ctx, param, value):
    if value == '':
        return None
    if value.startswith('#'):
        try:
            color = HexColor(value)
        except ValueError:
            raise click.BadParameter(repr(value) + " is an invalid hex color value")
    else:
        if value in colors:
            color = colors[value]
        else:
            raise click.BadParameter(repr(value) + " is not a known color")

    return color


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
load_defaults(loaded_defaults)

help_blank = "Number of underscores to normalize the size of the blank spaces to in the black cards. \
Meant to prevent you from pulling your hair out making sure all the blank marks are the same. Defaults to {}. \
If set to 0, no normalizing will be done.".format(hc_defaults["blank"])
help_width = "Width of each card in inches. Defaults to {}".format(hc_defaults["width"])
help_height = "Height of each card in inches. Defaults to {}".format(hc_defaults["height"])
help_sm = "Left and right card print margin in pixels. Defaults to {}".format(hc_defaults["side_margin"])
help_tm = "Top and bottom card print margin in pixels. Defaults to {}".format(hc_defaults["top_margin"])
help_title = "The game title to be printed on the back and the bottom of the front of all the cards. \
Make sure it's an acronym of CAH. Note that the original game phrase is trademarked. \
Defaults to {}".format(hc_defaults["title"])
help_release_title_restrict = "If enabled, will not restrict the title to an acronym of CAH. \
The title will be exactly as given. WARNING it currently does not work. If anyone knows the python click library, \
can you help me out?"
help_font_size = "Font size of the text printed on the card. \
Does not automatically check whether a huge message will print correctly on the card. Please check your output files. \
Defaults to {}"
help_icon = "Image file to be used as the icon on the front of the card."
help_icon_width = "Pixel width to print the icon on the front of the card. \
Height is scaled to match original ratio if possible. Defaults to {}".format(hc_defaults["icon_width"])
help_stripe_color = "The stripe at the bottom of the card, meant to distinguish various packs. \
Either a standard color, or a hex RGB(a) value if started with '#'. \
Example: `--stripe-color crimson` or `--stripe-color #DC143C` or `--stripe-color #DC143CFF` are all the same. \
If left unset, even with text given, no stripe will be printed."
help_stripe_text = "The stripe at the bottom of the card, meant to distinguish various packs. \
The text to be printed into the stripe. Always black. If a color is given but no text is given, \
a stripe will still be printed."
help_output = "Output {} to write the pdf files. Defaults to {}"
help_contains = "Limit the printed colors to anything containing the given string. \
Remember that this will not be the entire list available. Does not support wildcard at the moment."
help_duplex = "If set then the backs will be written alternating the fronts. \
The options that would be fed to the back command must be given using the config file."


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
@click.option("--width", default=loaded_defaults["width"], callback=validate_positive, help=help_width)
@click.option("--height", default=loaded_defaults["height"], callback=validate_positive, help=help_height)
@click.option("--side-margin", default=loaded_defaults["side_margin"], callback=validate_positive, help=help_sm)
@click.option("--top-margin", default=loaded_defaults["top_margin"], callback=validate_positive, help=help_tm)
@click.option("--title", type=TITLE_TYPE, default=loaded_defaults["title"], help=help_title)
@click.option("--release-title-restrict", is_flag=True, help=help_release_title_restrict)
@click.option("--font-size", default=loaded_defaults["front_fs"], callback=validate_positive,
              help=help_font_size.format(hc_defaults["front_fs"]))
@click.option("--icon", type=click.Path(exists=True), default=loaded_defaults["icon"], help=help_icon)
@click.option("--icon-width", default=loaded_defaults["icon_width"], callback=validate_positive, help=help_icon_width)
@click.option("--output", type=click.Path(), default=loaded_defaults["output"], callback=validate_output,
              help=help_output.format("directory", "the same directory"))
@click.option("--duplex", is_flag=True, help=help_duplex)
@click.argument("lists", nargs=-1, type=click.File())
def white(width, height, side_margin, top_margin, title, release_title_restrict,
          font_size, icon, icon_width, output, duplex, lists):
    """Standard white card generator, given files that are lists of the contents of the cards.
    The output is written to [input_filename].pdf and will replace any preexisting file.
    If the --output option is supplied, the file will be written to that directory, instead of the same as the input
    files."""

    old_set_style(font_size, True)
    if duplex:
        old_set_style(loaded_defaults["back_fs"], False)
        stripe_color = validate_stripe_color(None, None, loaded_defaults["stripe_color"])
        stripe_text = loaded_defaults["stripe_text"]
    else:
        stripe_color = None
        stripe_text = ''
    for file in lists:
        output_file = join(output if output else dirname(file.name), splitext(basename(file.name))[0] + ".pdf")
        cards = old_process_whites(file.readlines())
        old_write_file(cards, output_file, width, height, side_margin, top_margin, title, icon, icon_width,
                       stripe_color, stripe_text, duplex)


@cli.command(short_help="process black card lists")
@click.option("--blank", default=loaded_defaults["blank"], callback=validate_blank, help=help_blank)
@click.option("--width", default=loaded_defaults["width"], callback=validate_positive, help=help_width)
@click.option("--height", default=loaded_defaults["height"], callback=validate_positive, help=help_height)
@click.option("--side-margin", default=loaded_defaults["side_margin"], callback=validate_positive, help=help_sm)
@click.option("--top-margin", default=loaded_defaults["top_margin"], callback=validate_positive, help=help_tm)
@click.option("--title", type=TITLE_TYPE, default=loaded_defaults["title"], help=help_title)
@click.option("--release-title-restrict", is_flag=True, help=help_release_title_restrict)
@click.option("--font-size", default=loaded_defaults["front_fs"], callback=validate_positive,
              help=help_font_size.format(hc_defaults["front_fs"]))
@click.option("--icon", type=click.Path(exists=True), default=loaded_defaults["icon"], help=help_icon)
@click.option("--icon-width", default=loaded_defaults["icon_width"], callback=validate_positive, help=help_icon_width)
@click.option("--output", type=click.Path(), default=loaded_defaults["output"], callback=validate_output,
              help=help_output.format("directory", "the same directory"))
@click.option("--duplex", is_flag=True, help=help_duplex)
@click.argument("lists", nargs=-1, type=click.File())
def black(blank, width, height, side_margin, top_margin, title, release_title_restrict,
          font_size, icon, icon_width, output, duplex, lists):
    """Standard black card generator, given files that are lists of the contents of the cards.
    The output is written to [input_filename].pdf and will replace any preexisting file.
    If the --output option is supplied, the file will be written to that directory, instead of the same as the input
    files."""

    old_set_style(font_size, True)
    if duplex:
        old_set_style(loaded_defaults["back_fs"], False)
        stripe_color = validate_stripe_color(None, None, loaded_defaults["stripe_color"])
        stripe_text = loaded_defaults["stripe_text"]
    else:
        stripe_color = None
        stripe_text = ''
    for file in lists:
        output_file = join(output if output else dirname(file.name), splitext(basename(file.name))[0] + ".pdf")
        cards = old_process_blacks(file.readlines(), blank)
        old_write_file(cards, output_file, width, height, side_margin, top_margin, title, icon, icon_width,
                       stripe_color, stripe_text, duplex)


@cli.command(short_help="print single page of card backs")
@click.option("--width", default=loaded_defaults["width"], callback=validate_positive, help=help_width)
@click.option("--height", default=loaded_defaults["height"], callback=validate_positive, help=help_height)
@click.option("--side-margin", default=loaded_defaults["side_margin"], callback=validate_positive, help=help_sm)
@click.option("--top-margin", default=loaded_defaults["top_margin"], callback=validate_positive, help=help_tm)
@click.option("--title", type=TITLE_TYPE, default=loaded_defaults["title"], help=help_title)
@click.option("--release-title-restrict", is_flag=True, help=help_release_title_restrict)
@click.option("--font-size", default=loaded_defaults["back_fs"], callback=validate_positive,
              help=help_font_size.format(hc_defaults["back_fs"]))
@click.option("--stripe-color", default=loaded_defaults["stripe_color"], callback=validate_stripe_color,
              help=help_stripe_color)
@click.option("--stripe-text", default=loaded_defaults["stripe_text"], help=help_stripe_text)
@click.option("--output", type=click.Path(), default=loaded_defaults["output"],
              help=help_output.format("file", "./back.pdf"))
def back(width, height, side_margin, top_margin, title, release_title_restrict, font_size,
         stripe_color, stripe_text, output):
    """Prints the back of the cards as a one-page pdf, meant to be printed on the reverse side of the cards.
    Writes to back.pdf, in the --output directory if supplied or current directory otherwise. Still useful
    with the duplex option of the blacks/whites, as it gives you a preview of the back"""

    old_set_style(font_size, False)
    if not output:
        output = join('.', "back.pdf")
    old_write_back(output, width, height, side_margin, top_margin, title, stripe_color, stripe_text)


@cli.command(short_help="Write standard config file for editing")
def cfg():
    """Writes all the hardcoded defaults to the config file for easy editing. No more scurrying for obscure
    config API listings! This creates a simple editable file to be read right back into the program! Holy easy
    customizing Batman!!"""

    config = ConfigParser()
    config["DEFAULTS"] = {k: str(v) for k, v in hc_defaults.items() if k != "icon"}
    config["DEFAULTS"]["icon"] = basename(hc_defaults["icon"])
    with open(default_config_fn, mode="w") as file:
        config.write(file)


@cli.command(short_help="List all available named colors")
@click.option("--contains", default='', help=help_contains)
def listcolors(contains):
    """List all the colors available to use in the --stripe-color option of the `back` command"""

    color_names = sorted(color for color in colors.keys() if contains in color)
    if color_names:
        length = len(max(color_names, key=len)) + 3  # max length color name + column gap of 5
        columns = 3
        column_len, add_one = divmod(len(color_names), columns)
        if add_one:
            column_len += 1
        columns_list = []
        for i in range(0, len(color_names), column_len):
            column = [color.ljust(length, ' ') for color in color_names[i:i+column_len]]
            if len(column) != column_len:
                column.append('')
            columns_list.append(column)
        for row in zip(*columns_list):
            click.echo(''.join(row))


@cli.command(short_help="Run the windowed program")
def gui():
    """Start the gui of the program for more advanced handling of files"""
    run()


if __name__ == "__main__":
    cli()
