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

import keyring
from builtins import staticmethod


class CredentialManager:
    
    SERVICE_ID = 'CRYPTO_BOT_1'
    API_LIST_LOGIN_STR = 'CRYPTO_BOT_API_LIST_LOGIN_1'
    SUCCESS = 0
    ALREADY_EXISTS = 1 

    @staticmethod
    def set_credentials(api_label, exchange_name, api_credentials, user_name=None):
        if user_name == None or api_label.find('@') > 0:
            login_str = exchange_name + '_' + api_label
        else:
            login_str = exchange_name + '_' + api_label + '@' + user_name
        # checking if the credentials were already assigned for this login
        curr_cred = keyring.get_password(CredentialManager.SERVICE_ID, login_str)
        if curr_cred == None or curr_cred.password == None:
            keyring.set_password(CredentialManager.SERVICE_ID, login_str, str(api_credentials))
            label_list = CredentialManager.get_raw_api_label_list()
            label_list.append(login_str)
            CredentialManager.set_raw_api_label_list(label_list)
            return CredentialManager.SUCCESS
        else:
            return CredentialManager.ALREADY_EXISTS
        
    @staticmethod
    def get_credentials(api_label, user_name=None):
        exchange_name = CredentialManager.get_exchange_name_from_api_label(api_label)
        if user_name == None or api_label.find('@') > 0:
            login_str = exchange_name + '_' + api_label
        else:
            login_str = exchange_name + '_' + api_label + '@' + user_name
        cred_str = keyring.get_password(CredentialManager.SERVICE_ID, login_str)
        cred_dict = eval(cred_str)
        return cred_dict
    
    @staticmethod
    def remove_credentials(api_label, user_name=None):
        exchange_name = CredentialManager.get_exchange_name_from_api_label(api_label)
        if user_name == None or api_label.find('@') > 0:
            login_str = exchange_name + '_' + api_label
        else:
            login_str = exchange_name + '_' + api_label + '@' + user_name
        try:
            keyring.delete_password(CredentialManager.SERVICE_ID, login_str)
        except keyring.errors.PasswordDeleteError:
            pass            
        label_list = CredentialManager.get_raw_api_label_list()
        label_list.remove(login_str)
        CredentialManager.set_raw_api_label_list(label_list)
        return CredentialManager.SUCCESS
    
    @staticmethod
    def get_raw_api_label_list():
        passwd = keyring.get_password(CredentialManager.SERVICE_ID, CredentialManager.API_LIST_LOGIN_STR)
        if passwd == None or len(passwd) == 0:
            return []
        else:
            label_list = passwd.split(', ')
            return label_list
             
    @staticmethod
    def set_raw_api_label_list(label_list):
        keyring.set_password(CredentialManager.SERVICE_ID, CredentialManager.API_LIST_LOGIN_STR, ', '.join(label_list))
        return CredentialManager.SUCCESS
    
    @staticmethod
    def get_api_label_list(user_name=None):
        raw_api_labels = CredentialManager.get_raw_api_label_list()
        api_labels = [*map(lambda el: el.split('_', 1)[1], raw_api_labels)]
        if user_name != None:
            api_labels = [*filter(lambda x : x.find('@') > 0 and x.split('@')[1] == user_name, api_labels)]
        return api_labels
    
    @staticmethod
    def get_exchange_name_from_api_label(api_label):
        exch_plus_label_list = CredentialManager.get_raw_api_label_list()
        exch_plus_label = [*filter(lambda el: el.find(api_label) > 0, exch_plus_label_list)][0]
        exchange_name = exch_plus_label.split('_')[0]
        return exchange_name
