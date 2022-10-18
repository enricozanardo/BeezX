lint-python:
	pylint beez/

lint-api-module:
	pylint beez/api/

lint-block-module:
	pylint beez/block/

lint-challenge-module:
	pylint beez/challenge/

lint-consensus-module:
	pylint beez/consensus/

lint-index-module:
	pylint beez/index/

lint-keys-module:
	pylint beez/keys/

lint-node-module:
	pylint beez/node/

lint-socket-module:
	pylint beez/socket/

lint-state-module:
	pylint beez/state/

lint-transaction-module:
	pylint beez/transaction/

lint-wallet-module:
	pylint beez/wallet/

format-python:
	./scripts/format-python.sh

typecheck-python:
	./scripts/typecheck-python.sh

test-block-module:
	./scripts/test-block-module.sh