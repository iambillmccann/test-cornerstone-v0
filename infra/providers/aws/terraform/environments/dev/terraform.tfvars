aws_region       = "us-east-2"
environment_name = "dev"

# Clerk
clerk_jwks_url = "https://immortal-lark-23.clerk.accounts.dev/.well-known/jwks.json"
# Optional for compatibility, but recommended for strict JWT validation:
clerk_issuer          = ""
clerk_audience        = ""
clerk_publishable_key = "pk_test_aW1tb3J0YWwtbGFyay0yMy5jbGVyay5hY2NvdW50cy5kZXYk"

# These ARNs are output by bootstrap-state.sh
clerk_secret_key_arn = "arn:aws:secretsmanager:us-east-2:098295335350:secret:cornerstone-clerk-secret-key-WDz7OH"
rds_database_url_arn = "arn:aws:secretsmanager:us-east-2:098295335350:secret:cornerstone-database-url-A55JW2"

# RDS Configuration
rds_instance_class       = "db.t4g.micro"
rds_storage_gb           = 20
rds_public_accessibility = false

# CORS (set after first provision when CloudFront domain is known)
cors_origins = "https://d32c4rkhhvc6sn.cloudfront.net"

# Docker
ecr_image_tag = "latest"

# App Runner
app_runner_cpu    = 256
app_runner_memory = 512
