from utils import ERC20_DECIMALS, from_uint, get_erc20_uint_amount


def test_uint(user_deposit):
    print(f"initial user_deposit = {user_deposit}")
    u = get_erc20_uint_amount(user_deposit)
    print(f"Uint deposit Amount * ERC20DECIMALS ={u}")
    nu = from_uint(u)
    print(f"INT deposit Amount * ERC20DECIMAS ={nu}")
    ru = nu/ERC20_DECIMALS
    print(f"reconverted user_deposit {ru}")
    assert user_deposit==ru