"""! @brief Defines the mint logic methods."""
##
# @file mint_logic.py
#
# @brief Defines the mint logic methods.
#
# @section description_mint_logic Description
# Defines the mint NFT logic methods 
#
# @section libraries_mint_logic Libraries/Modules
# - access to Any type
# - access to web3
# - standart time library (https://docs.python.org/3/library/time.html)
# - access to Logger type
# - access to helpers
# - access to accounts module
# - access to nft 1155 abi
#
# @section author_mint_logic Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/25/2023.

# Imports
from typing import Any
from web3 import Web3
from web3.types import Wei
from Logger import Logger
import helpers
import time
from abi import nft_1155_abi
import re
from accounts import turn_off_account_mint

#Functions
def start_mint_callback(sender: Any, app_data: Any, user_data: Logger) -> None:
    """ Start mint logic callback.
    
    
    @param sender    Sender of the callback
    @param app_data  Data from the callback
    @param user_data User data from the callback"""
    logger_mint = user_data
    logger_mint.all_info_log('Mint! Mint! Mint!')

    # Get accounts
    for account in helpers.get_shuffled_accounts():
        if account['mint'] == True:
            try:
                bridge_status = mint_logic(account, helpers.get_settings(), logger_mint)
            except Exception as e:
                logger_mint.error_log(account['address'], e)
                break

            if bridge_status == True:
                turn_off_account_mint(account.name)
                logger_mint.info_log(account['address'], f'Account mint turned off.')
            else:
                logger_mint.error_log(account['address'], f'Bridge failed. Work at the address has stopped.')

    logger_mint.all_info_log('All wallets minted.')

def mint_logic(
    account: Any, 
    settings: Any, 
    logger: Logger
)->bool:
    """ Main mint logic method.
    
    @param account  Row from CSV with account data
    @param settings Global settings provided from UI
    @param logger   Logger object for push messages in logger window

    @return Boolean value denoting the status of the mint logic
    """

    # Web3 provider
    if isinstance(account['proxy'], str) and account['proxy'] != '':
        w3_zora = Web3(Web3.HTTPProvider(helpers.get_zora_rpc_for_mint(), request_kwargs={'proxies':{'https': 'http://' + account['proxy'], 'http': 'http://' + account['proxy']}}))
        w3_eth = Web3(Web3.HTTPProvider(helpers.get_eth_rpc_for_mint(), request_kwargs={'proxies':{'https': 'http://' + account['proxy'], 'http': 'http://' + account['proxy']}}))
    else:
        w3_zora = Web3(Web3.HTTPProvider(helpers.get_zora_rpc_for_mint()))
        w3_eth = Web3(Web3.HTTPProvider(helpers.get_eth_rpc_for_mint()))

    # Check balance
    balance_zora = w3_zora.eth.get_balance(Web3.to_checksum_address(account['address']))
    logger.info_log(account['address'], f'Balance on Zora: {w3_zora.from_wei(balance_zora, "ether")} ETH.')

    # Get NFT info from url
    ## Check if NFT is for sale on Zora Network
    match = re.search(r'(zora|eth):([^/]+)', settings['nft_url'])
    if match:
        if match.group(1) == 'eth':
            logger.error_log(account['address'], f'NFT not found on Zora Network. It is for sale on Ethereum Network.')
            return False
    
    ## Get NFT address and id
    match = re.search(r'0x[^/]+', settings['nft_url'])
    if match:
        nft_address = Web3.to_checksum_address(match.group(0))
    else:
        logger.error_log(account['address'], f'NFT contract not found in url.')
        return False

    nft_id = settings['nft_url'].rsplit('/', 1)[-1]
    if nft_id.isdigit() == False:
        logger.error_log(account['address'], f'NFT id not found in url.')
        return False

    fee = helpers.calculate_zora_fee_in_wei(Web3.to_wei(settings['mint_price'], 'ether'), settings['gas_price_for_mint'], settings['gas_for_mint'], w3_eth, settings['is_testnet_mint'])

    logger.info_log(account['address'], f'NFT price with network fee: {format(w3_zora.from_wei(fee, "ether"), "f")} ETH.')

    ## Check if balance is enough
    while True:
        balance_zora = w3_zora.eth.get_balance(Web3.to_checksum_address(account['address']))
        if balance_zora >= fee:
            break
        logger.info_log(account['address'], f'Balance on Zora to low. Waiting for bridge confirmation on Zora Network. Re-verify after 30 seconds.')
        time.sleep(30)

    # Mint NFT
    nft_contract = w3_zora.eth.contract(address=nft_address, abi=nft_1155_abi)
    tx_raw = nft_contract.functions.mint(
        Web3.to_checksum_address(helpers.get_minter_address()),
        int(nft_id),
        1,
        Web3.to_hex(b'\x00' * 12 + Web3.to_bytes(hexstr=account['address']))
    ).build_transaction({
        'from': Web3.to_checksum_address(account['address']),
        'value': Web3.to_wei(settings['mint_price'], 'ether'),
        'gas': int(settings['gas_for_mint']),
        'gasPrice': w3_zora.to_wei(settings['gas_price_for_mint'], 'gwei'),
        'nonce': w3_zora.eth.get_transaction_count(Web3.to_checksum_address(account['address']))
    })

    logger.info_log(account['address'], f'Sending a transaction for minting.')

    account_web3 = w3_zora.eth.account.from_key(account['private_key'])
    signed_transaction = account_web3.sign_transaction(tx_raw)
    transaction_hash = w3_zora.eth.send_raw_transaction(signed_transaction.rawTransaction)
    transaction_data = w3_zora.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)

    if transaction_data.get('status') != None and transaction_data.get('status') == 1:
        logger.info_log(account['address'], f'Transaction hash on Zora Network: {transaction_hash.hex()}')
        return True
    else:
        logger.error_log(account['address'], f'Transaction failed on Zora Network.')
        return False
