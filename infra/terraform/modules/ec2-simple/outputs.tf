/**
 * Outputs for EC2 Simple Module
 * 
 * Provides key information about the created resources.
 */

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.dbmcp.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.dbmcp.public_ip
}

output "instance_private_ip" {
  description = "Private IP address of the EC2 instance"
  value       = aws_instance.dbmcp.private_ip
}

output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.dbmcp.dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.dbmcp.zone_id
}

output "load_balancer_arn" {
  description = "ARN of the load balancer"
  value       = aws_lb.dbmcp.arn
}

output "fastapi_target_group_arn" {
  description = "ARN of the FastAPI target group"
  value       = aws_lb_target_group.fastapi.arn
}

output "mcp_target_group_arn" {
  description = "ARN of the MCP target group"
  value       = aws_lb_target_group.mcp.arn
}

output "ec2_security_group_id" {
  description = "ID of the EC2 security group"
  value       = aws_security_group.ec2.id
}

output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "iam_role_arn" {
  description = "ARN of the IAM role for the EC2 instance"
  value       = aws_iam_role.ec2_role.arn
}

output "application_url" {
  description = "URL to access the application"
  value       = "https://${var.domain_name}"
}

output "ssl_certificate_arn" {
  description = "ARN of the SSL certificate used"
  value       = data.aws_acm_certificate.opsloom.arn
}

output "ssh_key_name" {
  description = "Name of the SSH key pair"
  value       = aws_key_pair.ec2_key.key_name
}

output "ssh_private_key_path" {
  description = "Path to the SSH private key file"
  value       = local_file.private_key.filename
}