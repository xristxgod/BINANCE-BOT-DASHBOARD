# coding: utf-8
# Copyright (c) 2020-2021 VADYM LAPCHYNSKYI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Vadim Lapchinskiy <vadim.lapchinsky@gmail.com>

import sys
import ccxt
import stdiomask
import re
from CredentialManager import CredentialManager

NO_WARRANTY_NOTICE = \
"THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n\
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n\
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n\
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n\
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n\
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN\n\
THE SOFTWARE.\n"

VERSION = '0.03'
HELP_STR = 'Credential management tool V{}. \n'.format(VERSION) + \
           'Supported command list: \n' + \
           'set [api label]                            creates and set new API credentials\n' + \
           'remove [api label]                         removes specified API credentials\n' + \
           'list                                       lists API labels\n' + \
           'exchanges                                  lists of supported exchanges\n' + \
           'quit                                       exists the program\n' + \
           'help, --help, -h                           prints this text\n\n'

if __name__ == '__main__':
    print(NO_WARRANTY_NOTICE)
    while True:
        pi_label = ''
        api_exchange_name = ''
        api_credentials = {}
        cmd = input("Command: ")
        if cmd.lower().find('set') == 0:
            params = cmd.split(' ')
            if len(params) != 2:
                print('Error: Api label name is missing!') 
                continue
            else:
                user_name = None
                user_name_idx = params[1].find('@')
                if user_name_idx > 0:
                    splt = params[1].split('@')
                    api_label = splt[0]
                    user_name = splt[1]
                else:
                    api_label = params[1]
                regex = re.compile('[!#$%^&*()<>?/\|}{~:]')
                if(regex.search(api_label) != None):
                    print('Error: Api label name should not contain special characters!') 
                    continue
                api_exchange_name = input("Exchange: ").lower()
                if api_exchange_name.lower() not in ccxt.exchanges:
                    print('Error: exchange \'{}\' not found!'.format(api_exchange_name))
                    continue
                exchange_class = getattr(ccxt, api_exchange_name.lower()) 
                exchange_instance = exchange_class()
                req_keys = [*filter(lambda cred: exchange_instance.requiredCredentials[cred], exchange_instance.requiredCredentials)]
                for key in req_keys:
                    cred_val = stdiomask.getpass(prompt=key + ': ', mask='*')
                    if len(cred_val):
                        api_credentials[key] = cred_val
                    else:
                        print('Error: wrong credential value!')
                        api_credentials = {}
                        continue
                if len(api_credentials) == 0:
                    continue
                else:
                    CredentialManager.set_credentials(api_label, api_exchange_name, api_credentials, user_name)
                    print('Credentials for {} successfully set.'.format(params[1]))
                    continue
        elif cmd.lower().find('remove') == 0:
            params = cmd.split(' ')
            if len(params) != 2:
                print('Error: Api label name is missing!') 
                continue
            else:
                api_label = params[1]
                label_lst = CredentialManager.get_api_label_list()
                if api_label in label_lst:
                    ans = input("Removing {} are you sure to continue? [y/n]: ".format(api_label))
                    if ans.lower() == 'y' or ans.lower() == 'yes':
                        CredentialManager.remove_credentials(api_label)
                        print('Done!')
                    else:
                        continue
                else:
                    print('Error: no \'{}\' label not found!'.format(api_label))
                    continue
        elif cmd.lower().find('list') == 0:
            label_lst = CredentialManager.get_api_label_list()
            for lb in label_lst:
                print(lb)
        elif cmd.lower().find('exchanges') == 0:
            for name in ccxt.exchanges:
                print(name)
        elif cmd.lower().find('help') == 0 or cmd.lower().find('--help') == 0 or cmd.lower().find('-h') == 0:
            print(HELP_STR)
            continue
        elif cmd.lower().find('quit') == 0:
            print('Exiting...')
            sys.exit(0)
        else:
            print('{}: command not found'.format(cmd))
            continue
            
