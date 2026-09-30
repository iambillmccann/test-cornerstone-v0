variable "name_prefix" {
  type = string
}

variable "environment" {
  type = string
}

variable "clerk_jwks_url" {
  type      = string
  sensitive = true
}

variable "clerk_issuer" {
  type      = string
  sensitive = true
  default   = ""
}

variable "clerk_audience" {
  type      = string
  sensitive = true
  default   = ""
}

variable "clerk_publishable_key" {
  type      = string
  sensitive = true
}

variable "cors_origins" {
  type = string
}

variable "vite_api_base_url" {
  type = string
}

variable "vite_clerk_publishable_key" {
  type      = string
  sensitive = true
}

output "database_url_secret_arn" {
  value = "arn:aws:secretsmanager:*:*:secret:${var.name_prefix}-database-url-*"
}

output "clerk_secret_key_arn" {
  value = "arn:aws:secretsmanager:*:*:secret:${var.name_prefix}-clerk-secret-key-*"
}

output "ssm_clerk_jwks_url" {
  value = aws_ssm_parameter.clerk_jwks_url.name
}

output "ssm_clerk_jwks_url_arn" {
  value = aws_ssm_parameter.clerk_jwks_url.arn
}

output "ssm_clerk_jwks_url_name" {
  value = aws_ssm_parameter.clerk_jwks_url.name
}

output "ssm_clerk_issuer" {
  value = aws_ssm_parameter.clerk_issuer.name
}

output "ssm_clerk_issuer_arn" {
  value = aws_ssm_parameter.clerk_issuer.arn
}

output "ssm_clerk_issuer_name" {
  value = aws_ssm_parameter.clerk_issuer.name
}

output "ssm_clerk_audience" {
  value = aws_ssm_parameter.clerk_audience.name
}

output "ssm_clerk_audience_arn" {
  value = aws_ssm_parameter.clerk_audience.arn
}

output "ssm_clerk_audience_name" {
  value = aws_ssm_parameter.clerk_audience.name
}

output "ssm_cors_origins" {
  value = aws_ssm_parameter.cors_origins.name
}

output "ssm_cors_origins_arn" {
  value = aws_ssm_parameter.cors_origins.arn
}

output "ssm_cors_origins_name" {
  value = aws_ssm_parameter.cors_origins.name
}

output "ssm_vite_api_base_url" {
  value = aws_ssm_parameter.vite_api_base_url.name
}

output "ssm_vite_clerk_publishable_key" {
  value = aws_ssm_parameter.vite_clerk_publishable_key.name
}

# SSM Parameters for configuration
resource "aws_ssm_parameter" "clerk_jwks_url" {
  name      = "/${var.name_prefix}/clerk_jwks_url"
  type      = "SecureString"
  value     = var.clerk_jwks_url
  overwrite = true

  tags = {
    Name = "${var.name_prefix}-clerk-jwks-url"
  }
}

resource "aws_ssm_parameter" "clerk_issuer" {
  name      = "/${var.name_prefix}/clerk_issuer"
  type      = "String"
  value     = var.clerk_issuer != "" ? var.clerk_issuer : "placeholder"
  overwrite = true

  tags = {
    Name = "${var.name_prefix}-clerk-issuer"
  }
}

resource "aws_ssm_parameter" "clerk_audience" {
  name      = "/${var.name_prefix}/clerk_audience"
  type      = "String"
  value     = var.clerk_audience != "" ? var.clerk_audience : "placeholder"
  overwrite = true

  tags = {
    Name = "${var.name_prefix}-clerk-audience"
  }
}

resource "aws_ssm_parameter" "cors_origins" {
  name      = "/${var.name_prefix}/cors_origins"
  type      = "String"
  value     = var.cors_origins != "" ? var.cors_origins : "http://localhost:5173"
  overwrite = true

  tags = {
    Name = "${var.name_prefix}-cors-origins"
  }
}

resource "aws_ssm_parameter" "vite_api_base_url" {
  name      = "/${var.name_prefix}/vite_api_base_url"
  type      = "String"
  value     = var.vite_api_base_url
  overwrite = true

  tags = {
    Name = "${var.name_prefix}-vite-api-base-url"
  }
}

resource "aws_ssm_parameter" "vite_clerk_publishable_key" {
  name      = "/${var.name_prefix}/vite_clerk_publishable_key"
  type      = "String"
  value     = var.vite_clerk_publishable_key
  overwrite = true

  tags = {
    Name = "${var.name_prefix}-vite-clerk-publishable-key"
  }
}
