## What the heck is this

A PDF generator for custom cards of everyone's favorite horrible person game, Cards Against Humanity™. Nearly fully customizable, including card size, font size, and game title.

## Usage

Typing `python cahgen.py` yields:

```
Usage: cahgen.py [OPTIONS] COMMAND [ARGS]...

  Generate a Cards Against Humanity™ style pdf to be printed and cut into
  cards.

  The white and black commands are the standard front face content
  generators, given files that are lists of the contents of the cards. The
  output is written to [input_filename].pdf and will replace any preexisting
  file. If the --output option is supplied, the file will be written to that
  directory, instead of the same as the input files.

  The black command has an option --blank which allows you to normalize all
  occurrences of underscores to a specified length of underscore, or set it
  to 0 to ignore normalizing.

  The back command prints the back of the cards as a one-page pdf, meant to
  be printed on the reverse side of the cards.

  I have tried to get the hard-coded defaults as close as possible to the
  normal game cards, except obviously the title which is in fact a
  registered trademark of Cards Against Humanity LLC.

Options:
  --help  Show this message and exit.

Commands:
  back   print single page of card backs
  black  process black card lists
  white  process white card lists
```

And each command has its own help with options. Example:

```
$ python cahgen.py white --help
Usage: cahgen.py white [OPTIONS] [LISTS]...

  Standard white card generator, given files that are lists of the contents
  of the cards. The output is written to [input_filename].pdf and will
  replace any preexisting file. If the --output option is supplied, the file
  will be written to that directory, instead of the same as the input files.

Options:
  --width FLOAT             Width of each card in inches. Defaults to 2.5
  --height FLOAT            Height of each card in inches. Defaults to 3.5
  --side-margin INTEGER     Left and right card print margin in pixels.
                            Defaults to 10
  --top-margin INTEGER      Top and bottom card print margin in pixels.
                            Defaults to 10
  --title TITLE             The game title to be printed on the back and the
                            bottom of the front of all the cards. Make sure
                            it's an acronym of CAH. Note that the original
                            game phrase is trademarked. Defaults to Calling
                            All Heretics
  --release-title-restrict  If enabled, will not restrict the title to an
                            acronym of CAH. The title will be exactly as
                            given. WARNING it currently does not work. If
                            anyone knows the python click library, can you
                            help me out?
  --font-size INTEGER       Font size of the text printed on the card. Does
                            not automatically check whether a huge message
                            will print correctly on the card. Please check
                            your output files. Defaults to 14
  --icon PATH               Image file to be used as the icon on the front of
                            the card. Defaults to cards.png
  --icon-width INTEGER      Pixel width to print the icon on the front of the
                            card. Height is scaled to match original ratio if
                            possible. Defaults to 30
  --output PATH             Output directory to write the pdf files. Defaults
                            to the same directory
  --help                    Show this message and exit.
```

There are example inputs and default outputs in `cards/`

Don't be afraid to poke around, you're not gonna break anything. I've put plenty of safety nets in for that.

If you do encounter a python error, that should not have happened at all and please share with me via the Feedback section below what happened.

## Motivation

I've wanted this game for a long time, but I didn't want to stick with just the standard deck and expansions, but I didn't want to write in my own by hand either. And the PDFs on the main website make cards that are slightly larger than your thumbnail, which are unusable.

## Installation

Requires Python 3.x and the `click` and `reportlab` python libraries. Currently this code is only available by cloning this repository, soon I will deploy this properly. I'm not paid, so it happens as I learn it.

## Feedback

If the code broke on you, or if it does something you believe is unintended, or if you'd like to help at all, contact me at:
* Twitter: [@hamstap85](https://twitter.com/hamstap85)

Sorry that's it for now, I don't even have any issue trackers running. This is literally my first publicly submitted software.

## License

GLP-3.0