#! /bin/bash

terraform -chdir=terraform destroy -auto-approve
minikube stop
minikube delete --all
