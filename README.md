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

```bash
mkdir ganache_data
npx ganache --database.dbPath ./ganache_data --wallet.defaultBalance 1000
   ```
## 4. Deploying the smart contract
```bash
python3 deploy_ena_notary.py
```
## 5. Running the ENA Notary
```bash
python3 ena_notary.py
```
## 6. Running the ENA Auditor
```bash
streamlit run ena_auditor.py
```
Note: This codebase has been generated with some assistance of AI
>>>>>>> 08fc640 (Initial release of ETD Notary cum Auditor (ENA) Framework)
