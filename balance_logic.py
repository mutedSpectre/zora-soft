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
# - access to Settings type
# - access to abi necessary contracts
# - stadart random library (https://docs.python.org/3/library/random.html)
#
# @section author_balance_logic Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/24/2023.

# Imports
from typing import Any
from ens.ens import ChecksumAddress
from web3 import Web3
import time
from web3.types import Wei
from Logger import Logger
from Settings import Settings
from abi import bridge_abi
import random

# Functions
def calculate_zora_fee_in_wei(
    mint_price: float, 
    gas_price_for_mint: float, 
    gas_for_mint: int, 
    w3_eth: Web3, 
    testnet: bool
    ) -> int:
    """ Calculate zora fee method
    
    @param mint_price         Price for mint (default Zora price is 0.000777 ETH)
    @param gas_price_for_mint Price for gas in Zora Network
    @param gas_for_mint       Gas amount for tx 'mint' (av. 130-160k)
    @param w3_eth             Web3 provider for ethereum (needed for testnet)
    @param testnet            Use testnet, or no

    @return Required amount of eth for minting on Zora Network
    """

    # Calculate mint_price ETH to wei
    zora_mint_fee = int(Web3.to_wei(mint_price, 'ether'))

    if testnet == False:
        # Calculate gas_price_for_mint gwei to wei * gas_for_mint + L1 gas price * 4000 * gas fee scalar
        zora_gas_fee = Web3.to_wei(gas_price_for_mint, 'gwei') * int(gas_for_mint) + int(w3_eth.eth.gas_price * 4000 * 0.684)
    else:
        # testnet zora have 1:1 gas fee scalar
        zora_gas_fee = Web3.to_wei(gas_price_for_mint, 'gwei') * int(gas_for_mint) + w3_eth.eth.gas_price * 6000

    return zora_mint_fee + zora_gas_fee


def balance_logic(
    account: Any, 
    settings: Settings, 
    logger: Logger
    ) -> bool:
    """ Main balance logic method.
    
    @param account  Row from CSV with account data
    @param settings Global settings provided from UI
    @param logger   Logger object for push messages in logger window

    @return Boolean value denoting the status of the balance logic
    """

    # Web3 provider
    if isinstance(account['proxy'], str):
        w3_zora = Web3(Web3.HTTPProvider(settings.ZORA_RPC, request_kwargs={'proxies':{'https': account['proxy'], 'http': account['proxy']}}))
        w3_eth = Web3(Web3.HTTPProvider(settings.ETH_RPC, request_kwargs={'proxies':{'https': account['proxy'], 'http': account['proxy']}}))
    else:
        w3_zora = Web3(Web3.HTTPProvider(settings.ZORA_RPC))
        w3_eth = Web3(Web3.HTTPProvider(settings.ETH_RPC))

    balance_zora = w3_zora.eth.get_balance(Web3.to_checksum_address(account['address']))
    logger.info_log(account['address'], f'Balance on Zora Network is {Web3.from_wei(balance_zora, "ether")} eth.')

    zora_fee_in_wei = calculate_zora_fee_in_wei(settings.MINT_PRICE, settings.GAS_PRICE_FOR_MINT, settings.GAS_FOR_MINT, w3_eth, settings.IS_TESTNET)
    logger.info_log(account['address'], f'Fee: {Web3.from_wei(zora_fee_in_wei, "ether")} eth')

    if balance_zora < zora_fee_in_wei:
        logger.warning_log(account['address'], f'Insufficient funds on Zora Network.')

        balance_eth_in_wei = w3_eth.eth.get_balance(Web3.to_checksum_address(account['address']))
        logger.info_log(account['address'], f'Balance on Ethereum is {Web3.from_wei(balance_eth_in_wei, "ether")} eth.')

        if balance_eth_in_wei < zora_fee_in_wei:
            logger.error_log(account['address'], f'Insufficient funds on Ethereum. Work at the address has stopped.')
            return False
        else:
            logger.info_log(account['address'], f'Enough funds on Ethereum. Checking whether the transferred amount can be transferred.')

            while True:
                gas_price = w3_eth.from_wei(w3_eth.eth.gas_price, 'gwei')
                logger.info_log(account['address'], f'Gas price is {gas_price} gwei')

                if gas_price < float(settings.MAX_GAS_IN_GWEI):
                    logger.info_log(account['address'], f'Gas price is lower than {settings.MAX_GAS_IN_GWEI} gwei from settings.')
                    break
                time.sleep(5)

            # Accuracy bridge amount logic
            ## Get random number in human-like format. So that 0.002 becomes 0.001 instead of 0.0014325234.
            decimal_places = len(str(settings.ACCURACY_IN_AMOUNT_FOR_BRIDGE).split('.')[1])
            random_number = random.uniform(0, float(settings.ACCURACY_IN_AMOUNT_FOR_BRIDGE))
            format_string = "{:."+str(decimal_places)+"f}"
            formatted_number = float(format_string.format(random_number))
            logger.info_log(account['address'], f'Random number is {formatted_number}')

            ## Randomize action
            action = random.choice(['+', '-'])
            if action == '+':
                bridge_amount_in_wei = Web3.to_wei(float(settings.BRIDGE_AMOUNT) + formatted_number, 'ether')
            else:
                bridge_amount_in_wei = Web3.to_wei(float(settings.BRIDGE_AMOUNT) - formatted_number, 'ether')

            if (bridge_amount_in_wei < balance_eth_in_wei) & (bridge_amount_in_wei > zora_fee_in_wei):
                # bridge bridge_amount_in_wei value
                logger.info_log(account['address'], f'Bridge amount is {Web3.from_wei(bridge_amount_in_wei, "ether")} eth.')
                bridge_status = bridge_from_eth_to_zora(
                    address=       Web3.to_checksum_address(account['address']), 
                    private_key=   account['private_key'], 
                    bridge_amount= bridge_amount_in_wei,
                    w3_eth=        w3_eth,
                    settings=      settings,
                    logger=        logger)
            else:
                # bridge zora_fee value only
                logger.info_log(account['address'], f'Bridge amount is {Web3.from_wei(zora_fee_in_wei, "ether")} eth.')
                bridge_status = bridge_from_eth_to_zora(
                    address=       Web3.to_checksum_address(account['address']), 
                    private_key=   account['private_key'], 
                    bridge_amount= Wei(zora_fee_in_wei),
                    w3_eth=        w3_eth,
                    settings=      settings,
                    logger=        logger)
            
            return bridge_status
    else:
        return True

def bridge_from_eth_to_zora(
    address: ChecksumAddress, 
    private_key: str, 
    bridge_amount: Wei, 
    w3_eth: Web3, 
    settings: Settings, 
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
    bridge_address = Web3.to_checksum_address(settings.BRIDGE_CONTRACT)
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