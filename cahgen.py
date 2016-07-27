from pdf_gen import PackProfile, WhiteCardWriter, BlackCardWriter, CardBackWriter

import click
from configparser import ConfigParser
from os.path import basename, dirname, exists, isdir, join, realpath, splitext
from reportlab.lib.colors import getAllNamedColors, HexColor

hc_defaults = {"blank": 5,
               "width": 2.5,
               "height": 3.5,
               "side_margin": 10,
               "tb_margin": 10,
               "title": "Calling All Heretics",
               "front_fs": 14,
               "back_fs": 35,
               "icon": join(dirname(realpath(__file__)), "cards.png"),
               "icon_width": 30,
               "stripe_color": '',
               "stripe_text": '',
               "output": '.'}
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


def replace_ext(filename, ext):
    return splitext(filename)[0] + '.' + ext


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
    return value


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
help_tbm = "Top and bottom card print margin in pixels. Defaults to {}".format(hc_defaults["tb_margin"])
help_title = "The game title to be printed on the back and the bottom of the front of all the cards. \
Make sure it's an acronym of CAH. Note that the original game phrase is trademarked. \
Defaults to {}".format(hc_defaults["title"])
help_release_title_restrict = "If enabled, will not restrict the title to an acronym of CAH. \
The title will be exactly as given. WARNING it currently does not work. If anyone knows the python click library, \
can you help me out?"
help_font_size = "Font size of the text printed on the {} of the card. \
Does not automatically check whether a huge message will print correctly on the card. Please check your output files. \
Defaults to {}"
help_icon = "Image file to be used as the icon on the front of the card."
help_icon_width = "Pixel width to print the icon on the front of the card. \
Height is scaled to match original ratio if possible. Defaults to {}".format(hc_defaults["icon_width"])
help_stripe_color = "The stripe at the bottom of the card, meant to distinguish various packs. \
Either a standard color, or a hex RGB(a) value if started with '#'. \
Example: `--stripe-color crimson` or `--stripe-color #DC143C` or `--stripe-color #DC143CFF` are all the same. \
If left unset, even with text given, no stripe will be printed."
help_stripe_text = "The text to be printed into the bottom stripe. Always contrasted black or white against the \
stripe color. If a color is given but no text is given, a stripe will still be printed."
help_output = "Output file to write the pdf files. Defaults to {}"
help_contains = "Limit the printed colors to anything containing the given string. \
Remember that this will not be the entire list available. Does not support wildcard at the moment."
help_duplex = "If set then the backs will be written alternating the fronts."
help_is_black = "Print as black cards"


@click.group()
def cli():
    """Generate a Cards Against Humanity™ style pdf to be printed and cut into cards.

    The white and black commands are the standard card generators, either front face only or alternating
    duplex, given files that are lists of the contents of the cards. The output is written to
    [current_directory]/[white or black].pdf and will replace any preexisting file. If the --output option
    is supplied, the file will be written to that file instead.

    The black command has an option --blank which allows you to normalize all occurrences of underscores to a
    specified length of underscore, or set it to 0 to ignore normalizing.

    The back command prints the back of the cards as a one-page pdf, meant to be printed on the reverse side of the
    cards.

    The back of the cards has the option to be printed with a pack profile, meaning the bottom margin of the card
    will be printed with a colored stripe and appropriately contrasted text, making pack sorting and separating
    at the end of a game simple. The colors available for this can be shown with the listcolors command. When
    loading files with the white or black command, the writer will attempt to load a profile from an adjacent .pp
    file for each file. If no .pp file exists, or no color is given, to stripe will be printed.

    I have tried to get the hard-coded defaults as close as possible to the normal game cards, except obviously the
    title which is in fact a registered trademark of Cards Against Humanity LLC.
    """


