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
from futuresboard.db_manager import *
from futuresboard.models import *

NO_WARRANTY_NOTICE = \
"THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n\
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n\
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n\
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n\
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n\
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN\n\
THE SOFTWARE.\n"

VERSION = '0.01'
HELP_STR = 'Admin tool V{}. \n'.format(VERSION) + \
           'Supported command list: \n' + \
           'mkadmin [user]                             made specified user admin\n' + \
           'rmadmin [user]                             removes admin rights from specified user\n' + \
           'suspend [user]                             suspends specified user\n' + \
           'resume [user]                              suspends specified user\n' + \
           'set_bal [user] [balance]                   assign balance to specified user\n' + \
           'creds [user]                               returns api credentials of specified user\n' + \
           'delete [user]                              deletes specified user and associated data\n' + \
           'list                                       lists of users\n' + \
           'quit                                       exists the program\n' + \
           'help, --help, -h                           prints this text\n\n'

           
def get_user_list():
        users = UserModel.query.all()   
        return users

def get_username_list():
    users = get_user_list()
    usernames = [user.username for user in users]
    return usernames

def delete_user(user):
    for income in user.incomes:
        db.session.delete(income)
    for position in user.positions:
        db.session.delete(position)
    for account in user.accounts:
        db.session.delete(account)
    for order in user.orders:
        db.session.delete(order)
    db.session.delete(user)

if __name__ == '__main__':
    print(NO_WARRANTY_NOTICE)
    while True:
        usernames = get_username_list()
        cmd = input("Command: ")
        if cmd.lower().find('mkadmin') == 0 or \
                cmd.lower().find('rmadmin') == 0 or \
                cmd.lower().find('suspend') == 0 or \
                cmd.lower().find('resume') == 0 or \
                cmd.lower().find('creds') == 0 or \
                cmd.lower().find('set_bal') == 0 or \
                cmd.lower().find('delete') == 0:
            params = cmd.split(' ')
            if len(params) < 2:
                print('Error: username is missing!') 
                continue
            else:
                username = params[1]
                if username not in usernames:
                    print(f'Error: username: {username} not found!') 
                    continue
                else:
                    user = UserModel.query.filter_by(username=username).first()
                    if cmd.lower().find('mkadmin') == 0:
                        user.is_admin = True
                    elif cmd.lower().find('rmadmin') == 0:
                        user.is_admin = False
                    elif cmd.lower().find('suspend') == 0:
                        user.status = 'suspended'    
                    elif cmd.lower().find('resume') == 0:
                        user.status = 'active'  
                    elif cmd.lower().find('set_bal') == 0:
                        if len(params) != 3:
                            print('Error: balance is missing!') 
                            continue
                        bal_str = params[2]
                        if not bal_str.replace('.', '', 1).isdigit():
                            print('Error: wrong format of balance parameter!') 
                            continue
                        user.budget = float(bal_str)
                    elif cmd.lower().find('creds') == 0:
                        label_lst = CredentialManager.get_api_label_list(username)
                        label_lst = [*map(lambda x : x.split('@')[0], label_lst)]
                        for api_label in label_lst:
                            credentials = CredentialManager.get_credentials(api_label, username)
                            print('{}: [{}]'.format(api_label, str(credentials).replace('{', '').replace('}', ''))) 
                        continue
                    elif cmd.lower().find('delete') == 0:
                        ans = input(f"Deleting {username} are you sure to continue? [y/n]: ")
                        if ans.lower() == 'y' or ans.lower() == 'yes':
                            delete_user(user)
                        else:
                            continue                                          
                    db.session.commit()
                    print('Done!')
        elif cmd.lower().find('list') == 0:
            user_lst = get_user_list()
            for user in user_lst:
                is_admin = 'yes' if user.is_admin == True else 'no'
                print(f'{user.username}: [status: {user.status}, is admin: {is_admin}, balance: {user.budget}]')
                
        elif cmd.lower().find('help') == 0 or cmd.lower().find('--help') == 0 or cmd.lower().find('-h') == 0:
            print(HELP_STR)
            continue
        elif cmd.lower().find('quit') == 0:
            print('Exiting...')
            sys.exit(0)
        else:
            print('{}: command not found'.format(cmd))
            continue

