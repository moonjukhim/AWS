```hcl
# Placeholder Terraform template for GCP Anthos multi-cluster architecture

# This is a starter template. You will need to customize networking, IAM,
# cluster versions, service mesh configs, databases, and application deployments.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google" {
  alias   = "west"
  project = var.project_id
  region  = "us-west1"
}

provider "google" {
  alias   = "central"
  project = var.project_id
  region  = "us-central1"
}

variable "project_id" {}
variable "region" {
  default = "us-west1"
}

# -------------------------
# VPC
# -------------------------
resource "google_compute_network" "main" {
  name                    = "anthos-multi-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "west" {
  name          = "subnet-us-west1"
  region        = "us-west1"
  network       = google_compute_network.main.id
  ip_cidr_range = "10.10.0.0/20"
}

resource "google_compute_subnetwork" "central" {
  name          = "subnet-us-central1"
  region        = "us-central1"
  network       = google_compute_network.main.id
  ip_cidr_range = "10.20.0.0/20"
}

# -------------------------
# GKE clusters (West & Central)
# -------------------------
resource "google_container_cluster" "west" {
  provider = google.west
  name     = "west-cluster"
  location = "us-west1"

  network    = google_compute_network.main.self_link
  subnetwork = google_compute_subnetwork.west.self_link

  remove_default_node_pool = true
  initial_node_count       = 1
}

resource "google_container_node_pool" "west_pool" {
  provider = google.west
  cluster  = google_container_cluster.west.name
  location = google_container_cluster.west.location
  name     = "default-pool"

  node_config {
    machine_type = "e2-standard-4"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

resource "google_container_cluster" "central" {
  provider = google.central
  name     = "central-cluster"
  location = "us-central1"

  network    = google_compute_network.main.self_link
  subnetwork = google_compute_subnetwork.central.self_link

  remove_default_node_pool = true
  initial_node_count       = 1
}

resource "google_container_node_pool" "central_pool" {
  provider = google.central
  cluster  = google_container_cluster.central.name
  location = google_container_cluster.central.location
  name     = "default-pool"

  node_config {
    machine_type = "e2-standard-4"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

# -------------------------
# Anthos Service Mesh (ASM) installation placeholder
# -------------------------
# ASM cannot be fully installed via Terraform alone. Normally installed via script.
# This block is just a placeholder.

locals {
  asm_note = "Use asmcli to install Anthos Service Mesh onto both clusters after creation."
}

# -------------------------
# Google Cloud Load Balancers (Ingress + NEG)
# -------------------------
# Placeholder resources. Actual config needs app manifests & NEGs.

resource "google_compute_global_address" "lb_ip" {
  name = "global-lb-ip"
}

resource "google_compute_global_forwarding_rule" "lb_rule" {
  name       = "global-lb-forwarding-rule"
  target     = google_compute_target_http_proxy.lb_http_proxy.self_link
  port_range = "80"
  ip_address = google_compute_global_address.lb_ip.address
}

resource "google_compute_target_http_proxy" "lb_http_proxy" {
  name    = "lb-http-proxy"
  url_map = google_compute_url_map.lb_url_map.self_link
}

resource "google_compute_url_map" "lb_url_map" {
  name = "lb-url-map"

  default_service = google_compute_backend_service.default_backend.self_link
}

resource "google_compute_backend_service" "default_backend" {
  name                  = "default-backend"
  protocol              = "HTTP"
  timeout_sec           = 30
  connection_draining_timeout_sec = 10
}

# -------------------------
# Databases (PostgreSQL Cloud SQL)
# -------------------------

resource "google_sql_database_instance" "accounts" {
  name             = "accounts-db"
  database_version = "POSTGRES_15"
  region           = "us-west1"
  settings {
    tier = "db-f1-micro"
  }
}

resource "google_sql_database_instance" "ledger" {
  name             = "ledger-db"
  database_version = "POSTGRES_15"
  region           = "us-central1"
  settings {
    tier = "db-f1-micro"
  }
}

# -------------------------
# Output
# -------------------------

output "west_cluster_name" {
  value = google_container_cluster.west.name
}

output "central_cluster_name" {
  value = google_container_cluster.central.name
}

output "global_lb_ip" {
  value = google_compute_global_address.lb_ip.address
}
```
