# TODO merge helm branch and try to terraform helm
terraform {
  required_providers {
    # docker = {
    #   source = "kreuzwerker/docker"
    #   version = "~> 3.0.1"
    # }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "~> 2.36.0"
    }
  }
}

variable "user_name" {
  type = string
  sensitive = true
}

# provider "docker" {}

# resource "docker_image" "adp" {
#   name = "adp"
#   build {
#     context = "."
#     tag = ["adp:latest"]
#   }
# }

# resource "docker_container" "adp" {
#   name = "adp"
#   image = docker_image.adp.name
#   env = ["USER_NAME=${var.user_name}"]
#   ports {
#     internal = 3000
#     external = 3000
#   }
# }

provider "kubernetes" {
  config_path = "~/.kube/config"
  config_context = "minikube"
}

resource "kubernetes_namespace" "local" {
  metadata {
    name = "local"
  }
}

resource "kubernetes_secret" "user-name" {
  metadata {
    name = "user-name"
    namespace = "local"
  }
  data = {
    user-name = var.user_name
  }
  type = "Opaque"
}

resource "kubernetes_deployment" "adp_deployment" {
  metadata {
    name = "adp-deployment"
    labels = {
      app = "adp"
    }
    namespace = "local"
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "adp"
      }
    }
    template {
      metadata {
        labels = {
          app = "adp"
        }
      }
      spec {
        container {
          image = "localhost:5000/adp:latest"
          name = "adp"
          env {
            name = "USER_NAME"
            value_from {
              secret_key_ref {
                name = "user-name"
                key = "user-name"
              }
            }
          }
          port {
            container_port = 3000
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "adp_service" {
  metadata {
    name = "adp-service"
    namespace = "local"
  }
  spec {
    type = "LoadBalancer"
    port {
      port = 3000
      target_port = 3000
    }
    selector = {
      app = "adp"
    }
  }
  timeouts {
    create = "30s"
  }
}
