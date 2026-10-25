import hashlib
import json
import time

class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data  # Holds our credential details
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Generates a SHA-256 hash of the block's content."""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        """Proof-of-Work: Finds a hash starting with 'difficulty' number of zeros."""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.difficulty = 3  # Fast enough for an instant classroom demo
        self.create_genesis_block()

    def create_genesis_block(self):
        """Generates the initial block of the blockchain."""
        genesis_block = Block(0, time.time(), {"info": "Genesis Block - System Initialized"}, "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_latest_block(self):
        """Returns the most recent block in the sequence."""
        return self.chain[-1]

    def add_block(self, data):
        """Creates, mines, and appends a new block to the chain."""
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=latest_block.hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def is_chain_valid(self):
        """Validates the cryptographic integrity of the entire blockchain sequence.
        Returns a tuple: (bool_status, error_message_or_none, broken_block_index)
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Rule 1: Check if the block's data matches its hash
            if current_block.hash != current_block.calculate_hash():
                return False, f"Block {i} hash value has been altered!", i

            # Rule 2: Check if previous_hash link is broken
            if current_block.previous_hash != previous_block.hash:
                return False, f"Block {i} links to an invalid historical hash!", i

        return True, "Chain is cryptographically intact.", -1
