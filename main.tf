terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

resource "docker_image" "adp" {
  name = "adp"
  build {
    context = "."
    tag = ["adp:latest"]
  }
}

resource "docker_container" "adp" {
  name = "adp"
  image = docker_image.adp.name
  env = ["USER_NAME=${var.USER_NAME}"]
  ports {
    internal = 3000
    external = 3000
  }
}

variable "USER_NAME" {
  type = string
}
