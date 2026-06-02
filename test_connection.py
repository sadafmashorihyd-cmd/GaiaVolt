from web3 import Web3
import os, json
from dotenv import load_dotenv
load_dotenv()

w3 = Web3(Web3.HTTPProvider('https://rpc-amoy.polygon.technology'))

with open("ecox-contracts/artifacts/contracts/QuantumLock2050.sol/QuantumLock2050.json") as f:
    abi = json.load(f)["abi"]

ql = w3.eth.contract(
    address=Web3.to_checksum_address("0xc0d5a8E04706674b5aA2e366122Ae8d54C56c7c1"),
    abi=abi
)

status = ql.functions.getFundStatus().call()
print("Locked:      ", status[0])
print("Accumulated: ", status[2] / 10**18, "ECOX")
print("Top holder:  ", status[3])
print("Top score:   ", status[4])