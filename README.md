# keybind helper - standalone sxhkd configuration parser and keybind runner

kbhelper -- Easily discover and execute sxhkd keybindings, inspired by [Hotkey-Helper](https://github.com/Triagle/hotkey-helper)

<gif img here>

# What this is
kbhelper is a python utility that parses `sxhkdhrc`-files for valid blocks of keybinds to create a documented list
associating the description, the keybinding and the action to execute. It can be used in conjunction with rofi/dmenu to have a fuzzy searchable cheatsheet of your configured keybinds.

This program was written using Python 3.8, but should work for most (if not all) Python 3 releases.

# Installation
To set this up inside your $SHELL (make sure that `${HOME}/.local/bin/` is located somewhere within your `$PATH`, or alternatively specify a directory that is in your `$PATH` after -O: `wget [...] -O <directory>/kbhelper.py`):

```sh
$ mkdir -p ${HOME}/.local/bin/
$ wget https://github.com/fiskhest/kbrmenu/src/branch/master/kbhelper.py -O ${HOME}/.local/bin/kbhelper.py
```

# sxhkdrc setup
In order to use the program's functionality, you need to tweak your
`sxhkdrc` to include special comments designed as documentation for
keybindings.

The special syntax for these documentation comments is any line beginning with the value of the variable `descriptor`, which can
be defined with [`--descriptor`, `-d`] or the shell variable `export descriptor='# '`, defaulting to `# ` if none is defined. Set these comments up above every keybinding you wish to document.

```
# Example keybinding with documentation
# Quit bspwm
super + alt + Escape
    bspc quit

# This would show up in the formatted output as:
Quit bspwm                                        super + alt + Escape                              bspc quit
```

Additionally, `{}` can be used to unpack keychains mapping multiple segments of description to keybind and action.
**If the preceeding description does not contain any keychains, all unpacked lines will get the same description.**

```
# Example of segmented documentation
# Move the current window {left,down,up,right}
super + {h,j,k,l}
  bspc node -s {west,south,north,east}

# This would expand in output as:
Move the current window left                      super + h                                         bspc node -s west
Move the current window down                      super + j                                         bspc node -s south
Move the current window up                        super + k                                         bspc node -s north
Move the current window right                     super + l                                         bspc node -s east

# Example of a keychain containing a range
# Focus workspace {1-6}
super + {1-6}
    bspc desktop -f '^{1-6}'

# This would expand in output as:
Focus workspace 1                                 super + 1                                         bspc desktop -f '^1'
Focus workspace 2                                 super + 2                                         bspc desktop -f '^2'
Focus workspace 3                                 super + 3                                         bspc desktop -f '^3'
Focus workspace 4                                 super + 4                                         bspc desktop -f '^4'
Focus workspace 5                                 super + 5                                         bspc desktop -f '^5'
Focus workspace 6                                 super + 6                                         bspc desktop -f '^6'
```

This allows for fast, compact documentation for keybindings of
arbitrary complexity.

# Usage
To use the program, run `kbhelper.py`. This will attempt to parse the configuration stored at the default location with the default descriptor, finally printing back to console (same as `--print`).

```
python kbhelper.py
```

Pass `--help` for a usage table:

```
usage: kbhelper.py [-h] [-f FILE] [-d DESCRIPTOR] [-e EXEC] [-p] [-m] [-r]

keybind helper - sxhkd configuration parser and keystroke runner

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to configuration file
  -d DESCRIPTOR, --descriptor DESCRIPTOR
                        comment descriptor
  -e EXEC, --exec EXEC  execute the passed shortcut
  -p, --print           Print fully unpacked keybind table
  -m, --markdown        Print fully unpacked keybind table in markdown format(for cheatsheets)
  -r, --raw             Print the raw configuration

```

By default, `kbhelper` will look for sxhkdrc in `~/.config/sxhkd/sxhkdrc`, but can be overridden by passing a path to the [`--file`, `-f`] argument or the shell variable `sxhkd_config=$CFGPATH/sxhkdrc`,

```sh
python kbhelper.py -f path/to/sxhkdrc
```

This will print an unpacked table of possible keybinds. passing [--exec,-e] instead executes the action defined for that keystroke (if one was found)

```
Split horizontal                                  super + period                                    bspc node -p east
Split vertical                                    super + minus                                     bspc node -p south
Split cancelation                                 super + comma                                     bspc node -p cancel
Preselect the ratio                               super + ctrl + 1                                  bspc node -o 0.1
Preselect the ratio                               super + ctrl + 2                                  bspc node -o 0.2
Preselect the ratio                               super + ctrl + 3                                  bspc node -o 0.3
Preselect the ratio                               super + ctrl + 4                                  bspc node -o 0.4
Preselect the ratio                               super + ctrl + 5                                  bspc node -o 0.5
Preselect the ratio                               super + ctrl + 6                                  bspc node -o 0.6
Preselect the ratio                               super + ctrl + 7                                  bspc node -o 0.7
Preselect the ratio                               super + ctrl + 8                                  bspc node -o 0.8
Preselect the ratio                               super + ctrl + 9                                  bspc node -o 0.9
Bspwm mode pseudotiled                            super + p                                         bspc node -t
Bspwm mode tiled                                  super + t                                         bspc node -t tiled
Set the node flags marked                         super + ctrl + m                                  bspc node -g marked
Set the node flags locked                         super + ctrl + x                                  bspc node -g locked
Set the node flags sticky                         super + ctrl + y                                  bspc node -g sticky
Set the node flags private                        super + ctrl + z                                  bspc node -g private
Move or swap node to the left (desktop/leaf)      super + shift + h                                 if ! bspc node -s west.local; then bspc node -d prev -f ; fi
Move or swap node to the right (desktop/leaf)     super + shift + l                                 if ! bspc node -s east.local; then bspc node -d next -f ; fi
```

The output is tabulated so that the columns descriptions are neatly aligned and easy to interpret.

This output can be piped to tools such as rofi or dmenu for further processing.

Doing this with a program like rofi allows for powerful searching of
hotkeys on the system.

By running `python kbhelper.py --exec`, you can execute a command associated with a keybinding. For instance, from
the above configuration `super + w` is bound to closing a window. Therefore, executing the following will close a window, as expected:

```sh
python kbhelper.py --exec "super + w"
```

By combining the `--print` flag, and the `--exec` flag, you can create a relatively
powerful system for discovery and remembering your keybindings by
having `kbhelper.py --exec` run the output of the hotkeys searching script from
earlier. A simple bash helper script `kbrmenu` is bundled with this repo, essentially doing the following:

```sh
python kbhelper.py -e "$(python kbhelper.py -p | rofi -p Hotkeys -i -dmenu -width 75 | grep -Po '(?<=\s\s)(?=\S).*(?=\b\s\s)(?!$)')"
```

If you wish to use the bundled `kbrmenu`, installation is as simple as:

```sh
$ wget https://github.com/fiskhest/kbrmenu/src/branch/master/kbrmenu -O ${HOME}/.local/bin/kbrmenu
```

create a bind in your sxhkd-configuration:
```sh
# Display keybind rofi menu
super + b
    ${HOME}/.local/bin/kbrmenu
```
