from cryptography.fernet import Fernet

# Generate the encryption key
key = Fernet.generate_key()

# Save the key to a file
with open("encryption_key.txt", 'wb') as file:
    file.write(key)

print("Encryption key generated and saved to encryption_key.txt")
