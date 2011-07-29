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

from .main import (
    UserError,
)

def new_to_addr_iter(path, use_shuffle=None):
    if use_shuffle is None:
        use_shuffle = True
    
    to_addr_list = []
    
    with open(path, encoding='utf-8', errors='replace', newline='\n') as fd:
        for line in filter(None, map(lambda x: x.strip(), fd)):
            to_addr = line
            
            if use_shuffle:
                to_addr_list.append(to_addr)
            else:
                yield to_addr
    
    if use_shuffle:
        from random import shuffle
        
        shuffle(to_addr_list)
        
        for to_addr in to_addr_list:
            yield to_addr

def new_mbox(
            to_addr,
            subject,
            text,
            real_from_addr=None,
            from_addr=None,
            attachments=None,
        ):
    assert to_addr is not None
    assert subject is not None
    assert text is not None
    
    mbox = repr(dict(
        to_addr=to_addr,
        subject=subject,
        text=text,
        real_from_addr=real_from_addr,
        from_addr=from_addr,
        attachments=attachments,
    ))
    
    return mbox

def sendmail(
            to_addr,
            subject,
            text,
            real_from_addr=None,
            from_addr=None,
            attachments=None,
            new_mbox=new_mbox,
        ):
    assert to_addr is not None
    assert subject is not None
    assert text is not None
    
    mbox = new_mbox(
        to_addr,
        subject,
        text,
        real_from_addr=real_from_addr,
        from_addr=from_addr,
        attachments=attachments,
    )
    
    print('sendmail(): mbox: == {}\n-------------------'.format(mbox)) # DEBUG TEST

def mass_sendmail(
            to_addr_list_file,
            subject,
            text,
            use_to_addr_list_shuffle=None,
            real_from_addr=None,
            from_addr=None,
            attachments=None,
        ):
    assert to_addr_list_file is not None
    assert subject is not None
    assert text is not None
    
    if attachments is None:
        attachments = ()
    
    for to_addr in new_to_addr_iter(to_addr_list_file, use_shuffle=use_to_addr_list_shuffle):
        sendmail(
            to_addr,
            subject,
            text,
            real_from_addr=real_from_addr,
            from_addr=from_addr,
            attachments=attachments,
        )
