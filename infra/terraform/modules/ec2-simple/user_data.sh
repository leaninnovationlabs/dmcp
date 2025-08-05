#!/bin/bash
set -e

# EC2 User Data Script for DBMCP
# This script sets up Docker, AWS CLI, and prepares the instance for Ansible management

# Variables from Terraform
ENVIRONMENT="${environment}"
AWS_REGION="${aws_region}"

# Log everything
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Starting DBMCP EC2 setup for environment: $ENVIRONMENT"

# Update system
dnf update -y

# Install Docker
dnf install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose v2 plugin
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
mkdir -p /usr/local/lib/docker/cli-plugins
curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Also install standalone for compatibility
curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install AWS CLI v2 (pre-installed on AL2023, but ensure it's available)
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    dnf install -y unzip
    unzip awscliv2.zip
    ./aws/install
    rm -rf aws awscliv2.zip
fi

# Configure AWS CLI with region
aws configure set region $AWS_REGION

# Install Python3 and pip (for Ansible) - Python 3.11+ is default on AL2023
dnf install -y python3 python3-pip

# Create application directory
mkdir -p /opt/dbmcp
chown ec2-user:ec2-user /opt/dbmcp

# Create a systemd service for health check endpoint
cat > /etc/systemd/system/dbmcp-health.service << 'EOF'
[Unit]
Description=DBMCP Health Check Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/dbmcp
ExecStart=/usr/bin/python3 -m http.server 8080 --bind 0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Create a simple health check HTML file
mkdir -p /opt/dbmcp/health
cat > /opt/dbmcp/health/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>DBMCP Health Check</title>
</head>
<body>
    <h1>DBMCP Server is Ready</h1>
    <p>Instance is configured and ready for Ansible deployment.</p>
</body>
</html>
EOF

chown -R ec2-user:ec2-user /opt/dbmcp

# Enable and start the health service
systemctl enable dbmcp-health
systemctl start dbmcp-health

# Install git (for potential code deployment)
dnf install -y git

# Create a marker file to indicate setup completion
echo "$(date): DBMCP EC2 setup completed successfully" > /opt/dbmcp/setup-complete.txt
chown ec2-user:ec2-user /opt/dbmcp/setup-complete.txt

# Install and start SSM agent (pre-installed on Amazon Linux 2023)
dnf install -y amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

# Install CloudWatch agent (optional, for monitoring)
dnf install -y amazon-cloudwatch-agent

# Create log directories
mkdir -p /var/log/dbmcp
chown ec2-user:ec2-user /var/log/dbmcp

# Create deployment script for SSM execution
cat > /opt/dbmcp/deploy.sh << 'DEPLOY_EOF'
#!/bin/bash
set -e

# DBMCP Container Deployment Script
# This script deploys FastAPI and MCP containers

echo "Starting DBMCP container deployment..."

# Variables
ENVIRONMENT="${environment}"
AWS_REGION="${aws_region}"
ECR_REGISTRY="767397957512.dkr.ecr.${aws_region}.amazonaws.com"
FASTAPI_IMAGE="$${ECR_REGISTRY}/dbmcp-fastapi:latest"
MCP_IMAGE="$${ECR_REGISTRY}/dbmcp-mcp:latest"

# Login to ECR
aws ecr get-login-password --region $${AWS_REGION} | \
    docker login --username AWS --password-stdin $${ECR_REGISTRY}

# Create Docker Compose file
cat > /opt/dbmcp/docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  fastapi:
    image: 767397957512.dkr.ecr.us-east-1.amazonaws.com/dbmcp-fastapi:latest
    container_name: dbmcp-fastapi
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=${environment}
      - DATABASE_URL_PARAMETER=/${environment}/dbmcp/database_url
      - USE_PARAMETER_STORE=true
      - JWT_SECRET_PARAMETER=/${environment}/dbmcp/jwt_secret
      - AWS_DEFAULT_REGION=${aws_region}
      - LOG_LEVEL=info
      - CORS_ALLOWED_ORIGINS=https://dbmcp.opsloom.io
    volumes:
      - /var/log/dbmcp/fastapi:/app/logs
    networks:
      - dbmcp-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/dbmcp/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  mcp:
    image: 767397957512.dkr.ecr.us-east-1.amazonaws.com/dbmcp-mcp:latest
    container_name: dbmcp-mcp
    restart: unless-stopped
    ports:
      - "4200:4200"
    environment:
      - ENVIRONMENT=${environment}
      - DATABASE_URL_PARAMETER=/${environment}/dbmcp/database_url
      - USE_PARAMETER_STORE=true
      - JWT_SECRET_PARAMETER=/${environment}/dbmcp/jwt_secret
      - AWS_DEFAULT_REGION=${aws_region}
      - LOG_LEVEL=info
      - TRANSPORT=http
    volumes:
      - /var/log/dbmcp/mcp:/app/logs
    networks:
      - dbmcp-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4200/dbmcp/mcp"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  dbmcp-network:
    driver: bridge
COMPOSE_EOF

# Pull and start containers
echo "Pulling latest container images..."
docker compose -f /opt/dbmcp/docker-compose.yml pull

echo "Starting DBMCP services..."
docker compose -f /opt/dbmcp/docker-compose.yml up -d

echo "Waiting for services to be ready..."
sleep 30

echo "Checking service status..."
docker compose -f /opt/dbmcp/docker-compose.yml ps

echo "DBMCP deployment completed successfully!"
DEPLOY_EOF

chmod +x /opt/dbmcp/deploy.sh
chown ec2-user:ec2-user /opt/dbmcp/deploy.sh

echo "DBMCP EC2 setup completed successfully"