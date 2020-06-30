#!/usr/bin/env python
import os
import re
import argparse
import sys
from itertools import zip_longest

HOME = os.getenv('HOME')
config_location = os.getenv('sxhkd_config', f'{HOME}/.config/sxhkd/sxhkdrc')
descriptor = os.getenv('descriptor', '# ')

parser = argparse.ArgumentParser(description='keybind helper - standalone sxhkd configuration parser and keystroke runner')
parser.add_argument('-c', '--config', default=f'{config_location}', help='Configurationfile location')
parser.add_argument('-d', '--descriptor', default=f'{descriptor}', help='comment descriptor')
parser.add_argument('-e', '--exec', default=False, help='execute the passed shortcut')
parser.add_argument('-p', '--print', default='true', action='store_true', help='Print fully unpacked keybind table')
parser.add_argument('-r', '--raw', action='store_true', help='Print the raw configuration')


class sxhkd_helper:
    """ instance helper args and functions """
    def __init__(self, loc, descr):
        self.location = loc
        self.descr = descr
        self.raw_config = self._get_raw_config()
        self.keybinds = [bind for bind in self._parse_keybinds()]


    def _transform_block(self, block):
        """ transform an eligible block of keybind into a list of three elements which is returned for further 
        processing.
        elem 1: comment/declaration of keybind usage
        elem 2: assigned keystrokes
        elem 3: command to execute """
        indent = re.sub(r"\n[\t\s]+", "\n", block)
        trim_trailing_commands = re.sub(r"\\\n", "", indent)
        block_lines = re.split(r'\n', trim_trailing_commands, 2)

        return block_lines


    def _get_raw_config(self):
        """ load configuration from the location defined upon instantiation of class """
        with open(self.location, "r") as cfg:
            data = cfg.read()
        
        self._raw_config = data
        return data


    def _parse_keybinds(self):
        """ take the raw configuration from config and parses all eligible blocks, unchaining keychains and returning
        a list of unpacked commands """
        block_regex = self.descr + r"[\w\s\(\),\-\/&{}]+\n[\w\s+\d{}_\-,;]+\n[\s+\t]+[\w\s\-_$'\\~%{,!.\/\(\)};\"\n]+\n\n"
        eligible_blocks = re.findall(block_regex, self._get_raw_config())
        unchained_lines = list()
        return_keybinds = list()
        for block in eligible_blocks:
            lines = self._transform_block(block)
            unchained_lines = self._unchain_lines(lines)
            to_be_returned = list(zip_longest(*unchained_lines, fillvalue=f'{unchained_lines[0][0]}'))
            for line in to_be_returned:
                return_keybinds.append(line)

        return return_keybinds


    def _unchain_lines(self, lines):
        """ take a transformed block of lines (from ._transform_block), unpacking any keychains, finally
        returning a list containing any unpacked or original lines of keybinds """
        any_chain = False
        return_lines = list()
        lines[0] = lines[0].strip(self.descr)
        lines[2] = lines[2].rstrip()

        for line in lines:
            chain = re.search(r'(?<={).*(?=})', line)
            if chain:
                any_chain = True
                return_lines.append(self._unchain(chain.group(0), line))
            else:
                return_lines.append([line])

        if not any_chain:
            return_lines.append(lines)

        elif any_chain and len(return_lines) == 1:
            exit("A keychain denoting multiple segments was specified for the keybind, but no matching cmdchain exists. Fix your sxhkdrc")

        return return_lines


    def _unchain(self, keys, line):
        """ takes a list of keys or commands and the original line, returning a new list of unpacked keybinds """
        lines = list()

        keys = re.sub(r'\s', '', keys)

        for key in keys.split(','):
            lines.append(self._delim_segment(key, line))
        return lines


    def _delim_segment(self, key, line):
        """ places a delimiter (+, or '') at the previous keychain segment position (start of line, in the middle, end of line OR nothing if the line only contains keychains) """
        if '+' in key:
            key = re.sub(r'\+', '', key)

        pos_in_chain = [r'^{.*}.', r'\s{.*}\s', r'{.*}$', r'^{.*}$']
        delim_in_chain = [f"{key} + ", f" {key} + ", f"{key}", f"{key}"]
        positions = zip(pos_in_chain, delim_in_chain)

        for pos, delim in positions: 
            match = re.search(pos, line)
            if match:
                if '_' in key:  # check for wildcard
                    return re.sub(f'{pos}', ' ', line)
                return re.sub(f'{pos}', fr'{delim}', line)

        return line
    
def print_keybinds(config):
    """ print all parsed and unpacked keybinds to console """
    for bind in config.keybinds:
        original_desc, keybind, original_cmd = bind
        print(f'{original_desc}\t{keybind}\t{original_cmd}'.expandtabs(30))

def execute_cmd(config, keystroke):
    """ run command passed with --exec 'modifier + <character>' """
    import subprocess
    for keybind in config.keybinds:
        # loop through all possible keybinds, finally executing a process if we matched
        cmd = keybind[2]
        keybind = keybind[1]
        if keystroke == keybind:
            subprocess.run([f'{cmd}'], shell=True)

def main(args):
    config = sxhkd_helper(args.config, args.descriptor)

    # only execute if --exec was passed with an actual value
    if bool(args.exec) == True:
        execute_cmd(config, args.exec)

    elif args.raw:
        print(f'Config location: {config.location}')
        print(config.raw_config)

    elif args.print:
        print_keybinds(config)
        

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)