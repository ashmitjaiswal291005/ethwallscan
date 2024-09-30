import os
import random
import requests
from mnemonic import Mnemonic

# Constants
NUM_PHRASES = 1000  # Number of phrases to generate
API_URL = "https://api.example.com/check_balance"  # Replace with your API endpoint
OUTPUT_FILE = "valid_phrases.txt"

# Initialize BIP-39 generator
mnemo = Mnemonic("english")

def generate_phrase():
    return mnemo.generate(strength=128)  # 12-word phrase

def check_balance(address):
    response = requests.get(API_URL, params={"address": address})
    if response.status_code == 200:
        data = response.json()
        return data['balance'] > 0
    else:
        print(f"Failed to check balance for {address}")
        return False

def main():
    valid_phrases = []

    for _ in range(NUM_PHRASES):
        phrase = generate_phrase()
        # Convert phrase to address (dummy function, replace with actual conversion)
        address = phrase_to_address(phrase)

        if check_balance(address):
            valid_phrases.append(phrase)
            print(f"Valid phrase found: {phrase}")

    # Write valid phrases to file
    with open(OUTPUT_FILE, "w") as f:
        for phrase in valid_phrases:
            f.write(f"{phrase}\n")

    print(f"Completed. Valid phrases saved to {OUTPUT_FILE}")

def phrase_to_address(phrase):
    # Convert BIP-39 phrase to address (dummy implementation)
    # Replace with actual conversion logic based on the blockchain
    return phrase

if __name__ == "__main__":
    main()