@cli.command(short_help="process white card lists")
@click.option("--width", default=loaded_defaults["width"], callback=validate_positive, help=help_width)
@click.option("--height", default=loaded_defaults["height"], callback=validate_positive, help=help_height)
@click.option("--side-margin", default=loaded_defaults["side_margin"], callback=validate_positive, help=help_sm)
@click.option("--tb-margin", default=loaded_defaults["tb_margin"], callback=validate_positive, help=help_tbm)
@click.option("--title", type=TITLE_TYPE, default=loaded_defaults["title"], help=help_title)
@click.option("--release-title-restrict", is_flag=True, help=help_release_title_restrict)
@click.option("--front_fs", default=loaded_defaults["front_fs"], callback=validate_positive,
              help=help_font_size.format("front", hc_defaults["front_fs"]))
@click.option("--back_fs", default=loaded_defaults["back_fs"], callback=validate_positive,
              help=help_font_size.format("back", hc_defaults["back_fs"]))
@click.option("--icon", type=click.Path(exists=True), default=loaded_defaults["icon"], help=help_icon)
@click.option("--icon-width", default=loaded_defaults["icon_width"], callback=validate_positive, help=help_icon_width)
@click.option("--output", type=click.Path(), default=loaded_defaults["output"], callback=validate_output,
              help=help_output.format(join(hc_defaults["output"], "white.pdf")))
@click.option("--duplex", is_flag=True, help=help_duplex)
@click.argument("lists", nargs=-1, type=click.File())
def white(width, height, side_margin, tb_margin, title, release_title_restrict,
          front_fs, back_fs, icon, icon_width, output, duplex, lists):
    """Standard white card generator, given files that are lists of the contents of the cards, ignoring .pp files.
    Writes to white.pdf, in the --output directory if supplied or current directory otherwise, and will replace
    any preexisting file."""

    output = join(output if output else '.', "white.pdf")
    writer = WhiteCardWriter(output, width, height, side_margin, tb_margin, front_fs, back_fs,
                             title, icon, icon_width, duplex)
    for file in lists:
        if splitext(file.name)[1] == ".pp":
            continue
        writer.add_pack(file, replace_ext(file.name, "pp"))
    writer.write()


@cli.command(short_help="process black card lists")
@click.option("--blank", default=loaded_defaults["blank"], callback=validate_blank, help=help_blank)
@click.option("--width", default=loaded_defaults["width"], callback=validate_positive, help=help_width)
@click.option("--height", default=loaded_defaults["height"], callback=validate_positive, help=help_height)
@click.option("--side-margin", default=loaded_defaults["side_margin"], callback=validate_positive, help=help_sm)
@click.option("--tb-margin", default=loaded_defaults["tb_margin"], callback=validate_positive, help=help_tbm)
@click.option("--title", type=TITLE_TYPE, default=loaded_defaults["title"], help=help_title)
@click.option("--release-title-restrict", is_flag=True, help=help_release_title_restrict)
@click.option("--front_fs", default=loaded_defaults["front_fs"], callback=validate_positive,
              help=help_font_size.format("front", hc_defaults["front_fs"]))
@click.option("--back_fs", default=loaded_defaults["back_fs"], callback=validate_positive,
              help=help_font_size.format("back", hc_defaults["back_fs"]))
@click.option("--icon", type=click.Path(exists=True), default=loaded_defaults["icon"], help=help_icon)
@click.option("--icon-width", default=loaded_defaults["icon_width"], callback=validate_positive, help=help_icon_width)
@click.option("--output", type=click.Path(), default=loaded_defaults["output"], callback=validate_output,
              help=help_output.format(join(hc_defaults["output"], "black.pdf")))
@click.option("--duplex", is_flag=True, help=help_duplex)
@click.argument("lists", nargs=-1, type=click.File())
def black(blank, width, height, side_margin, tb_margin, title, release_title_restrict,
          front_fs, back_fs, icon, icon_width, output, duplex, lists):
    """Standard black card generator, given files that are lists of the contents of the cards, ignoring .pp files.
    Writes to black.pdf, in the --output directory if supplied or current directory otherwise, and will replace
    any preexisting file."""

    output = join(output if output else '.', "black.pdf")
    writer = BlackCardWriter(output, width, height, side_margin, tb_margin, front_fs, back_fs,
                             title, icon, icon_width, duplex, blank)
    for file in lists:
        if splitext(file.name)[1] == ".pp":
            continue
        writer.add_pack(file, replace_ext(file.name, "pp"))
    writer.write()


