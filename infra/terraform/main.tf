terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = local.common_tags
  }
}



# ECR Module
module "ecr" {
  source = "./modules/ecr"
  
  repository_name = local.ecr_repository_name
  environment     = local.config.environment
  common_tags     = local.common_tags
}

# RDS Test Module (conditional)
module "rds_test" {
  count  = try(local.config.rds_test.enabled, false) ? 1 : 0
  source = "./modules/rds-test"
  
  environment         = local.config.environment
  vpc_id              = local.config.rds_test.vpc_id
  subnet_ids          = local.config.rds_test.subnet_ids
  database_name       = local.config.rds_test.database_name
  database_username   = local.config.rds_test.database_username
  publicly_accessible = local.config.rds_test.publicly_accessible
}

# EC2 Simple Module (replaces EKS)
module "ec2_simple" {
  source = "./modules/ec2-simple"
  
  environment   = local.config.environment
  aws_region    = local.config.region
  instance_type = local.config.ec2.instance_type
  domain_name   = local.config.ec2.domain_name
}

# Route 53 DNS Configuration
data "aws_route53_zone" "opsloom" {
  name         = "opsloom.io"
  private_zone = false
}

resource "aws_route53_record" "dbmcp" {
  zone_id = data.aws_route53_zone.opsloom.zone_id
  name    = local.config.ec2.domain_name
  type    = "A"

  alias {
    name                   = module.ec2_simple.load_balancer_dns
    zone_id                = module.ec2_simple.load_balancer_zone_id
    evaluate_target_health = true
  }
}

# Aurora Serverless v2 Module
module "aurora" {
  source = "./modules/aurora"
  
  cluster_name     = local.database_cluster_name
  environment      = local.config.environment
  engine_version   = local.database_engine_version
  max_capacity     = local.database_max_capacity
  common_tags      = local.common_tags
}

 