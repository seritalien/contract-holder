import pytest
from starkware.starknet.business_logic.state import BlockInfo
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from utils import ERC20_DECIMALS, from_uint, get_erc20_uint_amount


USER_DEPOSIT = 512340014.5674987897441654

@pytest.mark.asyncio
async def test_contract_deposit(contract_factory, signers):
    _, erc20, contract_holder, _, _, sender_account  = contract_factory
    _, _, sender_signer = signers
    deposit_amount = get_erc20_uint_amount(USER_DEPOSIT)

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
    assert pool_allowance.result == ((deposit_amount),)
    print(f"ERC20 Pool allowance = {str(pool_allowance.result)}")

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

    execution_info = await erc20.balanceOf(contract_holder.contract_address).call()
    assert execution_info.result.balance == deposit_amount
    print(f"Contract holder balance = {execution_info.result.balance}")

   