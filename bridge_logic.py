"""! @brief Defines the balance logic methods."""
##
# @file balance_logic.py
#
# @brief Defines the balance logic methods.
#
# @section description_balance_logic Description
# Defines the balance logic methods by which balances on both 
# networks are checked, and makes a bridge if necessary.
#
# @section libraries_balance_logic Libraries/Modules
# - access to Any type
# - access to web3
# - standart time library (https://docs.python.org/3/library/time.html)
# - access to Logger type
# - access to abi necessary contracts
# - stadart random library (https://docs.python.org/3/library/random.html)
# - access to helpers
# - access to accounts module
# - access to ChecksumAddress type
#
# @section author_balance_logic Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/25/2023.

# Imports
from typing import Any
from ens.ens import ChecksumAddress
from web3 import Web3
import time
from web3.types import Wei
from Logger import Logger
from abi import bridge_abi
import random
import helpers
from accounts import turn_off_account_bridge

# Functions
def start_bridge_callback(sender: Any, app_data: Any, user_data: Logger) -> None:
    """ Start bridge logic callback.
    
    @param sender    Sender of the callback
    @param app_data  Data from the callback
    @param user_data User data from the callback
    """
    logger_bridge = user_data
    logger_bridge.all_info_log('Bridge! Bridge! Bridge!')

    # Get accounts
    for account in helpers.get_shuffled_accounts():
        if bool(account['bridge']) == True:
            try:
                bridge_status = bridge_logic(account, helpers.get_settings(), logger_bridge)
            except Exception as e:
                logger_bridge.error_log(account['address'], e)
                break

            if bridge_status == True:
                logger_bridge.info_log(account['address'], f'Bridge tx sended. Wait for bridge ~2 min.')
                turn_off_account_bridge(account.name)
                logger_bridge.info_log(account['address'], f'Account bridge turned off.')
            else:
                logger_bridge.error_log(account['address'], f'Bridge failed. Work at the address has stopped.')

    logger_bridge.all_info_log('All wallets bridged.')

def bridge_logic(
    account: Any, 
    settings: Any, 
    logger: Logger
    ) -> bool:
    """ Main balance logic method.
    
    @param account  Row from CSV with account data
    @param settings Global settings provided from UI
    @param logger   Logger object for push messages in logger window

    @return Boolean value denoting the status of the balance logic
    """

    # Web3 provider
    if isinstance(account['proxy'], str) and account['proxy'] != '':
        w3_eth = Web3(Web3.HTTPProvider(helpers.get_eth_rpc_for_bridge(), request_kwargs={'proxies':{'https': 'http://' + account['proxy'], 'http': 'http://' + account['proxy']}}))
    else:
        w3_eth = Web3(Web3.HTTPProvider(helpers.get_eth_rpc_for_bridge()))

    balance_eth_in_wei = w3_eth.eth.get_balance(Web3.to_checksum_address(account['address']))
    logger.info_log(account['address'], f'Balance on Ethereum is {Web3.from_wei(balance_eth_in_wei, "ether")} eth.')

    logger.info_log(account['address'], f'Enough funds on Ethereum. Checking whether the transferred amount can be transferred.')

    while True:
        gas_price = w3_eth.from_wei(w3_eth.eth.gas_price, 'gwei')
        logger.info_log(account['address'], f'Gas price is {gas_price} gwei')

        if gas_price < float(settings['max_gas_in_gwei']):
            logger.info_log(account['address'], f'Gas price is lower than {settings["max_gas_in_gwei"]} gwei from settings.')
            break
        time.sleep(5)

    decimal_places_min = len(str(settings['min_amount_for_bridge']).split('.')[1])
    decimal_places_max = len(str(settings['max_amount_for_bridge']).split('.')[1])
    decimal_places = max(decimal_places_min, decimal_places_max)
    random_number = random.uniform(float(settings['min_amount_for_bridge']), float(settings['max_amount_for_bridge']))
    format_string = "{:."+str(decimal_places)+"f}"
    formatted_number = float(format_string.format(random_number))

    bridge_amount_in_wei = Web3.to_wei(float(formatted_number), 'ether')

    # bridge bridge_amount_in_wei value
    logger.info_log(account['address'], f'Bridge amount is {Web3.from_wei(bridge_amount_in_wei, "ether")} eth.')
    bridge_status = bridge_from_eth_to_zora(
        address=       Web3.to_checksum_address(account['address']), 
        private_key=   account['private_key'], 
        bridge_amount= bridge_amount_in_wei,
        w3_eth=        w3_eth,
        settings=      settings,
        logger=        logger)

    return bridge_status

def bridge_from_eth_to_zora(
    address: ChecksumAddress, 
    private_key: str, 
    bridge_amount: Wei, 
    w3_eth: Web3, 
    settings: Any, 
    logger: Logger
)->bool:
    """ Send bridge transaction from ethereum to zora

    @param address       Checksum address of account
    @param private_key   Private key from account
    @param bridge_amount Amount for bridge in Ethereum to Zora
    @param w3_eth        Web3 provider for ethereum
    @param settings      Global settings provided from UI
    @param logger        Logger object for push messages in logger window

    @return Bridge tx status
    """

    # depositTransaction(
    #   address _to, // Target address on L2.
    #   uint256 _value, // ETH value to send to the recipient.
    #   uint64  _gasLimit, // Minimum L2 gas limit (can be greater than or equal to this value).
    #   bool    _isCreation, // Whether or not the transaction is a contract creation.
    #   bytes   _data // Data to trigger the recipient with.
    # )
    bridge_address = Web3.to_checksum_address(helpers.get_bridge_contract_address())
    bridge_contract = w3_eth.eth.contract(address=bridge_address, abi=bridge_abi)

    gas = bridge_contract.functions.depositTransaction(
        address,
        bridge_amount,
        100000,
        False,
        Web3.to_bytes(text='')
    ).estimate_gas({
        'from':  address, 
        'value': bridge_amount, 
        'nonce': w3_eth.eth.get_transaction_count(address)
    })

    gas = int(gas * 1.2) # take accuracy

    if (gas + bridge_amount) > w3_eth.eth.get_balance(address):
        logger.error_log(address, 'Insufficient funds including gas.')
        return False

    tx_raw = bridge_contract.functions.depositTransaction(
        address,
        bridge_amount,
        100000,
        False,
        Web3.to_bytes(text='')
    ).build_transaction({
        'from':     address,
        'value':    bridge_amount,
        'gas':      gas,
        'gasPrice': w3_eth.eth.gas_price,
        'nonce':    w3_eth.eth.get_transaction_count(address)
    })

    logger.info_log(address, f'Sending a transaction for bridge.')

    account = w3_eth.eth.account.from_key(private_key)
    signed_transaction = account.sign_transaction(tx_raw)
    transaction_hash = w3_eth.eth.send_raw_transaction(signed_transaction.rawTransaction)
    transaction_data = w3_eth.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)

    if transaction_data.get('status') != None and transaction_data.get('status') == 1:
        logger.info_log(address, f'Transaction hash on Ethereum: {transaction_hash.hex()}')

        return True
    else:
        logger.error_log(address, f'Transaction bridge failed. Work at the address has stopped.')
        return False