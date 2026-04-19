from dhanhq import dhanhq
from .auth import load_valid_dhan_credentials


def get_dhan_client():
    creds = load_valid_dhan_credentials()

    if not creds:
        print("❌ No valid credentials")
        return None

    try:
        client = dhanhq(creds["client_id"], creds["access_token"])
        return client
    except Exception as e:
        print("❌ Dhan init error:", e)
        return None