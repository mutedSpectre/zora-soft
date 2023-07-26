"""!@brief GUI and other functions for work with accounts"""
##
# @file accounts.py
#
# @brief GUI and other functions for work with accounts.
#
# @section description_accounts Description
# Contains functions for work with accounts.
#
# @section libraries_accounts Libraries/Modules
# - access to Any type
# - access to GUI
# - access to pandas
# - access to helpers
#
# @section author_accounts Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/25/2023.

# Imports
from typing import Any
import dearpygui.dearpygui as dpg
import pandas as pd
from helpers import get_accounts, resource_path


# GUI callbacks
def edit_account_callback(sender: Any, app_data: Any, user_data: Any) -> None:
    """ Edit account callback.
    
    @param sender    Sender of the callback
    @param app_data  Data from the callback
    @param user_data User account
    """

    account_edit_window(account=user_data)

def add_account_callback(sender, app_data) -> None:
    """ Callback for adding a new account.

    @param sender    Sender of the callback
    @param app_data  Data from the callback
    """

    accounts_csv = pd.read_csv(resource_path('accounts.csv'))
    accounts_csv.loc[len(accounts_csv.index) + 1] = [None, None, None, False, False]
    accounts_csv.to_csv(resource_path('accounts.csv'), index=False)

    refresh_accounts_window()

def save_account_callback(sender: Any, app_data: Any, user_data: Any) -> None:
    """ Callback for saving an account.

    @param sender    Sender of the callback
    @param app_data  Data from the callback
    @param user_data User account
    """

    accounts_csv = pd.read_csv(resource_path('accounts.csv'))
    accounts_csv.loc[user_data, 'address'] = dpg.get_value('account_address')
    accounts_csv.loc[user_data, 'private_key'] = dpg.get_value('account_private_key')
    accounts_csv.loc[user_data, 'proxy'] = dpg.get_value('account_proxy')
    accounts_csv.loc[user_data, 'bridge'] = dpg.get_value('account_bridge')
    accounts_csv.loc[user_data, 'mint'] = dpg.get_value('account_mint')
    accounts_csv.to_csv(resource_path('accounts.csv'), index=False)

    refresh_accounts_window()

    # Close account edit window
    dpg.delete_item('account_edit_window')

def delete_account_callback(sender: Any, app_data: Any, user_data: Any) -> None:
    """ Callback for deleting an account.

    @param sender    Sender of the callback
    @param app_data  Data from the callback
    @param user_data User account
    """

    accounts_csv = pd.read_csv(resource_path('accounts.csv'))
    accounts_csv = accounts_csv.drop(user_data)
    accounts_csv.to_csv(resource_path('accounts.csv'), index=False)

    refresh_accounts_window()

def cancel_account_callback(sender: Any, app_data: Any) -> None:
    """ Callback for canceling an account editing.

    @param sender    Sender of the callback
    @param app_data  Data from the callback
    """

    # Close account window
    dpg.delete_item('account_edit_window')


# Functions
def turn_off_account_bridge(account: int) -> None:
    """ Turn off bridge for account.

    @param account Account id
    """

    accounts_csv = pd.read_csv(resource_path('accounts.csv'))
    accounts_csv.loc[account, 'bridge'] = False
    accounts_csv.to_csv(resource_path('accounts.csv'), index=False)

    refresh_accounts_window()

def turn_off_account_mint(account: int) -> None:
    """ Turn off mint for account.

    @param account Account id
    """

    accounts_csv = pd.read_csv(resource_path('accounts.csv'))
    accounts_csv.loc[account, 'mint'] = False
    accounts_csv.to_csv(resource_path('accounts.csv'), index=False)

    refresh_accounts_window()

def account_child_window() -> None:
    """ Create accounts child window. """

    with dpg.child_window(width=700, tag='accounts_window', border=False, parent='accounts_tab'):
        dpg.add_text('List of accounts:')
        for account in get_accounts():
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Edit", callback=edit_account_callback, user_data=account)
                dpg.add_button(label="Delete", callback=delete_account_callback, user_data=account.name)

                if not pd.isna(account['address']):
                    dpg.add_text(account['address'])
                    if account['bridge']:
                        dpg.add_text('Bridge', color=[0, 255, 0])
                    else:
                        dpg.add_text('No bridge', color=[255, 0, 0])
                    if account['mint']:
                        dpg.add_text('Mint', color=[0, 255, 0])
                    else:
                        dpg.add_text('No mint', color=[255, 0, 0])
                else: 
                    dpg.add_text('Edit this account...')
        dpg.add_spacer(height=20)
        dpg.add_button(label="Add new account", callback=add_account_callback)

def account_edit_window(account) -> None:
    """ Create account edit window.

    @param account Account
    """

    with dpg.window(
        tag='account_edit_window', 
        label='Edit account "' + str(account['address']) + '"', 
        width=700, 
        height=200,
        on_close=cancel_account_callback
    ):
        with dpg.group(horizontal=True):
            dpg.add_text('Address:')
            dpg.add_input_text(tag='account_address', default_value=account['address'])
        with dpg.group(horizontal=True):
            dpg.add_text('Private key:')
            dpg.add_input_text(tag='account_private_key', default_value=account['private_key'])
        with dpg.group(horizontal=True):
            dpg.add_text('Proxy (like login:password@ip:port):')
            dpg.add_input_text(tag='account_proxy', default_value=account['proxy'])
        with dpg.group(horizontal=True):
            dpg.add_text('Bridge:')
            dpg.add_checkbox(tag='account_bridge', label='', default_value=bool(account['bridge']))
        with dpg.group(horizontal=True):
            dpg.add_text('Mint:')
            dpg.add_checkbox(tag='account_mint', label='', default_value=bool(account['mint']))
        
        with dpg.group(horizontal=True):
            dpg.add_button(label='Save', callback=save_account_callback, user_data=account.name)
            dpg.add_button(label='Cancel', callback=cancel_account_callback)

def refresh_accounts_window() -> None:
    """ Refresh accounts window. """
    if dpg.does_item_exist('accounts_window'):
        dpg.delete_item('accounts_window')
    account_child_window()