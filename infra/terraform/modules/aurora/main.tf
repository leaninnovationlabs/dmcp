# Aurora Serverless v2 Module - Cheapest Configuration for Development
# Supports scaling down to 0 ACUs with auto-pause functionality

# Data sources for existing infrastructure
data "aws_region" "current" {}

data "aws_vpc" "existing" {
  filter {
    name   = "tag:Name"
    values = ["Opsloom VPC"]
  }
}

data "aws_subnets" "database" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }
  
  filter {
    name   = "tag:Name"
    values = ["DB Subnet A", "DB Subnet B"]
  }
}

# Security group for Aurora
resource "aws_security_group" "aurora" {
  name_prefix = "${var.cluster_name}-aurora-"
  vpc_id      = data.aws_vpc.existing.id
  description = "Security group for Aurora Serverless v2 cluster"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.existing.cidr_block]
    description = "PostgreSQL access from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = var.common_tags
}

# Security group for Aurora clients (will be attached to EKS nodes)
resource "aws_security_group" "aurora_client" {
  name_prefix = "${var.cluster_name}-aurora-client-"
  vpc_id      = data.aws_vpc.existing.id
  description = "Security group for Aurora clients"

  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.existing.cidr_block]
    description = "PostgreSQL access to Aurora"
  }

  tags = var.common_tags
}

# Database subnet group
resource "aws_db_subnet_group" "aurora" {
  name       = "${var.cluster_name}-subnet-group"
  subnet_ids = data.aws_subnets.database.ids
  
  tags = merge(var.common_tags, {
    Name = "${var.cluster_name}-subnet-group"
  })
}

# Aurora Serverless v2 Cluster - Cheapest Configuration
resource "aws_rds_cluster" "aurora" {
  cluster_identifier              = var.cluster_name
  engine                         = "aurora-postgresql"
  engine_version                 = var.engine_version
  database_name                  = var.database_name
  master_username                = var.master_username
  manage_master_user_password    = true  # AWS managed password in Secrets Manager
  
  # Network configuration
  vpc_security_group_ids = [aws_security_group.aurora.id]
  db_subnet_group_name   = aws_db_subnet_group.aurora.name
  
  # Serverless v2 scaling configuration - CHEAPEST POSSIBLE
  serverlessv2_scaling_configuration {
    min_capacity = 0    # Scale down to 0 ACUs (auto-pause)
    max_capacity = var.max_capacity
    seconds_until_auto_pause = 300  # Auto-pause after 5 minutes of inactivity
  }
  
  # Cost optimization settings
  backup_retention_period = 1    # Minimum backup retention
  preferred_backup_window = "03:00-04:00"
  preferred_maintenance_window = "sun:04:00-sun:05:00"
  
  # Disable expensive features for development
  enabled_cloudwatch_logs_exports = []
  performance_insights_enabled    = false
  monitoring_interval            = 0  # Disable enhanced monitoring
  
  # Development settings
  skip_final_snapshot       = true
  deletion_protection      = false
  copy_tags_to_snapshot    = true
  storage_encrypted        = true  # Always encrypt
  
  # Apply changes immediately in development
  apply_immediately = true
  
  tags = merge(var.common_tags, {
    Name = var.cluster_name
    Type = "Aurora Serverless v2"
    CostOptimized = "true"
  })
}

# Single Aurora Serverless v2 writer instance
resource "aws_rds_cluster_instance" "aurora" {
  identifier              = "${var.cluster_name}-writer"
  cluster_identifier      = aws_rds_cluster.aurora.id
  instance_class          = "db.serverless"
  engine                  = aws_rds_cluster.aurora.engine
  engine_version          = aws_rds_cluster.aurora.engine_version
  
  # Disable expensive monitoring features
  performance_insights_enabled = false
  monitoring_interval          = 0
  
  # Development settings
  auto_minor_version_upgrade = false
  publicly_accessible      = false
  
  tags = var.common_tags
}

