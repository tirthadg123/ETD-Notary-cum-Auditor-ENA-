import streamlit as st
import requests
import hashlib
import os
from web3 import Web3

DSPACE_API_URL = "http://localhost:8080/server/api"
GANACHE_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "" # Enter the contact address obtained upon notary deployment
CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "_uuid", "type": "string"}],
        "name": "verifyThesis",
        "outputs": [
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def get_hash_from_upload(uploaded_file):
    """Calculates SHA-256 for a Streamlit uploaded file object."""
    sha256_hash = hashlib.sha256()
    for chunk in iter(lambda: uploaded_file.read(4096), b""):
        sha256_hash.update(chunk)
    uploaded_file.seek(0)
    return sha256_hash.hexdigest()

def fetch_live_dspace_hash(item_uuid):
    try:
        item_req = requests.get(f"{DSPACE_API_URL}/core/items/{item_uuid}")
        if item_req.status_code != 200: return None
        bundles_url = item_req.json()['_links']['bundles']['href']
        bundles_data = requests.get(bundles_url).json()
        for bundle in bundles_data['_embedded']['bundles']:
            if bundle['name'] == 'ORIGINAL':
                bitstreams_url = bundle['_links']['bitstreams']['href']
                bitstreams_data = requests.get(bitstreams_url).json()
                for bitstream in bitstreams_data['_embedded']['bitstreams']:
                    if bitstream['name'].endswith('.pdf'):
                        download_url = bitstream['_links']['content']['href']
                        pdf_resp = requests.get(download_url, stream=True)
                        sha256 = hashlib.sha256()
                        for chunk in pdf_resp.iter_content(chunk_size=8192):
                            sha256.update(chunk)
                        return sha256.hexdigest()
    except Exception: return None
    return None

def fetch_blockchain_hash(item_uuid):
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    if not w3.is_connected(): return "Node Error"
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    try:
        result = contract.functions.verifyThesis(item_uuid).call()
        return result[0]
    except: return None

st.set_page_config(page_title="ENA Auditor", page_icon="🔍")
st.title("ENA Forensic Auditor")
st.markdown("Verify the integrity of research against the University Blockchain.")
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Identify Repository ETD Copy")
    target_uuid = st.text_input("Enter Repository ETD Copy UUID:", placeholder="e.g. 58fa59f4-d58f-...")
with col2:
    st.subheader("2. Upload Researcher ETD Copy")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if st.button("Run ENA Auditor", use_container_width=True):
    if not target_uuid or not uploaded_file:
        st.error("Please provide both a UUID and a PDF file.")
    else:
        with st.spinner("Executing Tripartite Audit..."):
            local_h = get_hash_from_upload(uploaded_file)
            dspace_h = fetch_live_dspace_hash(target_uuid)
            ledger_h = fetch_blockchain_hash(target_uuid)
            st.write("### Technical Details")
            t1, t2, t3 = st.tabs(["Researcher ETD Copy", "Repository ETD Copy", "Blockchain Fingerprint"])
            t1.code(local_h)
            t2.code(dspace_h if dspace_h else "Not Found")
            t3.code(ledger_h if ledger_h else "Not Found")
            st.divider()
            st.subheader("Audit Verdict")            
            if ledger_h == "Node Error":
                st.warning("Could not connect to Ganache blockchain. Is it running?")
            elif not ledger_h:
                st.error("UNVERIFIED: This ETD does not exist on the blockchain record.")
            elif local_h == dspace_h == ledger_h:
                st.success("ABSOLUTE INTEGRITY: All three records match perfectly. The ETD is authentic.")
            elif local_h != ledger_h and dspace_h == ledger_h:
                st.warning("LOCAL CORRUPTION: The repository is safe, but the researcher copy has been fabricated.")
            elif dspace_hash != ledger_hash and local_hash == ledger_hash:
                st.error("REPOSITORY COMPROMISED: The Repository ETD Copy has been fabricated post-submission!")
            else:
                st.error("CRITICAL BREACH: Neither file matches the original blockchain record.")
