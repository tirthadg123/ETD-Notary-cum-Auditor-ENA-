from web3 import Web3
import solcx
from solcx import compile_standard, install_solc
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
if not w3.is_connected():
    print("Failed to connect to Ganache. Is it running?")
    exit()
print("Connected to Local Open-Source Blockchain!")
admin_account = w3.eth.accounts[0]
print(f"University Admin Wallet: {admin_account}")
print("Compiling Smart Contract...")
install_solc("0.8.0") # Install compiler
with open("notary.sol", "r") as file:
    contract_source_code = file.read()
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"notary.sol": {"content": contract_source_code}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}}},
    },
    solc_version="0.8.0",
)
bytecode = compiled_sol["contracts"]["notary.sol"]["ETDNotary"]["evm"]["bytecode"]["object"]
abi = compiled_sol["contracts"]["notary.sol"]["ETDNotary"]["abi"]
print("Deploying Contract to the Ledger...")
NotaryContract = w3.eth.contract(abi=abi, bytecode=bytecode)
transaction = NotaryContract.constructor().build_transaction(
    {
        "chainId": 1337,
        "gasPrice": w3.eth.gas_price,
        "from": admin_account,
        "nonce": w3.eth.get_transaction_count(admin_account),
    }
)
tx_hash = NotaryContract.constructor().transact({'from': admin_account})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress
print("\n" + "="*50)
print("SMART CONTRACT SUCCESSFULLY DEPLOYED!")
print(f"Contract Address: {contract_address}")
print("Save this address. Your DSpace connector will need it!")
print("="*50 + "\n")
