import requests
import json
from typing import Mapping, List

CHAIN_ID_MAP = {
    "1": "ethereum",
    "10": "optimism",
    "56": "bnb",
    "137": "polygon",
    "169": "manta-pacific",
    "196": "xlayer",
    "314": "filecoin-evm",
    "324": "zksync-era",
    "1100": "dym",
    "4200": "merlin",
    "7000": "zeta-evm",
    "42161": "arbitrum",
    "43114": "avax",
    "42766": "zkfair",
    "81457": "blast",
    "80085": "bera-artio",
}

NATIVE_COIN_MAP = {
    "arbitrum": "ETH",
    "avax": "AVAX",
    "ethereum": "ETH",
    "optimism": "ETH",
    "bnb": "BNB",
    "polygon": "MATIC",
    "zksync-era": "ETH",
    "zeta-evm": "ZETA",
    "zkfair": "USDC",
    "bera-artio": "BERA",
    "filecoin-evm": "FIL",
    "merlin": "BTC",
    "coreum": "COREUM",
    "dym": "DYM",
    "xlayer": "OKB",
}

def update_tokens(new_tokens: Mapping[str, List]):
    for chain, tokens in new_tokens.items():
        origin_tokens = []
        origin_addrs = set()
        try:
            with open(f"{chain}.json", "r") as reader:
                origin_tokens = json.load(reader)
            for t in origin_tokens:
                origin_addrs.add(t["address"].lower())
            new_tokens = origin_tokens
            for t in tokens:
                if t["address"].lower() in origin_addrs:
                    continue
                new_tokens.append(t)
            new_tokens = list(filter(lambda t: t.get("symbol", None) != NATIVE_COIN_MAP.get(chain, ""), new_tokens))
            with open(f"{chain}.json", "w") as writer:
                json.dump(new_tokens, writer, indent=2)
        except BaseException as e:
            print(chain, e)
            continue        

def izumi():
    data = requests.get("https://raw.githubusercontent.com/izumiFinance/izumi-tokenList/main/build/tokenList.json").json()
    result = {}
    for item in data:
        name = item["name"]
        symbol = item["symbol"]
        logoURI = item["icon"]
        contracts = item.get("contracts", {})
        for chain_id, v in contracts.items():
            chain = CHAIN_ID_MAP.get(chain_id, None)
            if chain is None:
                continue
            address = v["address"]
            decimals = v["decimal"]
            token = {
                "address": address,
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "logoURI": logoURI,
            }
            if not chain in result:
                result[chain] = []
            result[chain].append(token)
    update_tokens(result)


def bera_artio():
    data = requests.get("https://raw.githubusercontent.com/berachain/default-token-list/main/src/tokens/testnet/defaultTokenList.json").json()
    result = {
        "bera-artio": []
    }
    for item in data.get("tokens", []):
        token = {
            "address": item["address"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": item["decimals"],
            "logoURI": item["logoURI"],
        }
        result["bera-artio"].append(token)    
    update_tokens(result)

def coreum():
    data = requests.get("https://raw.githubusercontent.com/CoreumFoundation/token-registry/master/mainnet/assets.json").json()
    
    metadatas = requests.get("https://full-node.mainnet-1.coreum.dev:1317/cosmos/bank/v1beta1/denoms_metadata").json()
    metadata_map = {}
    for item in metadatas["metadatas"]:
        metadata_map[item["base"]] = item

    result = {
        "coreum": []
    }
    for item in data.get("assets", []):
        address = item["denom"]
        meta = metadata_map.get(address)
        ibc = item.get("ibc_info")
        if not meta and ibc.get("display_name") is None:
            continue
        if address == "ucore":
            continue
        token = {
            "address": address,
            "logoURI": item["logo_URIs"]["png"],
            "name": meta["name"] if meta else ibc["display_name"],
            "symbol": meta["symbol"] if meta else ibc["display_name"],
            "decimals": meta["denom_units"][-1]["exponent"] if meta else ibc["precision"],
        }
        result["coreum"].append(token)    
    update_tokens(result)

def one_inch():
    result = {}
    for chain_id in ["1", "10", "56", "137", "324", "42161", "43114"]:
        chain = CHAIN_ID_MAP.get(chain_id)
        if not chain:
            continue
        data = requests.get(f"https://tokens.1inch.io/v1.2/{chain_id}").json()
        for address, item in data.items():
            logoURI = item.get("logoURI")
            if not logoURI:
                continue
            token = {
                "address": address,
                "name": item["name"],
                "symbol": item["symbol"],
                "decimals": item["decimals"],
                "logoURI": logoURI,
            }
            if not chain in result:
                result[chain] = []
            result[chain].append(token)
    update_tokens(result)

def sushiswap():
    chain_map = {
        "filecoin": "filecoin-evm"
    }
    result = {}
    for c in ["filecoin", ]:
        chain = chain_map.get(c)
        if not chain:
            continue
        data = requests.get(f"https://raw.githubusercontent.com/sushiswap/list/master/lists/token-lists/default-token-list/tokens/{c}.json").json()
        for item in data:
            token = {
                "address": item["address"],
                "name": item["name"],
                "symbol": item["symbol"],
                "decimals": item["decimals"],
                "logoURI": item["logoURI"],
            }
            if chain not in result:
                result[chain] = []
            result[chain].append(token)
    update_tokens(result)


def merlinswap():
    result = {
        "merlin": []
    }
    data = requests.get("https://raw.githubusercontent.com/MerlinSwap/MerlinSwap-tokenList/main/build/tokenList.json").json()
    for item in data:
        contract = item["contracts"]["4200"]
        token = {
            "address": contract["address"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": contract["decimal"],
            "logoURI": item["icon"],
        }
        result["merlin"].append(token)
    update_tokens(result)

def uniswap():
    chain_map = {
        "mainnet": "ethereum",
        "optimism": "optimism",
        "bnb": "bnb",
        "polygon": "polygon",
        "arbitrum": "arbitrum",
    }
    result = {}
    for chain, unique_id in chain_map.items():
        print(chain)
        url = f"https://raw.githubusercontent.com/Uniswap/default-token-list/main/src/tokens/{chain}.json"
        data = requests.get(url).json()
        if unique_id not in result:
            result[unique_id] = []
        for token in data:
            del token["chainId"]
            result[unique_id].append(token)
    update_tokens(result)


def xlayer():
    unique_id = "xlayer"
    result = {
       unique_id : []
    }
    url = "https://rpc.xlayer.tech/priapi/v1/ob/bridge/main-coins/3"
    data = requests.get(url).json()
    for item in data.get("data", []):
        if not item["address"]:
            continue
        chainId = item["chainId"]
        if chainId != "196":
            continue
        token = {
            "address": item["address"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": int(item["decimals"]),
            "logoURI": item["logoLink"],
        }
        result[unique_id].append(token)
    update_tokens(result)    


if __name__ == "__main__":
    one_inch()