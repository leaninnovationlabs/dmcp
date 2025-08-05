output "fastapi_repository_url" {
  description = "URL of the FastAPI ECR repository"
  value       = aws_ecr_repository.fastapi.repository_url
}

output "mcp_repository_url" {
  description = "URL of the MCP ECR repository"
  value       = aws_ecr_repository.mcp.repository_url
}

output "fastapi_repository_name" {
  description = "Name of the FastAPI ECR repository"
  value       = aws_ecr_repository.fastapi.name
}

output "mcp_repository_name" {
  description = "Name of the MCP ECR repository"
  value       = aws_ecr_repository.mcp.name
}

# Legacy compatibility outputs
output "repository_url" {
  description = "URL of the FastAPI ECR repository (legacy compatibility)"
  value       = aws_ecr_repository.fastapi.repository_url
}

output "repository_name" {
  description = "Name of the FastAPI ECR repository (legacy compatibility)"
  value       = aws_ecr_repository.fastapi.name
}