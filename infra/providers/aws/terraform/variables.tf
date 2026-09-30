variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project slug for default tags"
  type        = string
  default     = "cornerstone"
}

variable "environment_name" {
  description = "Environment label for default tags"
  type        = string
  default     = "dev"
}
