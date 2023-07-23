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
logger = Logger()

# GUI callbacks
def select_csv_callback(sender, app_data):
    """ Callback called when a .csv file is selected."""

    dpg.set_value("file_path", app_data['file_path_name'])
    dpg.configure_item("start_button", show=True, label="Lifechange")


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
            data_csv = pd.read_csv(dpg.get_value('file_path'))
            if data_csv['done'].isna().any():
                random_row = data_csv.query('done.isna()', engine='python').sample()
                row = random_row.iloc[0]
                logger.info_log(row['address'], 'Work! Work! Work!')
                try:
                    balance_status = balance_logic(account=row, settings=settings, logger=logger)
                    if balance_status == True:
                        mint_status = mint_logic(account=row, settings=settings, logger=logger)
                        if mint_status == True:
                            data_csv.at[random_row.index[0], 'done'] = 'done'
                            data_csv.to_csv(dpg.get_value('file_path'), index=False)
                except Exception as e:
                    logger.error_log(row['address'], e)
                    break
            else:
                print(f'All wallets finished!')
                logger.all_info_log(f'All wallets finished!')
                break
        except Exception as e:
            logger.all_error_log('Error while running the script.')
            break

# Functions
def main_window():
    """ Rendering main window."""
    with dpg.file_dialog(directory_selector=False, show=False, callback=select_csv_callback, cancel_callback=cancel_select_csv_callback, id="file_dialog_id", width=700 ,height=400):
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
        dpg.bind_font(font1)

        # author tag
        dpg.add_text("""$$___$_$$__$$_$$$$$$_$$$$$__$$$$$___$$$$__$$$$$__$$$$$___$$$$__$$$$$$_$$$$$__$$$$$______$$$$$__$$$$$$_$$__$$
$$$_$$_$$__$$___$$___$$_____$$__$$_$$_____$$__$$_$$_____$$__$$___$$___$$__$$_$$_________$$_______$$___$$__$$
$$_$_$_$$__$$___$$___$$$$___$$__$$__$$$$__$$$$$__$$$$___$$_______$$___$$$$$__$$$$_______$$$$_____$$___$$$$$$
$$___$_$$__$$___$$___$$_____$$__$$_____$$_$$_____$$_____$$__$$___$$___$$__$$_$$_________$$_______$$___$$__$$
$$___$__$$$$____$$___$$$$$__$$$$$___$$$$__$$_____$$$$$___$$$$____$$___$$__$$_$$$$$__$$__$$$$$____$$___$$__$$""", indent=270, color=(128, 173, 153, 255))
        dpg.add_text('Zora Software', indent=600, color=(153, 128, 173, 255))

        with dpg.group(horizontal=True):

            # first child window with settings
            with dpg.child_window(width=300, tag='settings', border=False):
                dpg.add_text('Provide settings:')
                dpg.add_spacer(height=20)
                dpg.add_text('NFT1155 contract:')
                dpg.add_input_text(tag='NFT_CONTRACT', default_value='0xF41A3e3033D4e878943194B729AeC993a4Ea2045')
                dpg.add_text('NFT1155 id:')
                dpg.add_input_text(tag='NFT_ID', default_value='5')
                dpg.add_text('Mint NFT price (ETH):')
                dpg.add_input_text(tag='MINT_PRICE', default_value='0.000777')
                dpg.add_text('Gas price for mint (Gwei):')
                dpg.add_input_text(tag='GAS_PRICE_FOR_MINT', default_value='0.005')
                dpg.add_text('Gas for mint:')
                dpg.add_input_text(tag='GAS_FOR_MINT', default_value='130000')
                dpg.add_text('Max price for gas in Ethereum (Gwei):')
                dpg.add_input_text(tag='MAX_GAS_IN_GWEI', default_value='18')
                dpg.add_text('Amount for bridge (ETH):')
                dpg.add_input_text(tag='AMOUNT_FOR_BRIDGE', default_value='0.001')
                dpg.add_text('Accuracy in amount for bridge (ETH):')
                dpg.add_input_text(tag='ACCURACY_IN_AMOUNT_FOR_BRIDGE', default_value='0.00005')

                dpg.add_spacer(height=20)

                with dpg.group(horizontal=True):
                    dpg.add_text('Testnet')
                    dpg.add_checkbox(tag='IS_TESTNET', label='')

                dpg.add_spacer(height=20)
                dpg.add_text('Select CSV with wallets:')
                dpg.add_button(label="Open File", callback=lambda: dpg.show_item("file_dialog_id"))
                dpg.add_text('Not selected', tag='file_path')
                dpg.add_spacer(height=20)
                dpg.add_button(label="Select CSV", callback=start_callback, show=False, tag='start_button', indent=100)

            # second child window with logger
            with dpg.child_window(width=1068, tag='logger', border=False):
                logger.create_logger()

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

# script entry point
if __name__ == '__main__':
    load_gui()