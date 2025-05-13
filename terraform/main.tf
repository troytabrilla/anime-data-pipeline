terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "~> 2.36.0"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
  config_context = "minikube"
}

variable "user_name" {
  type = string
  sensitive = true
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
        host_network = true
      }
    }
  }
}

resource "kubernetes_deployment" "broker_deployment" {
  metadata {
    name = "broker-deployment"
    labels = {
      app = "broker"
    }
    namespace = "local"
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "broker"
      }
    }
    template {
      metadata {
        labels = {
          app = "broker"
        }
      }
      spec {
        container {
          image = "apache/kafka:latest"
          name = "broker"
          port {
            container_port = 9092
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
    create = "10s"
  }
}

resource "kubernetes_service" "broker_service" {
  metadata {
    name = "broker-service"
    namespace = "local"
  }
  spec {
    type = "LoadBalancer"
    port {
      port = 9092
      target_port = 9092
    }
    selector = {
      app = "broker"
    }
  }
  timeouts {
    create = "10s"
  }
}

# TODO try to terraform helm
