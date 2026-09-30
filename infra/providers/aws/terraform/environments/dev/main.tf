# Dev Environment Configuration
# Wires together all AWS modules

locals {
  project_name = var.project_name
  environment  = var.environment_name
  name_prefix  = "${local.project_name}-${local.environment}"
}

# Networking
module "networking" {
  source = "../../modules/networking"

  name_prefix = local.name_prefix
  environment = local.environment

  availability_zones = ["${var.aws_region}a", "${var.aws_region}b"]
  vpc_cidr           = "10.0.0.0/16"
  public_subnet_cidrs = [
    "10.0.1.0/24",
    "10.0.2.0/24"
  ]
  private_subnet_cidrs = [
    "10.0.11.0/24",
    "10.0.12.0/24"
  ]
}

# RDS PostgreSQL Database
module "database" {
  source = "../../modules/database"

  name_prefix               = local.name_prefix
  environment               = local.environment
  vpc_id                    = module.networking.vpc_id
  private_subnet_ids        = module.networking.private_subnet_ids
  allowed_security_group_id = module.networking.app_runner_security_group_id
  instance_class            = var.rds_instance_class
  allocated_storage         = var.rds_storage_gb
  publicly_accessible       = var.rds_public_accessibility
  database_name             = var.database_name
  database_username         = "postgres"
  # Password will be generated and stored in Secrets Manager by bootstrap script
}

# ECR Repository for Docker images
module "backend_ecr" {
  source = "../../modules/ecr"

  name_prefix = local.name_prefix
  environment = local.environment
}

# App Runner Backend Service
module "backend" {
  source = "../../modules/backend"

  name_prefix                  = local.name_prefix
  environment                  = local.environment
  ecr_repository_url           = module.backend_ecr.repository_url
  ecr_image_tag                = var.ecr_image_tag
  app_runner_cpu               = var.app_runner_cpu
  app_runner_memory            = var.app_runner_memory
  vpc_connector_subnets        = module.networking.private_subnet_ids
  app_runner_security_group_id = module.networking.app_runner_security_group_id

  # Secrets Manager secret ARNs
  clerk_secret_key_arn = var.clerk_secret_key_arn
  database_url_arn     = var.rds_database_url_arn

  # SSM Parameter Store ARNs (created by secrets module)
  clerk_jwks_url_param_arn = module.secrets.ssm_clerk_jwks_url_arn
  cors_origins_param_arn   = module.secrets.ssm_cors_origins_arn
  clerk_issuer_param_arn   = var.clerk_issuer != "" ? module.secrets.ssm_clerk_issuer_arn : ""
  clerk_audience_param_arn = var.clerk_audience != "" ? module.secrets.ssm_clerk_audience_arn : ""
}

# Frontend (S3 + CloudFront)
module "frontend" {
  source = "../../modules/frontend"

  name_prefix          = local.name_prefix
  environment          = local.environment
  cors_allowed_origins = var.cors_origins != "" ? split(",", var.cors_origins) : []
}

# Secrets & Configuration
module "secrets" {
  source = "../../modules/secrets"

  name_prefix                = local.name_prefix
  environment                = local.environment
  clerk_jwks_url             = var.clerk_jwks_url
  clerk_issuer               = var.clerk_issuer
  clerk_audience             = var.clerk_audience
  clerk_publishable_key      = var.clerk_publishable_key
  cors_origins               = var.cors_origins
  vite_api_base_url          = module.backend.app_runner_service_url
  vite_clerk_publishable_key = var.clerk_publishable_key
}