# Store connection string in Parameter Store as SecureString
# Note: This stores a template URL since the password is managed by AWS Secrets Manager
resource "aws_ssm_parameter" "database_url" {
  name  = "/${var.environment}/dbmcp/database_url"
  type  = "SecureString"
  value = "postgresql+asyncpg://${aws_rds_cluster.aurora.master_username}:{get_password_from_secrets_manager}@${aws_rds_cluster.aurora.endpoint}:${aws_rds_cluster.aurora.port}/${aws_rds_cluster.aurora.database_name}"
  
  description = "Aurora Serverless v2 database connection string template for DBMCP (password in Secrets Manager)"
  
  tags = merge(var.common_tags, {
    Component = "Database"
    Secret = "true"
  })
}

# Store individual connection components for flexibility
resource "aws_ssm_parameter" "database_host" {
  name  = "/${var.environment}/dbmcp/database_host"
  type  = "SecureString"
  value = aws_rds_cluster.aurora.endpoint
  
  tags = var.common_tags
}

resource "aws_ssm_parameter" "database_port" {
  name  = "/${var.environment}/dbmcp/database_port"
  type  = "String"
  value = tostring(aws_rds_cluster.aurora.port)
  
  tags = var.common_tags
}

resource "aws_ssm_parameter" "database_name" {
  name  = "/${var.environment}/dbmcp/database_name"
  type  = "String"
  value = aws_rds_cluster.aurora.database_name
  
  tags = var.common_tags
}

resource "aws_ssm_parameter" "database_username" {
  name  = "/${var.environment}/dbmcp/database_username"
  type  = "SecureString"
  value = aws_rds_cluster.aurora.master_username
  
  tags = var.common_tags
}

resource "aws_ssm_parameter" "database_secret_arn" {
  name  = "/${var.environment}/dbmcp/database_secret_arn"
  type  = "SecureString"
  value = aws_rds_cluster.aurora.master_user_secret[0].secret_arn
  
  description = "ARN of the Aurora master user secret in AWS Secrets Manager"
  
  tags = var.common_tags
}

# IAM Role for EKS Service Account to access Parameter Store
data "aws_eks_cluster" "existing" {
  name = "opsloom-eks"  # Based on config
}

data "aws_iam_openid_connect_provider" "eks" {
  url = data.aws_eks_cluster.existing.identity[0].oidc[0].issuer
}

data "aws_iam_policy_document" "parameter_store_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.eks.arn]
    }
    actions = ["sts:AssumeRoleWithWebIdentity"]
    condition {
      test     = "StringEquals"
      variable = "${replace(data.aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:dbmcp-${var.environment}:dbmcp"]
    }
    condition {
      test     = "StringEquals"
      variable = "${replace(data.aws_iam_openid_connect_provider.eks.url, "https://", "")}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "parameter_store_role" {
  name               = "${var.cluster_name}-parameter-store-role"
  assume_role_policy = data.aws_iam_policy_document.parameter_store_assume_role.json
  
  tags = var.common_tags
}

data "aws_iam_policy_document" "parameter_store_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:ssm:*:*:parameter/${var.environment}/dbmcp/*"
    ]
  }
  
  # Allow access to Secrets Manager for Aurora master password
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      aws_rds_cluster.aurora.master_user_secret[0].secret_arn
    ]
  }
  
  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt"
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = [
        "ssm.${data.aws_region.current.name}.amazonaws.com",
        "secretsmanager.${data.aws_region.current.name}.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_policy" "parameter_store_policy" {
  name        = "${var.cluster_name}-parameter-store-policy"
  description = "Policy for accessing Parameter Store for DBMCP"
  policy      = data.aws_iam_policy_document.parameter_store_policy.json
  
  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "parameter_store_policy_attachment" {
  role       = aws_iam_role.parameter_store_role.name
  policy_arn = aws_iam_policy.parameter_store_policy.arn
}