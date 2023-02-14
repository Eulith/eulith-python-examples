# Overview
This repo contains short scripts that do basic things via eulith. These can be used as helper files, particularly if you are using a KMS wallet. Some examples:
* A basic swap
* Getting the balance of an ERC 20 token
* Testing KMS integration
* Sending a transaction to an address

# Instructions
1. Run `pip install -r requirements.txt`, the main library here is eulith-web3
2. Set wallet details in `config.py` (lines 26 & 27)
3. Copy/paste your refresh token in `config.py` on line 30
4. (optional) Set the network you wish to send transactions to, default is mainnet (line 29)
6. Run `python3 <file to execute>.py`

