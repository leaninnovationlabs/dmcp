/**
 * Simple EC2-based deployment for DBMCP
 * 
 * This module creates a single EC2 instance with proper IAM roles,
 * an Application Load Balancer with path-based routing, and all
 * necessary security groups.
 * 
 * Unlike the overcomplicated Kubernetes setup, this follows the KISS principle:
 * one instance, clear routing, simple management.
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
    Module      = "ec2-simple"
    ManagedBy   = "terraform"
  }
}

# Data sources for existing infrastructure
data "aws_vpc" "existing" {
  filter {
    name   = "tag:Name"
    values = ["Opsloom VPC"]
  }
}

# Auto-discover SSL certificate for opsloom.io domain
data "aws_acm_certificate" "opsloom" {
  domain      = "opsloom.io"
  statuses    = ["ISSUED"]
  most_recent = true
}

# Generate SSH key pair for EC2 access
resource "tls_private_key" "ec2_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "ec2_key" {
  key_name   = "dbmcp-${var.environment}"
  public_key = tls_private_key.ec2_key.public_key_openssh

  tags = local.common_tags
}

# Store private key locally for Ansible access
resource "local_file" "private_key" {
  content         = tls_private_key.ec2_key.private_key_pem
  filename        = "${path.root}/../../.ssh/dbmcp-${var.environment}.pem"
  file_permission = "0600"
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }
  
  filter {
    name   = "tag:Name"
    values = ["*Public*"]
  }
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# IAM role for EC2 instance
resource "aws_iam_role" "ec2_role" {
  name = "dbmcp-${var.environment}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# IAM policy for Parameter Store, ECR access, and SSM Session Manager
resource "aws_iam_role_policy" "ec2_policy" {
  name = "dbmcp-${var.environment}-ec2-policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = "arn:aws:ssm:*:*:parameter/${var.environment}/dbmcp/*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach AWS managed policy for SSM Session Manager
resource "aws_iam_role_policy_attachment" "ssm_managed_instance" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Instance profile
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "dbmcp-${var.environment}-ec2-profile"
  role = aws_iam_role.ec2_role.name

  tags = local.common_tags
}

# Security group for EC2 instance
resource "aws_security_group" "ec2" {
  name_prefix = "dbmcp-${var.environment}-ec2-"
  vpc_id      = data.aws_vpc.existing.id
  description = "Security group for DBMCP EC2 instance"

  # HTTP access from ALB
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "FastAPI from ALB"
  }

  ingress {
    from_port       = 4200
    to_port         = 4200
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "MCP server from ALB"
  }

  # SSH access (optional, for debugging)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16", "168.91.246.97/32"]  # VPC and deployment IP
    description = "SSH access from VPC and deployment"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.common_tags, {
    Name = "dbmcp-${var.environment}-ec2"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Security group for ALB
resource "aws_security_group" "alb" {
  name_prefix = "dbmcp-${var.environment}-alb-"
  vpc_id      = data.aws_vpc.existing.id
  description = "Security group for DBMCP Application Load Balancer"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.common_tags, {
    Name = "dbmcp-${var.environment}-alb"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# User data script for EC2 instance
locals {
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    environment = var.environment
    aws_region  = var.aws_region
  }))
}

# EC2 instance
resource "aws_instance" "dbmcp" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name              = aws_key_pair.ec2_key.key_name
  vpc_security_group_ids = [aws_security_group.ec2.id]
  subnet_id             = tolist(data.aws_subnets.public.ids)[0]
  iam_instance_profile  = aws_iam_instance_profile.ec2_profile.name

  user_data = local.user_data

  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
  }

  tags = merge(local.common_tags, {
    Name = "dbmcp-${var.environment}"
  })

  lifecycle {
    create_before_destroy = false
  }
}

# Application Load Balancer
resource "aws_lb" "dbmcp" {
  name               = "dbmcp-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.public.ids

  enable_deletion_protection = false

  tags = local.common_tags
}

# Target groups
resource "aws_lb_target_group" "fastapi" {
  name     = "dbmcp-${var.environment}-fastapi"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.existing.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/dbmcp/health"
    matcher             = "200"
    port                = "traffic-port"
    protocol            = "HTTP"
  }

  tags = local.common_tags
}

resource "aws_lb_target_group" "mcp" {
  name     = "dbmcp-${var.environment}-mcp"
  port     = 4200
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.existing.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/mcp"
    matcher             = "200,404"  # MCP may return 404 for GET requests
    port                = "traffic-port"
    protocol            = "HTTP"
  }

  tags = local.common_tags
}

# Target group attachments
resource "aws_lb_target_group_attachment" "fastapi" {
  target_group_arn = aws_lb_target_group.fastapi.arn
  target_id        = aws_instance.dbmcp.id
  port             = 8000
}

resource "aws_lb_target_group_attachment" "mcp" {
  target_group_arn = aws_lb_target_group.mcp.arn
  target_id        = aws_instance.dbmcp.id
  port             = 4200
}

# ALB listeners
resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.dbmcp.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.dbmcp.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = data.aws_acm_certificate.opsloom.arn

  # Default action - return 404
  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "text/plain"
      message_body = "Not Found"
      status_code  = "404"
    }
  }
}

# Listener rules for path-based routing
resource "aws_lb_listener_rule" "fastapi" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi.arn
  }

  condition {
    path_pattern {
      values = ["/dbmcp/*"]
    }
  }

  tags = local.common_tags
}

resource "aws_lb_listener_rule" "fastapi_root" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 101

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi.arn
  }

  condition {
    path_pattern {
      values = ["/"]
    }
  }

  tags = local.common_tags
}

resource "aws_lb_listener_rule" "mcp" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mcp.arn
  }

  condition {
    path_pattern {
      values = ["/mcp/*"]
    }
  }

  tags = local.common_tags
}