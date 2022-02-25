import pytest
import asyncio
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException
from sympy import symmetrize
from utils.utils import Signer, uint, str_to_felt, MAX_UINT256, assert_revert
from starkware.starknet.business_logic.state import BlockInfo


contract_signer = Signer(123456789987654321)
erc20_signer = Signer(987654321123456789)
sender_signer = Signer(111111111111111111)

@pytest.fixture(scope="module")
def event_loop():
    return asyncio.new_event_loop()


TEST_TOKEN_NAME = "STR Token"
TEST_TOKEN_SYMBOL = "STK"
TEST_TOKEN_SUPPLY = 1000
DECIMALS = 10 ** 4


@pytest.fixture(scope="module")
async def contract_factory():
    starknet = await Starknet.empty()
  
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

    erc20 = await starknet.deploy(
        "contracts/token/ERC20.cairo",
        constructor_calldata=[
            str_to_felt(TEST_TOKEN_NAME),  # name
            str_to_felt(TEST_TOKEN_SYMBOL),  # symbol
            *uint(TEST_TOKEN_SUPPLY),  # initial_supply
            erc20_account.contract_address,  # recipient
        ],
    )
    return starknet, erc20, contract_holder, erc20_account, contract_account, sender_account

UNIT = 1  # 10**126

def get_felt(value):
    return int(UNIT * value)


@pytest.mark.asyncio
async def test_contract_deposit(contract_factory):
    _, erc20, contract_holder, erc20_account, contract_account, sender_account  = contract_factory

    deposit_amount = uint(100)

    

    # first transfer test token to sender account
    return_bool = await erc20_signer.send_transaction(
        erc20_account,
        erc20.contract_address,
        "transfer",
        [sender_account.contract_address, *deposit_amount],
    )
    assert return_bool.result.response == [1]

    execution_info = await erc20.balanceOf(sender_account.contract_address).call()
    assert execution_info.result.balance == uint(100)

    #approve spending
    execution_info = await sender_signer.send_transaction(
        sender_account,
        erc20.contract_address,
        "approve",
        [
            contract_holder.contract_address,
            *deposit_amount,
        ],
    )

    # check that correct amount is allowed
    pool_allowance = await erc20.allowance(
        sender_account.contract_address, contract_holder.contract_address
    ).call()
    assert pool_allowance.result == ((100, 0),)

    execution_info = await sender_signer.send_transaction(
        sender_account,
        contract_holder.contract_address,
        "contract_deposit",
        [
            sender_account.contract_address,
            *deposit_amount,
            erc20.contract_address,
        ],
    )

   