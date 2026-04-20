from .get_keys import load_valid_dhan_credentials
from dhanhq import dhanhq


def get_nearest_strike_data(option_chain_json, target_price):
    try:
        oc_data = option_chain_json["data"]["data"]["oc"]

        strikes = [float(k) for k in oc_data.keys()]
        nearest_strike = min(strikes, key=lambda x: abs(x - target_price))
        strike_key = f"{nearest_strike:.6f}"

        strike_data = oc_data[strike_key]

        ce = strike_data.get("ce", {})
        pe = strike_data.get("pe", {})

        return {
            "nearest_strike": nearest_strike,
            "ce_security_id": ce.get("security_id"),
            "ce_price": ce.get("last_price"),
            "pe_security_id": pe.get("security_id"),
            "pe_price": pe.get("last_price"),
        }

    except Exception as e:
        return {"error": str(e)}


def get_option_contract(security_id, option_type):
    """
    security_id → index (13 / 51)
    option_type → buyCE / buyPE
    """

    try:
        creds = load_valid_dhan_credentials()
        dhan_instance = dhanhq(creds['client_id'], creds['access_token'])

        # STEP 1: expiry
        expiry_data = dhan_instance.expiry_list(
            under_security_id=int(security_id),
            under_exchange_segment="IDX_I"
        )

        expiry = expiry_data.get("data", {}).get("data", [])[0]

        # STEP 2: option chain
        oc = dhan_instance.option_chain(
            under_security_id=int(security_id),
            under_exchange_segment="IDX_I",
            expiry=expiry
        )

        # STEP 3: spot price
        spot_price = oc.get("data", {}).get("data", {}).get("last_price")

        # STEP 4: nearest strike
        result = get_nearest_strike_data(oc, spot_price)

        if "error" in result:
            return result

        # STEP 5: return correct contract
        if option_type == "buyCE":
            return {
                "security_id": result["ce_security_id"],
                "price": result["ce_price"],
                "strike": result["nearest_strike"]
            }

        elif option_type == "buyPE":
            return {
                "security_id": result["pe_security_id"],
                "price": result["pe_price"],
                "strike": result["nearest_strike"]
            }

        else:
            return {"error": "Invalid option type"}

    except Exception as e:
        return {"error": str(e)}