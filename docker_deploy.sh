# Build docker image for prototype
docker build -t prototype:latest .

# Build docker image for web
cd web
docker build -t webvault:latest .

# Run docker compose
cd ..
docker-compose --file=prototype.docker-compose.yml up -d 
