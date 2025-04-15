variable "openrouter_api_key" {
  description = "OpenRouter API Key"
  type        = string
  sensitive   = true
}

variable "openrouter_default_model" {
  description = "Default model for OpenRouter"
  type        = string
  default     = "google/gemini-pro-1.5" 
}

terraform {
  cloud {
    organization = "examify_hk"
    workspaces {
      name = "dsegen-prod"
    }
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "examify-456306"
  region  = "asia-east2"
}

resource "google_cloud_run_v2_service" "dsegen" {
  name     = "dsegen"
  location = "asia-east2"
  template {
    containers {
      image = "asia-east2-docker.pkg.dev/examify-456306/examify/dsegen:1.0.0"
      env {
        name  = "OPENROUTER_DEFAULT_MODEL"
        value = var.openrouter_default_model 
      }
      env {
        name  = "OPENROUTER_API_KEY"
        value = var.openrouter_api_key
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "noauth" {
  project  = google_cloud_run_v2_service.dsegen.project
  location = google_cloud_run_v2_service.dsegen.location
  name     = google_cloud_run_v2_service.dsegen.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "dsegen_service_url" {
  description = "The URL of the deployed dsegen Cloud Run service"
  value       = google_cloud_run_v2_service.dsegen.uri
}
