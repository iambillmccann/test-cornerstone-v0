variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment_name" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project slug used for resource name prefixes"
  type        = string
  default     = "cornerstone"
}

variable "database_name" {
  description = "Logical database name"
  type        = string
  default     = "cornerstone"
}

variable "tf_lock_table_name" {
  description = "DynamoDB table used for Terraform backend state locking"
  type        = string
  default     = "cornerstone-tf-lock"
}

# Clerk Configuration
variable "clerk_jwks_url" {
  description = "Clerk JWKS URL for JWT verification"
  type        = string
  sensitive   = true
}

variable "clerk_issuer" {
  description = "Clerk issuer URL (optional for compatibility; recommended for strict JWT validation)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "clerk_audience" {
  description = "Clerk audience (optional for compatibility; recommended for strict JWT validation)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "clerk_publishable_key" {
  description = "Clerk publishable key (frontend build-time env var)"
  type        = string
  sensitive   = true
}

variable "clerk_secret_key_arn" {
  description = "ARN of Secrets Manager secret containing CLERK_SECRET_KEY (created by bootstrap script)"
  type        = string
  sensitive   = true
}

# Database
variable "rds_database_url_arn" {
  description = "ARN of Secrets Manager secret containing DATABASE_URL (created by bootstrap script)"
  type        = string
  sensitive   = true
}

variable "rds_instance_class" {
  description = "RDS instance class (e.g., db.t4g.micro)"
  type        = string
  default     = "db.t4g.micro"
}

variable "rds_storage_gb" {
  description = "RDS storage in GB"
  type        = number
  default     = 20
}

variable "rds_public_accessibility" {
  description = "Whether RDS is publicly accessible (default false for private networking)"
  type        = bool
  default     = false
}

# CORS Configuration
variable "cors_origins" {
  description = "Comma-separated list of CORS origins"
  type        = string
  default     = ""
}

# Docker Image
variable "ecr_image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "app_runner_cpu" {
  description = "App Runner vCPU (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 256
}

variable "app_runner_memory" {
  description = "App Runner memory in MB (512, 1024, 2048, 3072, 4096)"
  type        = number
  default     = 512
}
