#! /bin/bash

minikube start
eval $(minikube docker-env)
docker run -d --rm -p 5000:5000 --name registry registry:latest
docker build -t localhost:5000/adp:latest .
docker push localhost:5000/adp:latest
terraform -chdir=terraform init
terraform -chdir=terraform apply -auto-approve
kubectl config set-context --current --namespace=local
minikube tunnel
