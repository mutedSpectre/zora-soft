"""! @brief Defines the settings class."""
##
# @file Settings.py
#
# @brief Defines the settings class.
#
# @section description_settings Description
# Provide settings from object.
#
# @section author_settings Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/24/2023.

class Settings:
    def __init__(
        self, 
        nft_contract: str,
        nft_id: str,
        mint_price: float, 
        gas_price_for_mint: float, 
        gas_for_mint: int, 
        max_gas_in_gwei: int,
        bridge_amount: float,
        accuracy_in_amount_for_bridge: float,
        testnet: bool
    ):
        self.NFT_CONTRACT = nft_contract
        self.NFT_ID = nft_id
        self.MINT_PRICE = mint_price
        self.GAS_PRICE_FOR_MINT = gas_price_for_mint
        self.GAS_FOR_MINT = gas_for_mint
        self.MAX_GAS_IN_GWEI = max_gas_in_gwei
        self.BRIDGE_AMOUNT = bridge_amount
        self.ACCURACY_IN_AMOUNT_FOR_BRIDGE = accuracy_in_amount_for_bridge
        self.IS_TESTNET = testnet
        if self.IS_TESTNET == True:
            self.ZORA_RPC = 'https://testnet.rpc.zora.energy'
            self.ETH_RPC = 'https://rpc.ankr.com/eth_goerli'
            self.BRIDGE_CONTRACT = '0xDb9F51790365e7dc196e7D072728df39Be958ACe'
            self.MINTER_ADDR = '0xd81351363b7d80b06e4ec4de7989f0f91e41a846'
        else:
            self.ZORA_RPC = 'https://rpc.zora.energy'
            self.ETH_RPC = 'https://eth.llamarpc.com'
            self.BRIDGE_CONTRACT = '0x1a0ad011913A150f69f6A19DF447A0CfD9551054'
            self.MINTER_ADDR = '0x169d9147dfc9409afa4e558df2c9abeebc020182'