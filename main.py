#!/usr/bin/env python3

##
# @mainpage Zora Automatization Software
#
# @section description_main Description
# This is a GUI-enabled program to automate the actions required for get
# a potential airdrop.

##
# @file main.py
#
# @brief The main file where the GUI is rendered and work begins.
#
# @section description_main Description
# The main file where the GUI is rendered and work begins.
#
# @section libraries_main Libraries/Modules
# - balance logic module (local)
# - mint logic module (local)
# - pandas for csv
# - logger module (local)
# - settings (local)
# - work with gui
#
# @section todo_main TODO
# - add work with accounts from gui
#
# @section author_main Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/24/2023.

# Imports
from balance_logic import balance_logic
from mint_logic import mint_logic
import pandas as pd
import dearpygui.dearpygui as dpg
from Logger import Logger
from Settings import Settings
import os
import sys

# Global constants
## A class that draws a logging window, with functions to send messages to the window.
logger_mint = Logger()
logger_bridge = Logger()

# GUI callbacks
def select_mint_csv_callback(sender, app_data):
    """ Callback called when a .csv file is selected."""

    dpg.set_value("file_path_mint", app_data['file_path_name'])
    dpg.configure_item("start_mint_button", show=True, label="Mint")

def select_bridge_csv_callback(sender, app_data):
    dpg.set_value('file_path_bridge', app_data['file_path_name'])
    dpg.configure_item('start_bridge_button', show=True, label="Bridge")

def cancel_select_csv_callback(sender, app_data):
    """ Callback called when canceling .csv file selection."""

    print('Cancel was clicked.')


def start_callback(sender, app_data):
    """ Main callback."""

    # set settings value from fields in GUI
    settings = Settings(
        nft_contract=dpg.get_value('NFT_CONTRACT'),
        nft_id=dpg.get_value('NFT_ID'),
        mint_price=dpg.get_value('MINT_PRICE'),
        gas_price_for_mint=dpg.get_value('GAS_PRICE_FOR_MINT'),
        gas_for_mint=dpg.get_value('GAS_FOR_MINT'),
        max_gas_in_gwei=dpg.get_value('MAX_GAS_IN_GWEI'),
        bridge_amount=dpg.get_value('AMOUNT_FOR_BRIDGE'),
        accuracy_in_amount_for_bridge=dpg.get_value('ACCURACY_IN_AMOUNT_FOR_BRIDGE'),
        testnet=dpg.get_value('IS_TESTNET'))

    while True:
        try:
            data_csv = pd.read_csv(dpg.get_value('file_path_mint'))
            if data_csv['done'].isna().any():
                random_row = data_csv.query('done.isna()', engine='python').sample()
                row = random_row.iloc[0]
                logger_mint.info_log(row['address'], 'Work! Work! Work!')
                try:
                    balance_status = balance_logic(account=row, settings=settings, logger=logger_mint)
                    if balance_status == True:
                        mint_status = mint_logic(account=row, settings=settings, logger=logger_mint)
                        if mint_status == True:
                            data_csv.at[random_row.index[0], 'done'] = 'done'
                            data_csv.to_csv(dpg.get_value('file_path'), index=False)
                except Exception as e:
                    logger_mint.error_log(row['address'], e)
                    break
            else:
                print(f'All wallets finished!')
                logger_mint.all_info_log(f'All wallets finished!')
                break
        except Exception as e:
            logger_mint.all_error_log('Error while running the script.')
            break

def start_mint_callback(sender, app_data):
    logger_mint.all_info_log('Mint! Mint! Mint!')

def start_bridge_callback(sender, app_data):
    logger_bridge.all_info_log('Bridge! Bridge! Bridge!')

def save_mint_settings_callback(sender, app_data):
    settings_csv = pd.read_csv(resource_path('settings.csv'))
    settings_csv.loc[0,[
        'nft_contract',
        'nft_id',
        'mint_price',
        'gas_price_for_mint',
        'gas_for_mint',
        'is_testnet_mint'
    ]] = [
        dpg.get_value('NFT_CONTRACT'),
        dpg.get_value('NFT_ID'),
        dpg.get_value('MINT_PRICE'),
        dpg.get_value('GAS_PRICE_FOR_MINT'),
        dpg.get_value('GAS_FOR_MINT'),
        dpg.get_value('IS_TESTNET_MINT')
    ]
    settings_csv.to_csv(resource_path('settings.csv'), index=False)
    logger_mint.all_info_log('Settings saved!')

