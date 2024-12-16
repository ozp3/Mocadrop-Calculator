from web3 import Web3

def resolve_ens_name(ens_name, provider_url="https://rpc.ankr.com/eth"):
    """
    Resolves an ENS name to an EVM address using Web3.

    :param ens_name: str, ENS name (e.g., vitalik.eth)
    :param provider_url: str, Ethereum RPC URL
    :return: dict, success status and resolved EVM address or error message
    """
    try:
        # Connect to Ethereum node
        w3 = Web3(Web3.HTTPProvider(provider_url))

        # Check if the provider is connected
        if not w3.provider.is_connected():
            raise ConnectionError("Unable to connect to Ethereum network.")

        # Activate ENS resolution
        if not hasattr(w3, 'ens'):
            raise AttributeError("ENS resolution is not supported by this provider.")

        # Resolve ENS to EVM address
        resolved_address = w3.ens.address(ens_name)
        if resolved_address:
            return {"success": True, "address": resolved_address}
        else:
            return {"success": False, "error": f"No EVM address found for ENS name: {ens_name}"}

    except Exception as e:
        return {"success": False, "error": f"Error resolving ENS name: {str(e)}"}

def resolve_ens_or_evm_address(input_value, provider_url="https://rpc.ankr.com/eth"):
    """
    Resolves ENS name to EVM address or validates the EVM address if provided.

    :param input_value: str, ENS name (e.g., vitalik.eth) or EVM address
    :param provider_url: str, Ethereum node provider URL
    :return: dict, success status and resolved EVM address or error message
    """
    try:
        w3 = Web3(Web3.HTTPProvider(provider_url))
        if not w3.provider.is_connected():
            return {"success": False, "error": "Unable to connect to Ethereum network."}

        # Check if input is an ENS name
        if input_value.endswith(".eth"):
            return resolve_ens_name(input_value, provider_url)

        # Validate EVM address
        elif w3.is_address(input_value):
            return {"success": True, "type": "EVM", "address": input_value}

        # Invalid input
        return {"success": False, "error": "Invalid input. Please enter a valid ENS name or EVM address."}

    except Exception as e:
        return {"success": False, "error": f"Error resolving ENS/EVM address: {str(e)}"}
