from concurrent.futures import ProcessPoolExecutor, as_completed
from mnemonic import Mnemonic
from web3 import Web3
import random
import requests

# Load BIP39 word list
def load_word_list():
    with open('bip39_wordlist.txt') as f:
        return [line.strip() for line in f]

# Generate a random 12-word phrase
def generate_random_phrase(word_list):
    return ' '.join(random.choices(word_list, k=12))

# Convert seed phrase to Ethereum address
def get_ethereum_address_from_phrase(phrase):
    mnemo = Mnemonic("english")
    seed = mnemo.to_seed(phrase)
    private_key = seed[:32]  # Extracting the private key (simplified)
    
    # Convert bytes to hex string
    private_key_hex = private_key.hex()
    
    # Create an account from the private key
    account = Web3().eth.account.from_key(private_key_hex)
    return account.address

# Check if the address has a balance
def check_balance(address):
    url = f'https://api.blockcypher.com/v1/eth/main/addrs/{address}/balance'
    response = requests.get(url)
    balance = response.json().get('balance', 0)
    return balance > 0

# Save the valid phrase and address to a file
def save_to_file(phrase, address):
    with open('valid_wallets.txt', 'a') as f:
        f.write(f'Phrase: {phrase}\nAddress: {address}\n\n')

def process_phrase(phrase):
    mnemo = Mnemonic("english")
    if mnemo.check(phrase):
        address = get_ethereum_address_from_phrase(phrase)
        if check_balance(address):
            print(f"Found a valid wallet phrase: {phrase}")
            print(f"Ethereum Address: {address}")
            save_to_file(phrase, address)
            return True
    return False

def main():
    word_list = load_word_list()
    processed_phrases = set()  # To keep track of already processed phrases
    scanned_count = 0
    found_wallet = False

    # Adjust concurrency settings based on your CPU capabilities
    num_workers = 4  # Example: Adjust this number based on the number of CPU cores
    batch_size = 100  # Adjust batch size as needed

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        while not found_wallet:
            phrases_to_check = []
            for _ in range(batch_size):
                phrase = generate_random_phrase(word_list)
                if phrase not in processed_phrases:
                    phrases_to_check.append(phrase)
                    processed_phrases.add(phrase)

            # Submit tasks to the executor
            future_to_phrase = {executor.submit(process_phrase, phrase): phrase for phrase in phrases_to_check}

            for future in as_completed(future_to_phrase):
                if future.result():
                    found_wallet = True
                    break

            scanned_count += len(phrases_to_check)
            print(f"Scanned {scanned_count} wallets...")

if __name__ == "__main__":
    main()
