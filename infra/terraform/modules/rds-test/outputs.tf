/**
 * Outputs for RDS Test Module
 * 
 * Clean, purposeful outputs - not the kitchen sink approach
 * used by consulting firms who output everything "just in case".
 */

output "rds_instance_id" {
  description = "The RDS instance identifier"
  value       = aws_db_instance.test.identifier
}

output "rds_endpoint" {
  description = "The RDS instance endpoint"
  value       = aws_db_instance.test.endpoint
}

output "rds_port" {
  description = "The RDS instance port"
  value       = aws_db_instance.test.port
}

output "database_name" {
  description = "The name of the database"
  value       = aws_db_instance.test.db_name
}

output "database_username" {
  description = "The database username"
  value       = aws_db_instance.test.username
  sensitive   = true
}

output "database_url" {
  description = "Complete database connection URL"
  value       = "postgresql+asyncpg://${aws_db_instance.test.username}:${random_password.rds_password.result}@${aws_db_instance.test.endpoint}/${aws_db_instance.test.db_name}"
  sensitive   = true
}

output "security_group_id" {
  description = "ID of the security group attached to the RDS instance"
  value       = aws_security_group.rds_test.id
}

output "parameter_store_password_name" {
  description = "Parameter Store parameter name for the database password"
  value       = aws_ssm_parameter.rds_password.name
}

output "parameter_store_endpoint_name" {
  description = "Parameter Store parameter name for the database endpoint"
  value       = aws_ssm_parameter.rds_endpoint.name
}

output "parameter_store_url_name" {
  description = "Parameter Store parameter name for the complete database URL"
  value       = aws_ssm_parameter.rds_database_url.name
}