## Beez Blockchain CHANGELOG

### v2.0.0 - 2023-01-06

#### Crypto
- Substitute RSA keypairs with Ed25519 elliptic curve keypairs
- Refactor key generation in Python
- Refactor hashing from SHA265 to SHA512

#### Addresses
- Implement address-key mapping broadcast on Beez Nodes
- Implement transformation from Ed25519 public key to Beez address
- Add implementation to P2P broadcast addresses if they are not already known by node
- Extend P2P protocol to broadcast address to public key mapping
- Add address index on nodes to store address to public key mapping
- Refactor signature validation from expecting public key in transaction to expecting address
- Implemented transaction covered check when transaction is handled.
- Added changelog ([#7]([https://github.com/onezerobinary/BeezX/issues/7])).

### v1.0 - 2022-11-29

- Added test suite ([#17]([https://github.com/onezerobinary/BeezX/issues/17])).
- Added type information ([#16]([https://github.com/onezerobinary/BeezX/issues/16])).
- Implemented test infrastructure using docker and docker-compose ([#3, #4, #5](https://github.com/onezerobinary/BeezX/issues/5, https://github.com/onezerobinary/BeezX/issues/4, https://github.com/onezerobinary/BeezX/issues/3)).
- Implemented basic blockchain functionality.