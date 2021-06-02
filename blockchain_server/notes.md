# TODOS

date: 2021.06.01

---

## Category

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
  - \__eq__
- Broadcasting
- Asynchronous way of Connection between nodes
  - exception handling
    - httpPool
    - in case of left server
  - debugging with logger
- consensus & chain substitution
- packaging
  - nodes
  - blockchain

### Network

- Synchronization cronjob between nodes
- Multi-threading for user
- concurrency

### API

- db init
- Packaging

## Priorities

1. chaining
    2. valid chain
    3. consensus
    4. chain substitution
1. 지금 구현되어 있는 것 robust하게 만들기
    1. genesis block과 세션 노드
    2. 서버 종료시 노드 연결 제거 with after app context
    2. 노드 커넥션 예외 처리
    3. 블록, tx, 노드 중복 개체 불허
2. 로거 추가하여 디버깅 용이하게 만들기