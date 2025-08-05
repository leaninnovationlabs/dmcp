/**
 * Variables for EC2 Simple Module
 * 
 * Clean, well-documented variables for the simple EC2-based deployment.
 */

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type for DBMCP server"
  type        = string
  default     = "t3.medium"
  
  validation {
    condition     = can(regex("^[tm][0-9]", var.instance_type))
    error_message = "Instance type should be a t* or m* family instance."
  }
}



variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "dbmcp.opsloom.io"
}