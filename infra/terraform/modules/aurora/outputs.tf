output "cluster_id" {
  description = "Aurora cluster identifier"
  value       = aws_rds_cluster.aurora.cluster_identifier
}

output "cluster_endpoint" {
  description = "Aurora cluster endpoint"
  value       = aws_rds_cluster.aurora.endpoint
}

output "cluster_reader_endpoint" {
  description = "Aurora cluster reader endpoint"
  value       = aws_rds_cluster.aurora.reader_endpoint
}

output "cluster_port" {
  description = "Aurora cluster port"
  value       = aws_rds_cluster.aurora.port
}

output "cluster_database_name" {
  description = "Aurora cluster database name"
  value       = aws_rds_cluster.aurora.database_name
}

output "cluster_master_username" {
  description = "Aurora cluster master username"
  value       = aws_rds_cluster.aurora.master_username
  sensitive   = true
}

output "cluster_master_user_secret_arn" {
  description = "ARN of the master user secret in AWS Secrets Manager"
  value       = aws_rds_cluster.aurora.master_user_secret[0].secret_arn
}

output "cluster_security_group_id" {
  description = "Security group ID for Aurora cluster"
  value       = aws_security_group.aurora.id
}

output "client_security_group_id" {
  description = "Security group ID for Aurora clients (attach to EKS nodes)"
  value       = aws_security_group.aurora_client.id
}

output "parameter_store_database_url" {
  description = "Parameter Store path for database URL"
  value       = aws_ssm_parameter.database_url.name
}

output "parameter_store_database_host" {
  description = "Parameter Store path for database host"
  value       = aws_ssm_parameter.database_host.name
}

output "cost_estimate_monthly" {
  description = "Estimated monthly cost for Aurora Serverless v2 (0-2 ACUs, us-east-1)"
  value       = "~$0-29/month (0 ACU when paused, ~$14.40/month at 0.5 ACU average, ~$28.80/month at 1 ACU average)"
}

output "parameter_store_iam_role_arn" {
  description = "IAM role ARN for Parameter Store access (for IRSA)"
  value       = aws_iam_role.parameter_store_role.arn
}