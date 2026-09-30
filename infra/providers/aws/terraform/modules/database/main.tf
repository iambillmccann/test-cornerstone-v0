variable "name_prefix" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "allowed_security_group_id" {
  type = string
}

variable "instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "allocated_storage" {
  type    = number
  default = 20
}

variable "publicly_accessible" {
  type    = bool
  default = false
}

variable "database_name" {
  type = string
}

variable "database_username" {
  type = string
}

output "rds_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive = true
}

output "rds_port" {
  value = aws_db_instance.main.port
}

output "rds_database_name" {
  value = aws_db_instance.main.db_name
}

output "rds_security_group_id" {
  value = aws_security_group.rds.id
}

# RDS Security Group (separate from networking module for module composition)
resource "aws_security_group" "rds" {
  name_prefix = "${var.name_prefix}-rds-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.allowed_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.name_prefix}-rds-sg"
  }
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.name_prefix}-rds-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.name_prefix}-rds-subnet-group"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier                  = "${var.name_prefix}-db"
  engine                      = "postgres"
  engine_version              = "16"
  instance_class              = var.instance_class
  allocated_storage           = var.allocated_storage
  db_name                     = var.database_name
  username                    = var.database_username
  manage_master_user_password = true

  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  publicly_accessible     = var.publicly_accessible
  skip_final_snapshot     = true
  multi_az                = false
  storage_encrypted       = false
  backup_retention_period = 1
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"
  deletion_protection     = false

  tags = {
    Name = "${var.name_prefix}-db"
  }
}

# CloudWatch Alarm for CPU
resource "aws_cloudwatch_metric_alarm" "cpu" {
  alarm_name          = "${var.name_prefix}-db-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alert when RDS CPU exceeds 80%"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}
