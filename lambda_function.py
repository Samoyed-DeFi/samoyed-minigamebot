from web3 import Web3
from time import sleep
import random
import boto3

ssm = boto3.client('ssm')


def get_drawerPrivateKey():
    response = ssm.get_parameters(
        Names=['drawerPrivateKey'], WithDecryption=False
    )
    for parameter in response['Parameters']:
        return parameter['Value']


def call_drawWinner(rpc_server, contract_address, contract_abi, drawer_address, drawer_privatekey, gas_limit, gas_price_gwei,salt):
    w3 = Web3(Web3.HTTPProvider(rpc_server))

    if w3.isConnected() == True:
        # Configure miniGame address & abi
        address = contract_address
        abi = contract_abi
        minigame_instance = w3.eth.contract(address=address, abi=abi)

        # drawer address
        drawer_address = drawer_address
        drawer_cksum_address = Web3.toChecksumAddress(drawer_address)

        # get nonce
        nonce = w3.eth.get_transaction_count(drawer_cksum_address)

        drawWinner_txn = minigame_instance.functions.drawWinner(salt).buildTransaction({
            # 'chainId': 1,
            'gas': gas_limit,
            'gasPrice': w3.toWei(gas_price_gwei, 'gwei'),
            'nonce': nonce,
        })

        # print Transaction
        print(drawWinner_txn)

        # Set Private Key
        private_key = drawer_privatekey

        # Use Private Key to Sign the transactions
        signed_txn = w3.eth.account.sign_transaction(
            drawWinner_txn, private_key=private_key)

        # send to RPC Server
        w3.eth.send_raw_transaction(signed_txn.rawTransaction)


def drawWinnerCheck(rpc_server, contract_address, contract_abi, authorized_drawer_address,
                    authorized_drawer_private_key, gas_limit, gas_price_gwei,sleep_base,sleep_range):
    # print("Start drawWinnerCheck")
    w3 = Web3(Web3.HTTPProvider(rpc_server))

    if w3.isConnected() == True:
        # Configure miniGame address & abi
        address = contract_address
        abi = contract_abi
        minigame_instance = w3.eth.contract(address=address, abi=abi)

        # Get currentRoomNo
        currentRoomNo = minigame_instance.functions.currentRoomNo().call()

        # Get nextWinnerDrawRoomNo
        nextWinnerDrawRoomNo = minigame_instance.functions.nextWinnerDrawRoomNo().call()
        print("currentRoomNo: %d, nextWinnerDrawRoomNo: %d" %
              (currentRoomNo, nextWinnerDrawRoomNo))

        if(currentRoomNo > nextWinnerDrawRoomNo):
            salt=random.getrandbits(256)
            timesleep=random.randrange(sleep_range)
            print("sleep %d + %d ms, before Call DrawWinner(%d)" % (sleep_base , timesleep, salt))
            sleep((sleep_base+timesleep)/1000)
            call_drawWinner(rpc_server, contract_address, contract_abi, authorized_drawer_address,
                            authorized_drawer_private_key, gas_limit, gas_price_gwei,salt)
        else:
            print("Do Nothing")

def getMiniGameContractABI():
    return '[{"inputs":[{"internalType":"uint256","name":"salt","type":"uint256"}],"name":"drawWinner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"currentRoomNo","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"nextWinnerDrawRoomNo","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

def lambda_handler(event, context):
    drawWinnerCheck(event['rpc_server'], event['contract_address'], getMiniGameContractABI(),
                    event['authorized_drawer_address'], get_drawerPrivateKey(), event['gas_limit'], event['gas_price_gwei'], event['sleep_base'], event['sleep_range'])