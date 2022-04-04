import typing
import tronpy

def generate_usdt_trc20() -> typing.Dict:
    private_key = tronpy.tron.PrivateKey.random()
    return {
        "private_key": private_key.hex(),
        "address": private_key.public_key.to_base58check_address()
    }

if __name__ == '__main__':
    wallet = generate_usdt_trc20()
    print(wallet)