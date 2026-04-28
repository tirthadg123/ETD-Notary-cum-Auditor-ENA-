<<<<<<< HEAD
# ETD-Notary-cum-Auditor-ENA-
This is ENA, the ETD Notary cum Auditor. It is a forensic system, that checks the authenticity of existing DSpace repository copies of electronic thesis and dissertations (ETDs) and a researcher-owned copy against a blockahin-notarized fingerprint using the SHA-256 system.
=======
# ETD Notary cum Auditor (ENA)

A decentralized "Zero-Trust" framework for securing Electronic Theses and Dissertations (ETDs) using DSpace 9.2 and the Ganache blockchain.

## 1. Prerequisites
- Python: 3.10 or higher
- DSpace: 9.2 (REST API enabled)
- Node.js: Latest LTS (to run Ganache)
- Ganache: 7.9.x

## 2. Installation
1. Clone this repository.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt

## 3. Setting up Ganache
mkdir ganache_data
npx ganache --database.dbPath ./ganache_data --wallet.defaultBalance 1000
   
## 4. Deploying the smart contract
python3 deploy_ena_notary.py

## 5. Running the ENA Notary
python3 ena_notary.py

## 6. Running the ENA Auditor
streamlit run ena_auditor.py

# NOTE : This codebase has been generated with some assistance of AI
>>>>>>> 08fc640 (Initial release of ETD Notary cum Auditor (ENA) Framework)
