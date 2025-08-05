# DBMCP EC2 Simple Deployment Guide

## Overview

This document describes the simplified EC2-based deployment architecture that replaces the complex Kubernetes/EKS setup. The new architecture follows the KISS principle with a single EC2 instance, Application Load Balancer, and Ansible-based container management.

## Architecture Components

### 1. Infrastructure (Terraform)
- **EC2 Instance**: Single t3.medium instance running Amazon Linux 2
- **Application Load Balancer**: Path-based routing with SSL termination
- **Security Groups**: Minimal required permissions
- **IAM Roles**: EC2 instance profile with Parameter Store and ECR access
- **Route 53**: DNS configuration for the domain

### 2. Application Deployment (Ansible)
- **Docker Compose**: Orchestrates FastAPI and MCP containers
- **Container Management**: Start, stop, upgrade operations
- **Configuration**: Environment-specific settings via templates
- **Monitoring**: Health checks and logging

## Path-Based Routing

The ALB routes traffic based on URL paths:
- `/dbmcp/*` → FastAPI server (port 8000)
- `/` → FastAPI server (port 8000) 
- `/mcp/*` → MCP server (port 4200)

## Key Files Created

### Terraform Module
- `infra/terraform/modules/ec2-simple/main.tf` - Core infrastructure
- `infra/terraform/modules/ec2-simple/variables.tf` - Input variables
- `infra/terraform/modules/ec2-simple/outputs.tf` - Outputs
- `infra/terraform/modules/ec2-simple/user_data.sh` - EC2 initialization script

### Ansible Playbooks
- `infra/ansible/inventory/development.yml` - Environment inventory
- `infra/ansible/playbooks/deploy.yml` - Full deployment
- `infra/ansible/playbooks/start.yml` - Start services
- `infra/ansible/playbooks/stop.yml` - Stop services
- `infra/ansible/playbooks/upgrade.yml` - Rolling upgrade
- `infra/ansible/playbooks/templates/docker-compose.yml.j2` - Docker Compose template
- `infra/ansible/playbooks/templates/.env.j2` - Environment file template

### Configuration Updates
- `infra/config/development.yml` - Added EC2 configuration section
- `infra/terraform/main.tf` - Replaced EKS with EC2 simple module
- `infra/terraform/outputs.tf` - Added EC2 outputs
- `Makefile` - Added EC2 deployment targets

## Deployment Commands

### Initial Deployment
```bash
make ec2-deploy ENV=development
```

### Service Management
```bash
make ec2-start ENV=development    # Start services
make ec2-stop ENV=development     # Stop services
make ec2-upgrade ENV=development  # Rolling upgrade
make ec2-status ENV=development   # Show status
```

### Monitoring and Debugging
```bash
make ec2-ssh ENV=development      # SSH into instance
make ec2-logs ENV=development     # View application logs
```

## Benefits of EC2 Simple Architecture

1. **Simplicity**: Single instance, easy to understand and debug
2. **Cost-effective**: No EKS control plane costs (~$72/month savings)
3. **Fast deployment**: No complex Kubernetes orchestration
4. **Direct access**: Easy SSH access for debugging
5. **Predictable**: No pod scheduling or node management complexity

## Migration from EKS

The new architecture maintains the same:
- Database connectivity (Aurora Serverless v2)
- Parameter Store configuration
- ECR container registry
- SSL/TLS termination
- Domain routing

## Security Features

- IAM instance profile with minimal permissions
- Security groups with restricted access
- Encrypted EBS volumes
- SSL termination at ALB
- VPC-only SSH access

## Monitoring and Logging

- Docker container health checks
- Application-level health endpoints
- Centralized logging to `/var/log/dbmcp`
- CloudWatch agent ready for installation

## Next Steps

1. Test the deployment: `make ec2-deploy ENV=development`
2. Verify application functionality
3. Clean up old EKS infrastructure
4. Update documentation and CI/CD pipelines

## Cost Comparison

**EKS Architecture (old)**:
- EKS control plane: ~$72/month
- Worker nodes: ~$30/month (t3.medium)
- Load balancer: ~$18/month
- **Total: ~$120/month**

**EC2 Simple Architecture (new)**:
- EC2 instance: ~$30/month (t3.medium)
- Application Load Balancer: ~$18/month
- **Total: ~$48/month**

**Savings: ~$72/month (60% reduction)**