import pyotp
from addition.utils import generate_code_for_google_authenticator

def google_authenticator(username: str):
    secret_key = generate_code_for_google_authenticator()
    return {
        "secretKey": secret_key,
        "qrcodeData": pyotp.TOTP(secret_key).provisioning_uri(name=f"code@MybotTech{username.upper()}", issuer_name=f"MybotTech{username.upper()}"),
    }
