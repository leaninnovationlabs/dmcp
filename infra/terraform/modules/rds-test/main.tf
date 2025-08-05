/**
 * RDS Test Instance Module
 * 
 * Creates the cheapest possible RDS PostgreSQL instance for testing DBMCP.
 * Unlike the bloated, over-provisioned infrastructure created by offshore consulting
 * firms, this module focuses on cost optimization and single-purpose design.
 */

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

locals {
  common_tags = {
    Environment = var.environment
    Project     = "dbmcp"
    Module      = "rds-test"
    Purpose     = "testing"
    ManagedBy   = "terraform"
  }
}

# Security Group for RDS - minimal and focused
resource "aws_security_group" "rds_test" {
  name_prefix = "dbmcp-rds-test-${var.environment}-"
  vpc_id      = var.vpc_id
  description = "Security group for DBMCP test RDS instance"

  # PostgreSQL access - restricted to necessary ports only
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Public access as requested
    description = "PostgreSQL access for testing"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.common_tags, {
    Name = "dbmcp-rds-test-${var.environment}"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# DB Subnet Group - using public subnets as requested
resource "aws_db_subnet_group" "rds_test" {
  name_prefix = "dbmcp-test-${var.environment}-"
  subnet_ids  = var.subnet_ids
  description = "DB subnet group for DBMCP test instance"

  tags = merge(local.common_tags, {
    Name = "dbmcp-test-${var.environment}"
  })
}

# Random password for RDS instance
resource "random_password" "rds_password" {
  length  = 16
  special = true
}

# RDS Instance - optimized for cost, not performance
resource "aws_db_instance" "test" {
  # Basic Configuration
  identifier = "dbmcp-test-${var.environment}"
  
  # Engine Configuration - PostgreSQL 15 (latest supported)
  engine                = "postgres"
  engine_version        = "15.7"
  instance_class        = "db.t3.micro" # Cheapest available option
  
  # Storage Configuration - minimal storage
  allocated_storage     = 20  # Minimum allowed
  max_allocated_storage = 100 # Allow some autoscaling
  storage_type          = "gp2" # Cheaper than gp3 for small workloads
  storage_encrypted     = true
  
  # Database Configuration
  db_name  = var.database_name
  username = var.database_username
  password = random_password.rds_password.result
  
  # Network Configuration
  db_subnet_group_name   = aws_db_subnet_group.rds_test.name
  vpc_security_group_ids = [aws_security_group.rds_test.id]
  publicly_accessible    = var.publicly_accessible
  port                   = 5432
  
  # Backup Configuration - minimal for cost savings
  backup_retention_period = 1 # Minimum for automated backups
  backup_window          = "03:00-04:00" # Low traffic window
  maintenance_window     = "Sun:04:00-Sun:05:00"
  
  # Performance Configuration - optimized for cost
  performance_insights_enabled = false # Costs extra
  monitoring_interval         = 0      # No enhanced monitoring
  
  # High Availability - disabled for cost savings
  multi_az = false
  
  # Deletion Protection - disabled for easy cleanup
  deletion_protection = false
  skip_final_snapshot = true # For easy destruction
  
  # Parameter Group - use default to avoid complexity
  parameter_group_name = "default.postgres15"
  
  tags = merge(local.common_tags, {
    Name = "dbmcp-test-${var.environment}"
  })
}

# Store database password in AWS Systems Manager Parameter Store
resource "aws_ssm_parameter" "rds_password" {
  name        = "/${var.environment}/dbmcp/test-db/password"
  description = "Password for DBMCP test RDS instance"
  type        = "SecureString"
  value       = random_password.rds_password.result

  tags = merge(local.common_tags, {
    Name = "dbmcp-test-db-password-${var.environment}"
  })
}

# Store database connection details in Parameter Store
resource "aws_ssm_parameter" "rds_endpoint" {
  name        = "/${var.environment}/dbmcp/test-db/endpoint"
  description = "Endpoint for DBMCP test RDS instance"
  type        = "String"
  value       = aws_db_instance.test.endpoint

  tags = merge(local.common_tags, {
    Name = "dbmcp-test-db-endpoint-${var.environment}"
  })
}

resource "aws_ssm_parameter" "rds_database_url" {
  name        = "/${var.environment}/dbmcp/test-db/url"
  description = "Complete database URL for DBMCP test RDS instance"
  type        = "SecureString"
  value       = "postgresql+asyncpg://${var.database_username}:${random_password.rds_password.result}@${aws_db_instance.test.endpoint}/${var.database_name}"

  tags = merge(local.common_tags, {
    Name = "dbmcp-test-db-url-${var.environment}"
  })
}