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

from .main import (
    UserError,
)

class SendmailError(Exception):
    pass

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

def i_string_encode(s):
    from base64 import b64encode
    
    b = b64encode(s.encode('UTF-8', 'replace'))
    i = '=?utf-8?B?{}?='.format(b.decode('ascii'))
    
    return i

def i_string(s):
    try:
        b = s.encode('ascii')
    except UnicodeEncodeError:
        i = i_string_encode(s)
    else:
        if '=' not in s and '"' not in s:
            i = s
        else:
            i = i_string_encode(s)
    
    return i

def base64_data(b):
    if isinstance(b, bytes):
        pass
    elif isinstance(b, str):
        b = b.encode('utf-8', 'replace')
    else:
        b = str(b).encode('utf-8', 'replace')
    
    from base64 import b64encode
    from textwrap import wrap
    
    result = wrap(b64encode(b).decode('ascii'))
    
    return result

def new_boundary():
    from random import choice
    
    r = ''.join(
        choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/')
        for x in range(20)
    )
    boundary = '=-{}'.format(r)
    
    return boundary

def new_mbox(
            to_addr,
            subject,
            text,
            from_name=None,
            from_addr=None,
            to_name=None,
            attachments=None,
            attachments_cache=None,
        ):
    if attachments is None:
        attachments = ()
    if attachments_cache is None:
        attachments_cache = {}
    
    mbox_list = []
    boundary = new_boundary()
    
    if subject is not None:
        mbox_list.append('Subject: {}'.format(i_string(subject)))
    if from_addr is not None:
        if from_name is not None:
            mbox_list.append('From: {} <{}>'.format(i_string(from_name), from_addr))
        else:
            mbox_list.append('From: {}'.format(from_addr))
    if to_addr is not None:
        if to_name is not None:
            mbox_list.append('To: {} <{}>'.format(i_string(to_name), to_addr))
        else:
            mbox_list.append('To: {}'.format(to_addr))
    mbox_list.append('Content-Type: multipart/mixed; boundary="{}"'.format(boundary))
    mbox_list.append('')
    
    if text is not None:
        text_b64 = base64_data(text)
        
        mbox_list.append('--{}'.format(boundary))
        mbox_list.append('Content-Type: text/plain; charset="UTF-8"')
        mbox_list.append('Content-Transfer-Encoding: base64')
        mbox_list.append('')
        mbox_list.extend(text_b64)
    
    if attachments:
        from os.path import abspath, basename
        
        for att_path in attachments:
            att_name = basename(att_path)
            att_abs_path = abspath(att_path)
            
            if att_abs_path in attachments_cache:
                att_b64 = attachments_cache[att_abs_path]
            else:
                with open(att_path, 'rb') as fd:
                    att_data = fd.read()
                
                att_b64 = base64_data(att_data)
                attachments_cache[att_abs_path] = att_b64
            
            mbox_list.append('--{}'.format(boundary))
            mbox_list.append('Content-Type: application/octet-stream; name="{}"'.format(i_string(att_name)))
            mbox_list.append('Content-Disposition: attachment; filename="{}"'.format(i_string(att_name)))
            mbox_list.append('Content-Transfer-Encoding: base64')
            mbox_list.append('')
            mbox_list.extend(att_b64)
    
    mbox_list.append('--{}--'.format(boundary))
    mbox_list.append('.')
    
    mbox = '\r\n'.join(mbox_list)
    
    return mbox

def sendmail(
            to_addr,
            subject,
            text,
            real_from_addr=None,
            from_name=None,
            from_addr=None,
            to_name=None,
            attachments=None,
            attachments_cache=None,
            new_mbox=new_mbox,
        ):
    assert to_addr is not None
    
    from subprocess import Popen, PIPE
    
    mbox = new_mbox(
        to_addr,
        subject,
        text,
        from_name=from_name,
        from_addr=from_addr,
        to_name=to_name,
        attachments=attachments,
        attachments_cache=attachments_cache,
    )
    mbox_b = mbox.encode('utf-8', 'replace')
    
    args = ['sendmail']
    if real_from_addr is not None:
        args.extend(('-f', real_from_addr))
    args.append(to_addr)
    
    with Popen(args, stdin=PIPE) as proc:
        proc.stdin.write(mbox_b)
        proc.stdin.close()
        ret = proc.wait()
    
    if ret != 0:
        raise SendmailError('sandmail-proc result is not zero')

def mass_sendmail(
            to_addr_list_file,
            subject,
            text,
            use_to_addr_list_shuffle=None,
            real_from_addr=None,
            from_name=None,
            from_addr=None,
            attachments=None,
            force_delay=None,
        ):
    from .safe_print import safe_print as print
    
    attachments_cache = {}
    
    for i, to_addr in enumerate(new_to_addr_iter(
            to_addr_list_file,
            use_shuffle=use_to_addr_list_shuffle)):
        print('[{}] {}...'.format(i, to_addr), end=' ')
        try:
            sendmail(
                to_addr,
                subject,
                text,
                real_from_addr=real_from_addr,
                from_name=from_name,
                from_addr=from_addr,
                attachments=attachments,
                attachments_cache=attachments_cache,
            )
        except KeyboardInterrupt:
            print('KeyboardInterrupt!')
            break
        except:
            from traceback import print_exc
            
            print('ERROR!')
            print_exc()
        else:
            print('PASS!')
        
        if force_delay is not None:
            from time import sleep
            
            print('delaying {} sec...'.format(force_delay), end=' ')
            sleep(force_delay)
            print('DONE')
