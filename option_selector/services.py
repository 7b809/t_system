import os
from core.get_keys import load_valid_dhan_credentials
from dhanhq import dhanhq

# ✅ SINGLE SOURCE OF TRUTH
BASIC_LOGS = os.getenv("BASIC_LOGS", "false").lower() == "true"


def log(msg):
    if BASIC_LOGS:
        print(msg)


def log_line():
    if BASIC_LOGS:
        print("-" * 40)

def get_nearest_strike_data(option_chain_json, target_price, option_type):
    try:
        oc_data = option_chain_json.get("data", {}).get("data", {}).get("oc", {})

        if not oc_data:
            return {"error": "Option chain data missing"}

        strikes = sorted([float(k) for k in oc_data.keys()])

        # 🎯 ALWAYS FLOOR (for both CE & PE)
        valid_strikes = [s for s in strikes if s <= target_price]
        nearest_strike = max(valid_strikes) if valid_strikes else strikes[0]

        strike_key = f"{nearest_strike:.6f}"
        strike_data = oc_data.get(strike_key, {})

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
        log_line()
        log(f"🔍 Fetching option contract | SecID={security_id} | Type={option_type}")

        # -----------------------------
        # 🔐 STEP 0: Credentials
        # -----------------------------
        log_line()

        creds = load_valid_dhan_credentials()

        if not creds:
            return {"error": "No valid credentials"}

        masked_client = creds["client_id"][:4] + "****"
        log(f"🔐 Using Client ID: {masked_client}")

        dhan_instance = dhanhq(creds['client_id'], creds['access_token'])

        # -----------------------------
        # 📅 STEP 1: Expiry
        # -----------------------------
        log_line()

        expiry_data = dhan_instance.expiry_list(
            under_security_id=int(security_id),
            under_exchange_segment="IDX_I"
        )

        log(f"📅 Expiry API Response: {expiry_data}")

        expiry_list = expiry_data.get("data", {}).get("data", [])

        if not expiry_list:
            return {"error": "No expiry data"}

        expiry = expiry_list[0]
        log(f"✅ Selected Expiry: {expiry}")

        # -----------------------------
        # 📊 STEP 2: Option Chain
        # -----------------------------
        log_line()

        oc = dhan_instance.option_chain(
            under_security_id=int(security_id),
            under_exchange_segment="IDX_I",
            expiry=expiry
        )

        log(f"📊 Option Chain Response received")

        oc_data = oc.get("data", {}).get("data", {})

        if not oc_data:
            return {"error": "Invalid option chain response"}

        # -----------------------------
        # 📈 STEP 3: Spot Price
        # -----------------------------
        log_line()

        spot_price = oc_data.get("last_price")

        if spot_price is None:
            return {"error": "Missing spot price"}

        log(f"📈 Spot Price: {spot_price}")

        # -----------------------------
        # 🎯 STEP 4: Nearest Strike
        # -----------------------------
        log_line()

        result = get_nearest_strike_data(oc, spot_price, option_type)

        log(f"🎯 Nearest Strike Data: {result}")

        if not isinstance(result, dict) or "error" in result:
            return {"error": result.get("error", "Invalid strike data")}

        # -----------------------------
        # 🧾 STEP 5: Select Contract
        # -----------------------------
        log_line()

        if option_type == "buyCE":
            sec_id = result.get("ce_security_id")
            price = result.get("ce_price")

        elif option_type == "buyPE":
            sec_id = result.get("pe_security_id")
            price = result.get("pe_price")

        else:
            return {"error": "Invalid option type"}

        # -----------------------------
        # ❌ FINAL VALIDATION
        # -----------------------------
        log_line()

        if not sec_id or price is None:
            return {"error": "Invalid contract data"}

        log(f"✅ Selected Contract → SecID: {sec_id}, Price: {price}")

        # -----------------------------
        # ✅ FINAL RESPONSE
        # -----------------------------
        log_line()

        return {
            "security_id": sec_id,
            "price": price,
            "strike": result.get("nearest_strike"),
            "spot_price": spot_price
        }

    except Exception as e:
        # 🔥 ALWAYS log errors
        print(f"❌ Exception in get_option_contract: {str(e)}")
        return {"error": str(e)}