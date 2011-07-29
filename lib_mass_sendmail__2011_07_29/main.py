# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2011 Andrej A Antonov <polymorphm@qmail.com>
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

class UserError(Exception):
    pass

def main():
    from sys import argv
    
    if len(argv) >= 2:
        from os.path import join, dirname
        from .mass_sendmail import mass_sendmail
        
        for arg in argv[1:]:
            from configparser import ConfigParser
            from configparser import DEFAULTSECT
            
            config = ConfigParser()
            config.read(arg, encoding='utf-8')
            
            mass_sendmail(
                join(dirname(arg), config.get(
                        DEFAULTSECT, 'to-addr-list-file', fallback='to-addr-list.txt')),
                config.get(DEFAULTSECT, 'subject'),
                config.get(DEFAULTSECT, 'text'),
                use_to_addr_list_shuffle=config.getboolean(
                        DEFAULTSECT, 'use-to-addr-list-shuffle', fallback=None),
                real_from_addr=config.get(
                        DEFAULTSECT, 'real-from-addr', fallback=None),
                from_addr=config.get(
                        DEFAULTSECT, 'from-addr', fallback=None),
                attachments=tuple(map(
                    lambda path: join(dirname(arg), path),
                    filter(None, map(lambda x: x.strip(),
                            config.get(DEFAULTSECT, 'attachments', fallback='').split(':')))
                )),
            )
    else:
        raise UserError('missing arguments')