def save_bridge_settings_callback(sender, app_data):
    settings_csv = pd.read_csv(resource_path('settings.csv'))
    settings_csv.loc[0,[
        'max_gas_in_gwei',
        'amount_for_bridge',
        'accuracy_in_amount_for_bridge',
        'is_testnet_bridge'
    ]] = [
        dpg.get_value('MAX_GAS_IN_GWEI'),
        dpg.get_value('AMOUNT_FOR_BRIDGE'),
        dpg.get_value('ACCURACY_IN_AMOUNT_FOR_BRIDGE'),
        dpg.get_value('IS_TESTNET_BRIDGE')
    ]
    settings_csv.to_csv(resource_path('settings.csv'), index=False)
    logger_bridge.all_info_log('Settings saved!')

def edit_account_callback(sender, app_data, user_data):
    account_window(account=user_data)


# Functions
def main_window():
    """ Rendering main window."""
    with dpg.file_dialog(directory_selector=False, show=False, callback=select_mint_csv_callback, cancel_callback=cancel_select_csv_callback, id="file_dialog_mint", width=700 ,height=400):
        dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")

    with dpg.file_dialog(directory_selector=False, show=False, callback=select_bridge_csv_callback, cancel_callback=cancel_select_csv_callback, id="file_dialog_bridge", width=700 ,height=400):
        dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")

    with dpg.font_registry():
        font_path=resource_path("resources/FiraCode-Regular.ttf")
        with dpg.font(font_path, 15) as font1:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Thai)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)

    with dpg.window(tag='Primary Window', no_title_bar=False):
        dpg.bind_font(font1) # type: ignore

        # author tag
        dpg.add_text("""$$___$_$$__$$_$$$$$$_$$$$$__$$$$$___$$$$__$$$$$__$$$$$___$$$$__$$$$$$_$$$$$__$$$$$______$$$$$__$$$$$$_$$__$$
$$$_$$_$$__$$___$$___$$_____$$__$$_$$_____$$__$$_$$_____$$__$$___$$___$$__$$_$$_________$$_______$$___$$__$$
$$_$_$_$$__$$___$$___$$$$___$$__$$__$$$$__$$$$$__$$$$___$$_______$$___$$$$$__$$$$_______$$$$_____$$___$$$$$$
$$___$_$$__$$___$$___$$_____$$__$$_____$$_$$_____$$_____$$__$$___$$___$$__$$_$$_________$$_______$$___$$__$$
$$___$__$$$$____$$___$$$$$__$$$$$___$$$$__$$_____$$$$$___$$$$____$$___$$__$$_$$$$$__$$__$$$$$____$$___$$__$$""", indent=270, color=(128, 173, 153, 255))
        dpg.add_text('Zora Software', indent=600, color=(153, 128, 173, 255))

        with dpg.tab_bar(tag='tab_bar'):

            with dpg.tab(
                tag='tab_mint',
                label='Mint'
            ):

                with dpg.group(horizontal=True):

                    # first child window with settings
                    with dpg.child_window(width=300, tag='settings_mint', border=False):
                        dpg.add_text('Provide settings:')
                        dpg.add_spacer(height=20)
                        dpg.add_text('NFT1155 contract:')
                        dpg.add_input_text(tag='NFT_CONTRACT', default_value=settings['nft_contract'])
                        dpg.add_text('NFT1155 id:')
                        dpg.add_input_text(tag='NFT_ID', default_value=settings['nft_id'])
                        dpg.add_text('Mint NFT price (ETH):')
                        dpg.add_input_text(tag='MINT_PRICE', default_value=settings['mint_price'])
                        dpg.add_text('Gas price for mint (Gwei):')
                        dpg.add_input_text(tag='GAS_PRICE_FOR_MINT', default_value=settings['gas_price_for_mint'])
                        dpg.add_text('Gas for mint:')
                        dpg.add_input_text(tag='GAS_FOR_MINT', default_value=settings['gas_for_mint'])

                        dpg.add_spacer(height=20)

                        with dpg.group(horizontal=True):
                            dpg.add_text('Testnet')
                            dpg.add_checkbox(tag='IS_TESTNET_MINT', label='', default_value=bool(settings['is_testnet_mint']))

                        dpg.add_spacer(height=20)
                        dpg.add_button(label='Save Settings', callback=save_mint_settings_callback, indent=100)
                        dpg.add_spacer(height=20)
                        dpg.add_text('Select CSV with wallets:')
                        dpg.add_button(label='Open File', callback=lambda: dpg.show_item('file_dialog_mint'))
                        dpg.add_text('Not selected', tag='file_path_mint')
                        dpg.add_spacer(height=20)
                        dpg.add_button(label='Select CSV', callback=start_mint_callback, show=False, tag='start_mint_button', indent=100)

                    # second child window with logger
                    with dpg.child_window(width=1068, tag='logger_mint', border=False):
                        logger_mint.create_logger()

            with dpg.tab(
                tag="bridge_tab",
                label="Bridge"
            ):
                with dpg.group(horizontal=True):

                    # first child window with settings
                    with dpg.child_window(width=300, tag='settings_bridge', border=False):
                        dpg.add_text('Provide settings:')
                        dpg.add_spacer(height=20)
                        dpg.add_text('Max price for gas in Ethereum (Gwei):')
                        dpg.add_input_text(tag='MAX_GAS_IN_GWEI', default_value=settings['max_gas_in_gwei'])
                        dpg.add_text('Amount for bridge (ETH):')
                        dpg.add_input_text(tag='AMOUNT_FOR_BRIDGE', default_value=settings['amount_for_bridge'])
                        dpg.add_text('Accuracy in amount for bridge (ETH):')
                        dpg.add_input_text(tag='ACCURACY_IN_AMOUNT_FOR_BRIDGE', default_value="{:f}".format(settings['accuracy_in_amount_for_bridge']))

                        dpg.add_spacer(height=20)

                        with dpg.group(horizontal=True):
                            dpg.add_text('Testnet')
                            dpg.add_checkbox(tag='IS_TESTNET_BRIDGE', label='', default_value=bool(settings['is_testnet_bridge']))

                        dpg.add_spacer(height=20)
                        dpg.add_button(label='Save Settings', callback=save_bridge_settings_callback, indent=100)
                        dpg.add_spacer(height=20)
                        dpg.add_text('Select CSV with wallets:')
                        dpg.add_button(label="Open File", callback=lambda: dpg.show_item("file_dialog_bridge"))
                        dpg.add_text('Not selected', tag='file_path_bridge')
                        dpg.add_spacer(height=20)
                        dpg.add_button(label="Select CSV", callback=start_bridge_callback, show=False, tag='start_bridge_button', indent=100)

                    # second child window with logger
                    with dpg.child_window(width=1068, tag='logger_bridge', border=False):
                        logger_bridge.create_logger()

            with dpg.tab(
                tag='accounts_tab',
                label='Accounts'
            ):
                dpg.add_text('List of accounts:')
                for account in accounts:
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Edit", callback=edit_account_callback, user_data=account)
                        dpg.add_text(account['address'])

def account_window(account):
    with dpg.window(tag='account_window', no_title_bar=False, width=500, height=200):
        with dpg.group(horizontal=True):
            dpg.add_text('Address:')
            dpg.add_input_text(tag='account_address', default_value=account['address'])
            dpg.add_text('Private key:')
            dpg.add_input_text(tag='account_private_key',)

def load_gui():
    """ GUI loader."""
    dpg.create_context()

    main_window()

    dpg.create_viewport(title='Zora Soft | RePack by mutedspectre.eth', width=1392, height=787, resizable=False)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    dpg.set_primary_window('Primary Window', True)

    dpg.start_dearpygui()

    dpg.destroy_context()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

settings = pd.read_csv(resource_path('settings.csv')).iloc[0]
accounts = pd.read_csv(resource_path('accounts.csv')).iloc()

# script entry point
if __name__ == '__main__':
    load_gui()
