locals {
  # Load configuration from YAML file based on environment
  config_file = "../config/${var.environment}.yml"
  config      = yamldecode(file(local.config_file))
  
  # Common tags for all resources
  common_tags = {
    Environment   = local.config.environment
    Project       = local.config.app.name
    ManagedBy     = "terraform"
    Region        = local.config.region
  }
  
  # ECR repository name
  ecr_repository_name = local.config.ecr.repository_name
  
  
  # Application configuration
  app_name     = local.config.app.name
  app_version  = local.config.app.version
  app_port     = local.config.app.port
  
  
  # Database configuration
  database_cluster_name     = local.config.database.aurora.cluster_name
  database_engine_version   = local.config.database.aurora.engine_version
  database_max_capacity     = local.config.database.aurora.max_capacity
  database_parameter_store  = local.config.database.parameter_store_url
} 