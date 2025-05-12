#! /bin/bash

terraform -chdir=terraform destroy
minikube stop
minikube delete --all
