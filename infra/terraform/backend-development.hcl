bucket         = "opsloom-terraform-state-bucket"
key            = "dbmcp/development/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "terraform-state-lock"
encrypt        = true