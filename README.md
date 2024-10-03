
# Introduction
This repository contains a set of programs illustrating conditional, predicate-based, decryption - that is, decryption based on certain attributes being set. 

Most use Fully Homomorphic Encryption (FHE) to work. 

# Mechanisms
## Timed Mechanism
After a certain integer, greater than encrypted constant, has been supplied to the program, information necessary to decrypt a piece of data is provided.

TODO: the data is to be read from the Solana or Ethereum block chain.

## TODO: ZKFHE
If data matches a specific ML model, data is decrypted.

# Artifacts
## Dockerfile
The included `Dockerfile` is a decent one to explore the most reliable FHE implementations.



## System UML Diagram

```mermaid
sequenceDiagram
Flag Source ->> Listener: Current time, encrypted with <br/>a `concrete` client/encryption<br/>(as opposed to evalutor or decryption)<br/> key
Listener-->>Decryptor: Encrypted output of the comparison
Note right of Decryptor: Decrypts encrypted comparison output,<br/> and derives decryption key,<br/> then attempts to decrypt shielded data
