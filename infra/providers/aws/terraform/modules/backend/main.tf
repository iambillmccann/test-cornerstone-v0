variable "name_prefix" {
  type = string
}

variable "environment" {
  type = string
}

variable "ecr_repository_url" {
  type = string
}

variable "ecr_image_tag" {
  type    = string
  default = "latest"
}

variable "app_runner_cpu" {
  type    = number
  default = 256
}

variable "app_runner_memory" {
  type    = number
  default = 512
}

variable "vpc_connector_subnets" {
  type    = list(string)
  default = []
}

variable "app_runner_security_group_id" {
  type = string
}

variable "clerk_secret_key_arn" {
  type      = string
  sensitive = true
}

variable "database_url_arn" {
  type      = string
  sensitive = true
}

variable "clerk_jwks_url_param_arn" {
  type = string
}

variable "cors_origins_param_arn" {
  type = string
}

variable "clerk_issuer_param_arn" {
  type = string
}

variable "clerk_audience_param_arn" {
  type = string
}

output "app_runner_service_url" {
  value = aws_apprunner_service.main.service_url
}

output "app_runner_service_arn" {
  value = aws_apprunner_service.main.arn
}

output "app_runner_role_arn" {
  value = aws_iam_role.app_runner_role.arn
}

output "app_runner_ecr_access_role_arn" {
  value = aws_iam_role.app_runner_ecr_access_role.arn
}

output "ecr_repository_url" {
  value = var.ecr_repository_url
}

# IAM Role for App Runner
resource "aws_iam_role" "app_runner_role" {
  name_prefix = "${var.name_prefix}-app-runner-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "tasks.apprunner.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.name_prefix}-app-runner-role"
  }
}

# IAM Role for App Runner to authenticate and pull private images from ECR
resource "aws_iam_role" "app_runner_ecr_access_role" {
  name_prefix = "${var.name_prefix}-apprunner-ecr-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.name_prefix}-app-runner-ecr-access-role"
  }
}

resource "aws_iam_role_policy_attachment" "app_runner_ecr_access" {
  role       = aws_iam_role.app_runner_ecr_access_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

# Policy for Secrets Manager access
resource "aws_iam_role_policy" "secrets_manager" {
  name_prefix = "${var.name_prefix}-secrets-"
  role        = aws_iam_role.app_runner_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          var.clerk_secret_key_arn,
          var.database_url_arn
        ]
      }
    ]
  })
}

# Policy for SSM Parameter Store access
resource "aws_iam_role_policy" "ssm_parameters" {
  name_prefix = "${var.name_prefix}-ssm-"
  role        = aws_iam_role.app_runner_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = compact([
          var.clerk_jwks_url_param_arn,
          var.cors_origins_param_arn,
          var.clerk_issuer_param_arn,
          var.clerk_audience_param_arn
        ])
      }
    ]
  })
}

resource "aws_apprunner_vpc_connector" "main" {
  vpc_connector_name = "${var.name_prefix}-connector"
  subnets            = var.vpc_connector_subnets
  security_groups    = [var.app_runner_security_group_id]

  tags = {
    Name = "${var.name_prefix}-vpc-connector"
  }
}

# App Runner Service
resource "aws_apprunner_service" "main" {
  service_name = "${var.name_prefix}-api"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.app_runner_ecr_access_role.arn
    }

    image_repository {
      image_identifier      = "${var.ecr_repository_url}:${var.ecr_image_tag}"
      image_repository_type = "ECR"

      image_configuration {
        port = "8000"

        runtime_environment_secrets = merge(
          {
            "CLERK_SECRET_KEY" = var.clerk_secret_key_arn
            "DATABASE_URL"     = var.database_url_arn
            "CLERK_JWKS_URL"   = var.clerk_jwks_url_param_arn
            "CORS_ORIGINS"     = var.cors_origins_param_arn
          },
          var.clerk_issuer_param_arn != "" ? {
            "CLERK_ISSUER" = var.clerk_issuer_param_arn
          } : {},
          var.clerk_audience_param_arn != "" ? {
            "CLERK_AUDIENCE" = var.clerk_audience_param_arn
          } : {}
        )
      }
    }

    auto_deployments_enabled = false # GitHub Actions controls deployment
  }

  instance_configuration {
    cpu               = tostring(var.app_runner_cpu)
    memory            = tostring(var.app_runner_memory)
    instance_role_arn = aws_iam_role.app_runner_role.arn
  }

  network_configuration {
    egress_configuration {
      egress_type       = "VPC"
      vpc_connector_arn = aws_apprunner_vpc_connector.main.arn
    }
  }

  tags = {
    Name = "${var.name_prefix}-app-runner"
  }

  depends_on = [
    aws_iam_role_policy_attachment.app_runner_ecr_access,
    aws_iam_role_policy.secrets_manager,
    aws_iam_role_policy.ssm_parameters,
    aws_apprunner_vpc_connector.main
  ]
}

# CloudWatch Alarm for App Runner
resource "aws_cloudwatch_metric_alarm" "cpu" {
  alarm_name          = "${var.name_prefix}-app-runner-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/AppRunner"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alert when App Runner CPU exceeds 80%"

  dimensions = {
    ServiceName = aws_apprunner_service.main.service_name
  }
}
