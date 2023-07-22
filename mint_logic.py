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
# - access to Settings type
# - access to abi NFT contract
# - access to method for calculating fee from balance logic
#
# @section author_mint_logic Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/22/2023.
#
# Copyright (c) 2023 mutedspectre.eth. All rights reserved.

# Imports
from typing import Any
from web3 import Web3
from Logger import Logger
from Settings import Settings
from balance_logic import calculate_zora_fee_in_wei
import time
from abi import nft_abi

#Functions
def mint_logic(
    account: Any, 
    settings: Settings, 
    logger: Logger
)->bool:
    """ Main mint logic method.
    
    @param account  Row from CSV with account data
    @param settings Global settings provided from UI
    @param logger   Logger object for push messages in logger window

    @return Boolean value denoting the status of the mint logic
    """

    # Providers
    if isinstance(account['proxy'], str):
        w3_zora = Web3(Web3.HTTPProvider(settings.ZORA_RPC, request_kwargs={'proxies':{'https': account['proxy'], 'http': account['proxy']}}))
        w3_eth = Web3(Web3.HTTPProvider(settings.ETH_RPC, request_kwargs={'proxies':{'https': account['proxy'], 'http': account['proxy']}}))
    else:
        w3_zora = Web3(Web3.HTTPProvider(settings.ZORA_RPC))
        w3_eth = Web3(Web3.HTTPProvider(settings.ETH_RPC))

    fee = calculate_zora_fee_in_wei(settings.MINT_PRICE, settings.GAS_PRICE_FOR_MINT, settings.GAS_FOR_MINT, w3_eth, settings.IS_TESTNET)

    while True:
        balance_zora = w3_zora.eth.get_balance(account['address'])
        if balance_zora >= fee:
            break
        logger.info_log(account['address'], f'Waiting for bridge confirmation on Zora Network. Re-verify after 30 seconds.')
        time.sleep(30)

    nft_address = Web3.to_checksum_address(settings.NFT_CONTRACT)
    nft_contract = w3_zora.eth.contract(address=nft_address, abi=nft_abi)

    tx_raw = nft_contract.functions.mint(
        Web3.to_checksum_address(settings.MINTER_ADDR),
        int(settings.NFT_ID),
        1,
        Web3.to_hex(b'\x00' * 12 + Web3.to_bytes(hexstr=account['address']))
    ).build_transaction({
        'from': account['address'],
        'value': w3_zora.to_wei(settings.MINT_PRICE, 'ether'),
        'gas': int(settings.GAS_FOR_MINT),
        'gasPrice': w3_zora.to_wei(settings.GAS_PRICE_FOR_MINT, 'gwei'),
        'nonce': w3_zora.eth.get_transaction_count(account['address'])
    })

    logger.info_log(account['address'], f'Sending a transaction for minting.')

    account_web3 = w3_zora.eth.account.from_key(account['private_key'])
    signed_transaction = account_web3.sign_transaction(tx_raw)
    transaction_hash = w3_zora.eth.send_raw_transaction(signed_transaction.rawTransaction)
    transaction_data = w3_zora.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)

    logger.info_log(account['address'], f'Transaction hash on Zora Network: {transaction_hash.hex()}')
    if transaction_data.get('status') != None and transaction_data.get('status') == 1:
        return True
    else:
        return False
