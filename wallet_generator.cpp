#include <iostream>
#include <fstream>
#include <vector>
#include <random>
#include <string>
#include <thread>
#include <future>
#include <unordered_set>
#include <cpr/cpr.h>
#include <cryptlib.h>
#include <osrng.h>
#include <hex.h>
#include <secblock.h>
#include <sha.h>
#include <filters.h>
#include <eccrypto.h>
#include <pubkey.h>
#include <modes.h>
#include <aes.h>
#include <ripemd.h>
#include <base58.h>
#include <mnemonic.h>

using namespace std;

// Load BIP39 word list
vector<string> load_word_list(const string& filename) {
    vector<string> word_list;
    ifstream file(filename);
    string word;

    while (file >> word) {
        word_list.push_back(word);
    }

    return word_list;
}

// Generate a random 12-word phrase
string generate_random_phrase(const vector<string>& word_list) {
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dis(0, word_list.size() - 1);
    string phrase;

    for (int i = 0; i < 12; ++i) {
        phrase += word_list[dis(gen)] + " ";
    }

    return phrase.substr(0, phrase.length() - 1); // Remove trailing space
}

// Convert seed phrase to Ethereum address
string get_ethereum_address_from_phrase(const string& phrase) {
    // Use Crypto++ to generate the seed and derive the private key
    string seed = Mnemonic::to_seed(phrase);
    string private_key = seed.substr(0, 32); // Extracting the private key

    // Generate the Ethereum address from the private key
    byte hash[32];
    CryptoPP::SHA256().CalculateDigest(hash, (const byte*)private_key.data(), private_key.size());
    string address = "0x";
    for (int i = 12; i < 32; ++i) {
        address += hex_to_string(hash[i]);
    }
    
    return address;
}

// Check if the address has a balance
bool check_balance(const string& address) {
    string url = "https://api.blockcypher.com/v1/eth/main/addrs/" + address + "/balance";
    auto response = cpr::Get(cpr::Url{url});

    if (response.status_code == 200) {
        auto json = json::parse(response.text);
        return json["balance"].get<int64_t>() > 0;
    }
    
    return false;
}

// Save the valid phrase and address to a file
void save_to_file(const string& phrase, const string& address) {
    ofstream file("valid_wallets.txt", ios::app);
    file << "Phrase: " << phrase << "\nAddress: " << address << "\n\n";
}

bool process_phrase(const string& phrase) {
    if (Mnemonic::check(phrase)) {
        string address = get_ethereum_address_from_phrase(phrase);
        if (check_balance(address)) {
            cout << "Found a valid wallet phrase: " << phrase << endl;
            cout << "Ethereum Address: " << address << endl;
            save_to_file(phrase, address);
            return true;
        }
    }
    return false;
}

void wallet_generator(const vector<string>& word_list, unordered_set<string>& processed_phrases, bool& found_wallet) {
    while (!found_wallet) {
        string phrase = generate_random_phrase(word_list);

        if (processed_phrases.find(phrase) == processed_phrases.end()) {
            processed_phrases.insert(phrase);
            if (process_phrase(phrase)) {
                found_wallet = true;
            }
        }
    }
}

int main() {
    vector<string> word_list = load_word_list("bip39_wordlist.txt");
    unordered_set<string> processed_phrases;
    bool found_wallet = false;
    
    // Adjust concurrency settings based on your CPU capabilities
    const int num_threads = thread::hardware_concurrency(); // Number of available threads

    vector<thread> threads;
    for (int i = 0; i < num_threads; ++i) {
        threads.emplace_back(wallet_generator, ref(word_list), ref(processed_phrases), ref(found_wallet));
    }

    for (auto& t : threads) {
        t.join();
    }

    return 0;
}
