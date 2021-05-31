# TODOS

date: 2021.05.31

---

### Model

- Transaction In/Out
- Wallet
  - hash
    - RSA
    - ECDSA
- Block
  - timestamp stringfy
  - index unique constraint
- Transaction
  - cascade delete option in block_hash column

### Routes

- Transaction calculate
- Valid Chain
- Broadcasting
- Asynchronous way of Connection between nodes
  - exception handling
  - debugging with logger
- consensus & chain substitution
- packaging
  - nodes
  - blockchain

### Network

- Synchronization cronjob between nodes
- Multi-threading for user
