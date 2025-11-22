import time
import hashlib
import json

class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        """
        Calcule le hash SHA-256 du bloc.
        """
        block_string = (
            str(self.index)
            + str(self.timestamp)
            + str(self.data)
            + str(self.previous_hash)
            + str(self.nonce)
        )
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self, difficulty=3):
        self.chain = []
        self.difficulty = difficulty
        self.prefix = "0" * self.difficulty
        self.create_genesis_block()
        self.total_nonce = 0
        self.total_mining_time = 0.0

    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), "Genesis Block", "0")
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        start_time = time.time()
        while True:
            block.hash = block.compute_hash()
            if block.hash.startswith(self.prefix):
                elapsed_time = time.time() - start_time
                self.total_mining_time += elapsed_time
                self.total_nonce += block.nonce + 1  # nonce starts at 0
                return block, elapsed_time
            block.nonce += 1

    def add_block(self, data):
        previous_block = self.get_last_block()
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=previous_block.hash
        )
        mined_block, elapsed = self.proof_of_work(new_block)
        self.chain.append(mined_block)
        return mined_block, elapsed

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.previous_hash != previous.hash:
                return False, f"Block {i}: previous_hash incorrect"
            if current.hash != current.compute_hash():
                return False, f"Block {i}: hash recomputé différent"
            if not current.hash.startswith(self.prefix):
                return False, f"Block {i}: difficulté non respectée"
        return True, "Chaîne valide"

    def average_nonce(self):
        if len(self.chain) <= 1:
            return 0
        return self.total_nonce / (len(self.chain) - 1)


# Démonstration 

if __name__ == "__main__":
    difficulty = 4  # tu peux augmenter pour bonus
    blockchain = Blockchain(difficulty=difficulty)

    # Miner des blocs avec mesure du temps
    transactions = ["Alice ➜ Bob : 5", "Bob ➜ Charlie : 2", "Charlie ➜ Dave : 1"]
    for tx in transactions:
        print(f"Mining block {len(blockchain.chain)} with data: '{tx}' ...")
        block, elapsed = blockchain.add_block(tx)
        print(f" -> Mined block {block.index}: hash={block.hash} nonce={block.nonce} time={elapsed:.4f}s\n")

    # Afficher la blockchain complète
    print("\n Full blockchain:")
    for block in blockchain.chain:
        print(json.dumps(block.__dict__, indent=2))

    # Valider la chaîne
    valid, message = blockchain.is_chain_valid()
    print(f"\n🔍 Validation: {valid} - {message}")

    # Tamper pour montrer l'invalidation
    print("\n Tampering block 2 data...")
    blockchain.chain[2].data = "FRAUD !!!"
    valid, message = blockchain.is_chain_valid()
    print(f"Validation after tampering: {valid} - {message}")

    # Réparer la chaîne en re-minant les blocs falsifiés
    print("\n Re-mining tampered block and subsequent blocks...")
    for i in range(2, len(blockchain.chain)):
        block = blockchain.chain[i]
        block.previous_hash = blockchain.chain[i-1].hash
        block.nonce = 0
        mined_block, elapsed = blockchain.proof_of_work(block)
        blockchain.chain[i] = mined_block
        print(f" -> Re-mined block {mined_block.index}: nonce={mined_block.nonce} hash={mined_block.hash} time={elapsed:.4f}s")

    # Validation finale
    valid, message = blockchain.is_chain_valid()
    print(f"\n Final Validation after repair: {valid} - {message}")

    # Afficher statistiques 
    print(f"\nAverage nonce across mined blocks: {blockchain.average_nonce():.2f}")
    print(f"Total mining time: {blockchain.total_mining_time:.4f}s")
