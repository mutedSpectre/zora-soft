"""!@brief Helper functions for scripts"""
##
# @file helpers.py
#
# @brief Helper functions for scripts.
#
# @section description_helpers Description
# Contains helper functions
#
# @section libraries_helpers Libraries/Modules
# - access to os
# - access to sys
# - access to pandas
# - access to web3
#
# @section author_helpers Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/25/2023.

# Imports
import os
import sys
import pandas as pd
from web3 import Web3

# Functions
def get_accounts():
    """ Get accounts from accounts.csv"""
    accounts = pd.read_csv(resource_path('accounts.csv')).iloc()
    return accounts

def get_shuffled_accounts():
    """ Get shuffled accounts from accounts.csv"""

    accounts = pd.read_csv(resource_path('accounts.csv'))
    accounts = accounts.sample(frac=1)
    return accounts.iloc()

def get_settings():
    """ Get settings from settings.csv"""
    settings = pd.read_csv(resource_path('settings.csv')).iloc[0]
    return settings

def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller 
    
    @param relative_path Relative path to resource
    """

    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def calculate_zora_fee_in_wei(
    mint_price: int, 
    gas_price_for_mint: float, 
    gas_for_mint: int, 
    w3_eth: Web3, 
    testnet: bool
    ) -> int:
    """ Calculate zora fee method
    
    @param mint_price         Price for mint without default price (default Zora price is 0.000777 ETH)
    @param gas_price_for_mint Price for gas in Zora Network
    @param gas_for_mint       Gas amount for tx 'mint' (av. 130-160k)
    @param w3_eth             Web3 provider for ethereum (needed for testnet)
    @param testnet            Use testnet, or no

    @return Required amount of eth for minting on Zora Network
    """

    # Calculate mint_price ETH to wei
    if testnet == False:
        # Calculate gas_price_for_mint gwei to wei * gas_for_mint + L1 gas price * 4000 * gas fee scalar
        zora_gas_fee = Web3.to_wei(gas_price_for_mint, 'gwei') * int(gas_for_mint) + int(w3_eth.eth.gas_price * 4000 * 0.684)
    else:
        # testnet zora have 1:1 gas fee scalar
        zora_gas_fee = Web3.to_wei(gas_price_for_mint, 'gwei') * int(gas_for_mint) + Web3.to_wei(4, 'gwei') * 7000

    return mint_price + zora_gas_fee

def get_zora_rpc_for_bridge() -> str:
    settings = get_settings()
    if bool(settings['is_testnet_bridge']) == True:
        return 'https://testnet.rpc.zora.energy'
    else:
        return 'https://rpc.zora.energy'

def get_eth_rpc_for_bridge() -> str:
    settings = get_settings()
    if bool(settings['is_testnet_bridge']) == True:
        return 'https://rpc.ankr.com/eth_goerli'
    else:
        return 'https://eth.llamarpc.com'

def get_zora_rpc_for_mint() -> str:
    settings = get_settings()
    if bool(settings['is_testnet_mint']) == True:
        return 'https://testnet.rpc.zora.energy'
    else:
        return 'https://rpc.zora.energy'

def get_eth_rpc_for_mint() -> str:
    settings = get_settings()
    if bool(settings['is_testnet_mint']) == True:
        return 'https://rpc.ankr.com/eth_goerli'
    else:
        return 'https://eth.llamarpc.com'

def get_bridge_contract_address() -> str:
    settings = get_settings()
    if bool(settings['is_testnet_bridge']) == True:
        return '0xDb9F51790365e7dc196e7D072728df39Be958ACe'
    else:
        return '0x1a0ad011913A150f69f6A19DF447A0CfD9551054'

def get_minter_address() -> str:
    settings = get_settings()
    if bool(settings['is_testnet_mint']) == True:
        return '0xd81351363b7d80b06e4ec4de7989f0f91e41a846'
    else:
        return '0x169d9147dfc9409afa4e558df2c9abeebc020182'

def get_price_stategy_address() -> str:
    settings = get_settings()
    if bool(settings['is_testnet_mint']) == True:
        return '0xd81351363b7d80b06E4Ec4De7989f0f91e41A846'
    else:
        return '0x169d9147dfc9409afa4e558df2c9abeebc020182'