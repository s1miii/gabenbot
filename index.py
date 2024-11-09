from flask import Flask, jsonify
from web3 import Web3

# Flask app setup
app = Flask(__name__)

# Configuration
TARGET_ADDRESS = "0xc204af95b0307162118f7bc36a91c9717490ab69"
RPC_URL = "https://base.drpc.org"  # Replace with your Base L2 network RPC URL

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

@app.route('/check', methods=['GET'])
def check_for_deployments():
    latest_block = w3.eth.block_number
    print(f"Checking block {latest_block} for deployments from {TARGET_ADDRESS}")

    block = w3.eth.get_block(latest_block, full_transactions=True)
    deployments = []

    for tx in block.transactions:
        # Check if transaction is from the target address and to a null address (new contract)
        if tx['from'].lower() == TARGET_ADDRESS.lower() and tx['to'] is None:
            # Get transaction receipt to fetch the contract address
            receipt = w3.eth.get_transaction_receipt(tx['hash'])
            contract_address = receipt.contractAddress

            # Record deployment details
            deployment_details = {
                "transaction_hash": tx['hash'].hex(),
                "contract_address": contract_address,
                "block_number": latest_block,
                "transaction_link": f"https://basescan.org/tx/{tx['hash'].hex()}",
                "contract_link": f"https://basescan.org/address/{contract_address}"
            }
            deployments.append(deployment_details)
    
    # Return deployment details, if any
    if deployments:
        return jsonify({
            "status": "New deployment(s) detected",
            "deployments": deployments
        }), 200
    else:
        return jsonify({
            "status": "No new deployments found in the latest block"
        }), 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Bot is ready to check for deployments"}), 200

# Start the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
