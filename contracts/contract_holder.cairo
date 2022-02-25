%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin, SignatureBuiltin
from starkware.starknet.common.syscalls import get_contract_address, get_caller_address
from contracts.token.IERC20 import IERC20
from contracts.utils.constants import TRUE, FALSE
from contracts.token.ERC20_base import ERC20_transfer, ERC20_transferFrom, ERC20_approve
from starkware.cairo.common.uint256 import Uint256, uint256_signed_nn_le
from starkware.cairo.common.math import split_felt

@storage_var
func contract_owner_account() -> (owner : felt):
end

@constructor
func constructor{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(owner : felt):
    contract_owner_account.write(owner)
    return ()
end

@external
func contract_deposit{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        sender_account : felt, deposit_amount : Uint256, token_address : felt) -> ():
    alloc_locals

    with_attr error_message("Deposit Amount must be positive."):
        let (local asserted) = uint256_signed_nn_le(Uint256(0, 0), deposit_amount)
        assert asserted = 1
    end

    let (local contract_address) = get_contract_address()
    let (local contract_account) = contract_owner_account.read()

    IERC20.transferFrom(
        contract_address=token_address,
        sender=sender_account,
        recipient=contract_address,
        amount=deposit_amount)

    return ()
end

func _felt_to_Uint256{range_check_ptr}(number : felt) -> (number : Uint256):
    alloc_locals
    let (local _number_high, local _number_low) = split_felt(number)
    let number256 : Uint256 = Uint256(_number_high, _number_low)
    return (number256)
end
