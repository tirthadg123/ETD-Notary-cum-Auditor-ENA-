import requests
import json
import hashlib
import os
from web3 import Web3

DSPACE_API_URL = "http://localhost:8080/server/api"
DSPACE_EMAIL = "tirtharajdasgupta963@gmail.com" # Enter the DSpace e-mail id
DSPACE_PASSWORD = "dspace" # Enter the DSpace login password
GANACHE_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "" # Enter the contact address obtained upon notary deployment
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_uuid", "type": "string"},
            {"internalType": "string", "name": "_hash", "type": "string"}
        ],
        "name": "notarizeThesis",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
client = requests.Session()

def get_dspace_token():
    print("1. Authenticating with DSpace (Executing Advanced CSRF Handshake)...")    
    status_resp = client.get(f"{DSPACE_API_URL}/authn/status")    
    csrf_token = status_resp.headers.get('DSPACE-XSRF-TOKEN')    
    if not csrf_token:
        csrf_token = client.cookies.get('DSPACE-XSRF-TOKEN')        
    headers = {
        "X-XSRF-TOKEN": csrf_token,
        "Origin": "http://localhost:4000",
        "Referer": "http://localhost:4000/",
        "Content-Type": "application/x-www-form-urlencoded"
    }    
    response = client.post(
        f"{DSPACE_API_URL}/authn/login", 
        data={"user": DSPACE_EMAIL, "password": DSPACE_PASSWORD},
        headers=headers
    )   
    if response.status_code == 200:
        print("   -> DSpace Authentication Successful!")
        
        client.headers.update({
            "Authorization": response.headers.get('Authorization'),
            "X-XSRF-TOKEN": response.headers.get('DSPACE-XSRF-TOKEN') or csrf_token,
            "Origin": "http://localhost:4000",
            "Referer": "http://localhost:4000/",
            "Content-Type": "application/json", 
            "Accept": "application/json"
        })
        return True
    else:
        print(f"DSpace Authentication Failed! Status Code: {response.status_code}")
        print(f"Server Message: {response.text}")
        return False

def fetch_thesis_pdf(item_uuid):
    print(f"2. Fetching Thesis Metadata for UUID: {item_uuid}...")    
    item_req = client.get(f"{DSPACE_API_URL}/core/items/{item_uuid}")
    if item_req.status_code != 200: return None
    bundles_url = item_req.json()['_links']['bundles']['href']    
    bundles_data = client.get(bundles_url).json()
    for bundle in bundles_data['_embedded']['bundles']:
        if bundle['name'] == 'ORIGINAL':
            bitstreams_url = bundle['_links']['bitstreams']['href']
            bitstreams_data = client.get(bitstreams_url).json()            
            for bitstream in bitstreams_data['_embedded']['bitstreams']:
                if bitstream['name'].endswith('.pdf'):
                    download_url = bitstream['_links']['content']['href']
                    print(f"   -> Downloading: {bitstream['name']}")
                    pdf_resp = client.get(download_url, stream=True)
                    file_name = "temp_thesis.pdf"
                    with open(file_name, 'wb') as f:
                        for chunk in pdf_resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    return file_name
    print("No PDF found in this item.")
    return None

def generate_hash(file_path):
    print("3. Generating SHA-256 Digital Fingerprint...")
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    doc_hash = sha256.hexdigest()
    print(f"   -> Hash: {doc_hash}")
    return doc_hash
    
def anchor_to_blockchain(item_uuid, doc_hash):
    print("4. Anchoring to Ganache Blockchain...")
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    if not w3.is_connected():
        print("Cannot connect to Ganache. Is it running?")
        return None
    admin_account = w3.eth.accounts[0]
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    try:
        tx_hash = contract.functions.notarizeThesis(item_uuid, doc_hash).transact({'from': admin_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        txn_id = receipt.transactionHash.hex()
        print(f"   -> Success! Blockchain Txn ID: {txn_id}")
        return txn_id
    except Exception as e:
        print(f"Blockchain Error: {e}")
        return None

def inject_metadata(item_uuid, doc_hash, txn_id):
    print("5. Injecting Trust Metadata back into DSpace...")
    patch_headers = {"Content-Type": "application/json", "Accept": "application/json"}   
    patch_payload = [
        {"op": "add", "path": "/metadata/dc.description.blockchainhash", "value": [{"value": doc_hash}]},
        {"op": "add", "path": "/metadata/dc.description.blockchaintxn", "value": [{"value": txn_id}]}
    ]    
    response = client.patch(f"{DSPACE_API_URL}/core/items/{item_uuid}", headers=patch_headers, data=json.dumps(patch_payload))
    if response.status_code == 200:
        print("   -> DSpace Registry Updated Successfully!")
    else:
        print(f"Failed to update DSpace metadata. Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("INITIATING ENA NOTARY ENGINE")
    print("="*50)
    TARGET_UUID = input("Enter the Repository ETD Copy UUID to notarize: ").strip()
    if not TARGET_UUID:
        print("No UUID entered. Exiting engine.")
    else:
        if get_dspace_token():
            temp_pdf = fetch_thesis_pdf(TARGET_UUID)
            if temp_pdf:
                thesis_hash = generate_hash(temp_pdf)               
                blockchain_txn_id = anchor_to_blockchain(TARGET_UUID, thesis_hash)                
                if blockchain_txn_id:
                    inject_metadata(TARGET_UUID, thesis_hash, blockchain_txn_id)              
                if os.path.exists(temp_pdf):
                    os.remove(temp_pdf)
                print("\nNOTARIZATION COMPLETE. Temporary files cleaned.")
                print("="*50 + "\n")
