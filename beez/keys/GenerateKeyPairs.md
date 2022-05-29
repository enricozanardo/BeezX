# generate a private key with the correct length
openssl genrsa -out genesisPrivateKey.pem 1024

# generate corresponding public key
openssl rsa -in genesisPrivateKey.pem -pubout -out genesisPublicKey.pem