@cli.command(short_help="print single page of card backs")
@click.option("--width", default=loaded_defaults["width"], callback=validate_positive, help=help_width)
@click.option("--height", default=loaded_defaults["height"], callback=validate_positive, help=help_height)
@click.option("--side-margin", default=loaded_defaults["side_margin"], callback=validate_positive, help=help_sm)
@click.option("--tb-margin", default=loaded_defaults["tb_margin"], callback=validate_positive, help=help_tbm)
@click.option("--title", type=TITLE_TYPE, default=loaded_defaults["title"], help=help_title)
@click.option("--release-title-restrict", is_flag=True, help=help_release_title_restrict)
@click.option("--font-size", default=loaded_defaults["back_fs"], callback=validate_positive,
              help=help_font_size.format("back", hc_defaults["back_fs"]))
@click.option("--stripe-color", default=loaded_defaults["stripe_color"], callback=validate_stripe_color,
              help=help_stripe_color)
@click.option("--stripe-text", default=loaded_defaults["stripe_text"], help=help_stripe_text)
@click.option("--output", type=click.Path(), default=loaded_defaults["output"],
              help=help_output.format(join(hc_defaults["output"], "back.pdf")))
@click.option("--is-black", is_flag=True)
def back(width, height, side_margin, tb_margin, title, release_title_restrict, font_size,
         stripe_color, stripe_text, output, is_black):
    """Prints the back of the cards as a one-page pdf, meant to be printed on the reverse side of the cards.
    Writes to back.pdf, in the --output directory if supplied or current directory otherwise. Still useful
    with the duplex option of the blacks/whites, as it gives you a preview of the back"""

    profile = PackProfile(stripe_text, stripe_color) if stripe_color else None
    output = join(output if output else '.', "back.pdf")
    CardBackWriter(output, width, height, side_margin, tb_margin, font_size, title, profile, is_black)


@cli.command(short_help="Write standard config file for editing")
@click.option("--defaults", is_flag=True, help="If given, will only write other configs if their flag is also given")
@click.option("--profile", is_flag=True)
def cfg(defaults, profile):
    """Writes a sample profile config to 'sample.pp', and all the hardcoded defaults to the config file for
    easy editing. No more scurrying for obscure config API listings! This creates a simple editable file to
    be read right back into the program! Holy easy customizing Batman!! Watch that the icon parameter will
    probably not work out of the box.

    If any flag is given, the other configs will only be written if their flag is also given."""

    if all(not flag for flag in (defaults, profile)):  # no flag given, write all
        defaults = True
        profile = True

    if defaults:
        config = ConfigParser()
        config["DEFAULTS"] = {k: str(v) for k, v in hc_defaults.items() if k != "icon"}
        config["DEFAULTS"]["icon"] = basename(hc_defaults["icon"])
        with open(default_config_fn, mode="w") as file:
            config.write(file)

    if profile:
        PackProfile.write_sample("sample.pp")


@cli.command(short_help="List all available named colors")
@click.option("--contains", default='', help=help_contains)
def listcolors(contains):
    """List all the colors available to use in the --stripe-color option of the `back` command"""

    color_names = PackProfile.available_colors(contains)

    if color_names:
        length = len(max(color_names, key=len)) + 3  # max length color name + column gap of 5
        n_columns = 3
        column_len, add_one = divmod(len(color_names), n_columns)
        if add_one:
            column_len += 1
        columns_list = []
        for i in range(0, len(color_names), column_len):
            column = [color.ljust(length, ' ') for color in color_names[i:i+column_len]]
            if len(column) != column_len:
                column.append('')
            columns_list.append(column)
        columns_list[-1] = [color.rstrip() for color in columns_list[-1]]
        for row in zip(*columns_list):
            for color in row:
                click.secho(color, color=color.strip(), nl=False)
            click.echo()


@cli.command(short_help="Run the windowed program")
def gui():
    """Start the gui of the program for more advanced handling of files.

    UNDER CONSTRUCTION: CURRENTLY DOES NOTHING. NOTHING AT ALL. TURN AROUND.
    GO SOMEWHERE ELSE."""
    # run()


if __name__ == "__main__":
    cli()
