# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2011, 2012 Andrej A Antonov <polymorphm@qmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

assert str is not bytes

import argparse

class UserError(Exception):
    pass

def main():
    parser = argparse.ArgumentParser(
            description='Utility for massive sendmail')
    
    parser.add_argument(
            'cfg', nargs='+',
            help='Path to config file')
    
    args = parser.parse_args()
    
    from os.path import join, dirname
    from .mass_sendmail import mass_sendmail
    
    for cfg in args.cfg:
        from configparser import ConfigParser
        from configparser import DEFAULTSECT
        
        config = ConfigParser()
        config.read(cfg, encoding='utf-8')
        
        mass_sendmail(
            join(dirname(cfg), config.get(
                    DEFAULTSECT, 'to-addr-list-file', fallback='to-addr-list.txt')),
            config.get(DEFAULTSECT, 'subject'),
            config.get(DEFAULTSECT, 'text'),
            use_to_addr_list_shuffle=config.getboolean(
                    DEFAULTSECT, 'use-to-addr-list-shuffle', fallback=None),
            real_from_addr=config.get(
                    DEFAULTSECT, 'real-from-addr', fallback=None),
            from_name=config.get(
                    DEFAULTSECT, 'from-name', fallback=None),
            from_addr=config.get(
                    DEFAULTSECT, 'from-addr', fallback=None),
            attachments=tuple(map(
                lambda path: join(dirname(cfg), path),
                filter(None, map(lambda x: x.strip(),
                        config.get(DEFAULTSECT, 'attachments', fallback='').split(':')))
            )),
            force_delay=config.getfloat(
                    DEFAULTSECT, 'force-delay', fallback=None),
        )
