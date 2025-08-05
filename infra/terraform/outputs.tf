output "ecr_fastapi_repository_url" {
  description = "FastAPI ECR repository URL"
  value       = module.ecr.fastapi_repository_url
}

output "ecr_mcp_repository_url" {
  description = "MCP ECR repository URL"
  value       = module.ecr.mcp_repository_url
}

# Legacy compatibility
output "ecr_repository_url" {
  description = "ECR repository URL (legacy compatibility)"
  value       = module.ecr.repository_url
}



output "ecr_fastapi_repository_arn" {
  description = "FastAPI ECR repository ARN"
  value       = module.ecr.fastapi_repository_name
}

output "ecr_mcp_repository_arn" {
  description = "MCP ECR repository ARN"  
  value       = module.ecr.mcp_repository_name
}

# General outputs
output "region" {
  description = "AWS region"
  value       = var.aws_region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "app_name" {
  description = "Application name from config"
  value       = local.app_name
}

# Aurora Serverless v2 outputs
output "aurora_cluster_endpoint" {
  description = "Aurora cluster endpoint"
  value       = module.aurora.cluster_endpoint
}

output "aurora_cluster_id" {
  description = "Aurora cluster identifier"
  value       = module.aurora.cluster_id
}

output "aurora_parameter_store_url" {
  description = "Parameter Store path for database URL"
  value       = module.aurora.parameter_store_database_url
}

output "aurora_cost_estimate" {
  description = "Estimated monthly cost for Aurora Serverless v2"
  value       = module.aurora.cost_estimate_monthly
}

output "aurora_client_security_group" {
  description = "Security group ID for Aurora clients (attach to EKS nodes)"
  value       = module.aurora.client_security_group_id
}

output "parameter_store_iam_role_arn" {
  description = "IAM role ARN for Parameter Store access (for IRSA)"
  value       = module.aurora.parameter_store_iam_role_arn
}

# RDS Test Database outputs (conditional)
output "rds_test_endpoint" {
  description = "RDS test instance endpoint"
  value       = try(module.rds_test[0].rds_endpoint, null)
}

output "rds_test_database_url" {
  description = "RDS test database connection URL"
  value       = try(module.rds_test[0].database_url, null)
  sensitive   = true
}

output "rds_test_parameter_store_url" {
  description = "Parameter Store path for RDS test database URL"
  value       = try(module.rds_test[0].parameter_store_url_name, null)
}

output "rds_test_instance_id" {
  description = "RDS test instance identifier"
  value       = try(module.rds_test[0].rds_instance_id, null)
}

# EC2 Simple Module outputs
output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = module.ec2_simple.instance_id
}

output "ec2_public_ip" {
  description = "EC2 instance public IP"
  value       = module.ec2_simple.instance_public_ip
}

output "ec2_private_ip" {
  description = "EC2 instance private IP"  
  value       = module.ec2_simple.instance_private_ip
}

output "load_balancer_dns" {
  description = "Application Load Balancer DNS name"
  value       = module.ec2_simple.load_balancer_dns
}

output "application_url" {
  description = "Application URL"
  value       = module.ec2_simple.application_url
}

output "ec2_security_group_id" {
  description = "EC2 security group ID"
  value       = module.ec2_simple.ec2_security_group_id
}

output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = module.ec2_simple.alb_security_group_id
}

output "ssl_certificate_arn" {
  description = "ARN of the SSL certificate used"
  value       = module.ec2_simple.ssl_certificate_arn
} 