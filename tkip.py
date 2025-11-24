import hashlib
import random

def tkip_encrypt(base_key, data):
    # Generate a 48-bit IV (Initialization Vector)
    iv = random.getrandbits(48)
    
    # Derive a per-packet key using SHA-1 hash
    per_packet_key = hashlib.sha1((base_key + str(iv)).encode()).digest()[:16]
    
    # Compute the Message Integrity Code (MIC)
    mic = hashlib.md5(data.encode()).hexdigest()
    
    # Encrypt using XOR with the per-packet key
    cipher = bytes([d ^ per_packet_key[i % len(per_packet_key)] for i, d in enumerate(data.encode())])
    
    return iv, cipher, mic

def tkip_decrypt(base_key, iv, cipher, mic):
    # Recreate the same per-packet key
    per_packet_key = hashlib.sha1((base_key + str(iv)).encode()).digest()[:16]
    
    # Decrypt by reversing XOR
    data = ''.join(chr(c ^ per_packet_key[i % len(per_packet_key)]) for i, c in enumerate(cipher))
    
    # Verify integrity
    if hashlib.md5(data.encode()).hexdigest() == mic:
        return data
    return 'Integrity check failed'

# ---------------- DEMO SECTION ----------------

if __name__ == "__main__":
    base_key = input("Enter base key: ")
    plaintext = input("Enter plaintext: ")

    iv, cipher, mic = tkip_encrypt(base_key, plaintext)
    print("\n--- ENCRYPTION ---")
    print("IV:", iv)
    print("Cipher (bytes):", cipher)
    print("MIC:", mic)

    decrypted = tkip_decrypt(base_key, iv, cipher, mic)
    print("\n--- DECRYPTION ---")
    print("Decrypted Text:", decrypted)
