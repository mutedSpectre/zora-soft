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
# - work with gui
# - access to resource path
# - access to settings
# - access to account child window
#
# @section author_main Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/25/2023.

# Imports
import pandas as pd
import dearpygui.dearpygui as dpg
from Logger import Logger
from accounts import account_child_window
from helpers import resource_path, get_settings
from bridge_logic import start_bridge_callback
from mint_logic import start_mint_callback

# Global constants
## A class that draws a logging window, with functions to send messages to the window.
logger_mint = Logger()
logger_bridge = Logger()

# GUI callbacks
def select_mint_csv_callback(sender, app_data):
    """ Callback called when a .csv file is selected.

    @param sender    Sender of the callback
    @param app_data  Data from the callback
    """

    dpg.set_value("file_path_mint", app_data['file_path_name'])
    dpg.configure_item("start_mint_button", show=True, label="Mint")

def select_bridge_csv_callback(sender, app_data):
    dpg.set_value('file_path_bridge', app_data['file_path_name'])
    dpg.configure_item('start_bridge_button', show=True, label="Bridge")

def save_mint_settings_callback(sender, app_data):
    """ Callback called when saving mint settings.
    
    @param sender    Sender of the callback
    @param app_data  Data from the callback
    """
    settings_csv = pd.read_csv(resource_path('settings.csv'))
    settings_csv.loc[0,[
        'nft_url',
        'mint_price',
        'gas_price_for_mint',
        'gas_for_mint',
        'is_testnet_mint'
    ]] = [
        dpg.get_value('NFT_URL'),
        dpg.get_value('MINT_PRICE'),
        dpg.get_value('GAS_PRICE_FOR_MINT'),
        dpg.get_value('GAS_FOR_MINT'),
        dpg.get_value('IS_TESTNET_MINT')
    ]
    settings_csv.to_csv(resource_path('settings.csv'), index=False)
    logger_mint.all_info_log('Settings saved!')

def save_bridge_settings_callback(sender, app_data):
    """ Callback called when saving bridge settings.
    
    @param sender    Sender of the callback
    @param app_data  Data from the callback
    """
    settings_csv = pd.read_csv(resource_path('settings.csv'))
    settings_csv.loc[0,[
        'max_gas_in_gwei',
        'min_amount_for_bridge',
        'max_amount_for_bridge',
        'is_testnet_bridge'
    ]] = [
        dpg.get_value('MAX_GAS_IN_GWEI'),
        dpg.get_value('MIN_AMOUNT_FOR_BRIDGE'),
        dpg.get_value('MAX_AMOUNT_FOR_BRIDGE'),
        dpg.get_value('IS_TESTNET_BRIDGE')
    ]
    settings_csv.to_csv(resource_path('settings.csv'), index=False)
    logger_bridge.all_info_log('Settings saved!')

# Functions
def main_window():
    """ Rendering main window."""
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
        dpg.add_text('Zora Software v2.0', indent=595, color=(153, 128, 173, 255))

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
                        dpg.add_text('NFT 1155 URL:')
                        dpg.add_input_text(tag='NFT_URL', default_value=settings['nft_url'])
                        dpg.add_text('Mint price (ETH):')
                        dpg.add_input_text(tag='MINT_PRICE', default_value=settings['mint_price'])
                        dpg.add_text('Gas price for mint (Gwei):')
                        dpg.add_input_text(tag='GAS_PRICE_FOR_MINT', default_value=settings['gas_price_for_mint'])
                        dpg.add_text('Gas for mint:')
                        dpg.add_input_text(tag='GAS_FOR_MINT', default_value=settings['gas_for_mint'])

                        dpg.add_spacer(height=20)

                        with dpg.group(horizontal=True):
                            dpg.add_text('Testnet:')
                            dpg.add_checkbox(tag='IS_TESTNET_MINT', label='', default_value=bool(settings['is_testnet_mint']))

                        dpg.add_spacer(height=20)
                        dpg.add_button(label='Save Settings', callback=save_mint_settings_callback, indent=90)

                        dpg.add_spacer(height=40)
                        dpg.add_button(label='Start Mint', callback=start_mint_callback, indent=100, user_data=logger_mint)

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
                        dpg.add_text('Min amount for bridge (ETH):')
                        dpg.add_input_text(tag='MIN_AMOUNT_FOR_BRIDGE', default_value=settings['min_amount_for_bridge'])
                        dpg.add_text('Max amount for bridge (ETH):')
                        dpg.add_input_text(tag='MAX_AMOUNT_FOR_BRIDGE', default_value=settings['max_amount_for_bridge'])

                        dpg.add_spacer(height=20)

                        with dpg.group(horizontal=True):
                            dpg.add_text('Testnet:')
                            dpg.add_checkbox(tag='IS_TESTNET_BRIDGE', label='', default_value=bool(settings['is_testnet_bridge']))

                        dpg.add_spacer(height=20)
                        dpg.add_button(label='Save Settings', callback=save_bridge_settings_callback, indent=90)

                        dpg.add_spacer(height=40)
                        dpg.add_button(label='Start Bridge', callback=start_bridge_callback, indent=95, user_data=logger_bridge)

                    # second child window with logger
                    with dpg.child_window(width=1068, tag='logger_bridge', border=False):
                        logger_bridge.create_logger()

            with dpg.tab(
                tag='accounts_tab',
                label='Accounts'
            ):
                account_child_window()

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

settings = get_settings()

# script entry point
if __name__ == '__main__':
    load_gui()
