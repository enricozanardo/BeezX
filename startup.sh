docker-compose -f docker-compose/docker-compose.yml up -d beez-node-genesis
sleep 20
docker-compose -f docker-compose/docker-compose.yml up -d beez-node-alice
sleep 20
docker-compose -f docker-compose/docker-compose.yml up -d beez-node-bob
sleep 20
docker-compose -f docker-compose/docker-compose.yml up -d beez-node-lukas

docker-compose -f docker-compose/docker-compose.yml logs -f