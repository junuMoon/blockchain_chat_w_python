# TODOS

date: 2021.06.03

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

1. Verify Transaction
2. Packaging
    1. 앱 시작 시 db 생성 후 create_all
3. Wallet
    1. Node
    2. 공개키/비밀키
    3. func sign
4. chaining
    2. valid chain
    3. consensus
    4. chain substitution
5. network
    1. CONN_NODES 를 deque로 구현
    2. 서버 종료시 노드 연결 제거 with after app context
    3. 노드 커넥션 예외 처리
6. 로거 추가하여 디버깅 용이하게 만들기