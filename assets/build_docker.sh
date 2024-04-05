docker build -f Dockerfile_v1 -t superecho:v1  .
docker build -f Dockerfile_v2 -t superecho:v2  .

docker tag superecho:v1 ricchagas/superecho:v1
docker tag superecho:v2 ricchagas/superecho:v2

docker push ricchagas/superecho:v1
docker push ricchagas/superecho:v2
