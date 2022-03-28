import pytest
import asyncio
from starkware.starknet.testing.starknet import Starknet
from utils  import Signer, get_erc20_uint_amount, uint, str_to_felt, ERC20_DECIMALS
@pytest.fixture(scope="module")
def user_deposit():
    return 51234.56789


TEST_TOKEN_NAME = "STR Token"
TEST_TOKEN_SYMBOL = "STK"
TEST_TOKEN_SUPPLY_9BILLION = get_erc20_uint_amount(9000000000)

@pytest.fixture(scope="module")
def event_loop():
    return asyncio.new_event_loop()

@pytest.fixture(scope="module")
def signers():
    contract_signer = Signer(123456789987654321)
    erc20_signer = Signer(987654321123456789)
    sender_signer = Signer(111111111111111111)
    return contract_signer, erc20_signer, sender_signer

@pytest.fixture(scope="module")
async def contract_factory(signers):
    starknet = await Starknet.empty()
    contract_signer, erc20_signer, sender_signer = signers
  
    erc20_account = await starknet.deploy(
        "contracts/Account.cairo", constructor_calldata=[erc20_signer.public_key]
    )
    
    contract_account = await starknet.deploy(
        "contracts/Account.cairo", constructor_calldata=[contract_signer.public_key]
    )
    
    sender_account = await starknet.deploy(
        "./contracts/Account.cairo",
        constructor_calldata=[sender_signer.public_key],
    )

    contract_holder = await starknet.deploy(
        "./contracts/contract_holder.cairo",
        constructor_calldata=[contract_account.contract_address],
    )

    initial_supply = TEST_TOKEN_SUPPLY_9BILLION
    erc20 = await starknet.deploy(
        "contracts/token/ERC20.cairo",
        constructor_calldata=[
            str_to_felt(TEST_TOKEN_NAME),  # name
            str_to_felt(TEST_TOKEN_SYMBOL),  # symbol
            *initial_supply,
            erc20_account.contract_address,  # recipient
        ],
    )

    deposit_amount = TEST_TOKEN_SUPPLY_9BILLION

    # first transfer test token to sender account
    return_bool = await erc20_signer.send_transaction(
        erc20_account,
        erc20.contract_address,
        "transfer",
        [sender_account.contract_address, *deposit_amount],
    )
    assert return_bool.result.response == [1]

    execution_info = await erc20.balanceOf(sender_account.contract_address).call()
    assert execution_info.result.balance == deposit_amount

    return starknet, erc20, contract_holder, erc20_account, contract_account, sender_account

