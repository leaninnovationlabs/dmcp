-- AWS Cost and Usage Report - Simplified with 10 Key Fields
-- This script creates a streamlined CUR table with the most essential cost analysis fields

-- Drop table if exists
DROP TABLE IF EXISTS aws_cost_usage_report;

-- Create simplified CUR table with 10 key fields
CREATE TABLE aws_cost_usage_report (
    line_item_usage_account_id VARCHAR(20),
    line_item_usage_start_date DATE,
    line_item_product_code VARCHAR(50),
    line_item_usage_type VARCHAR(100),
    line_item_resource_id VARCHAR(200),
    line_item_usage_amount DECIMAL(15,6),
    line_item_unblended_cost DECIMAL(12,6),
    product_region VARCHAR(50),
    product_instance_type VARCHAR(50),
    resource_tags_user_environment VARCHAR(50)
);

-- Insert dummy data covering various AWS services
INSERT INTO aws_cost_usage_report VALUES
('123456789012', '2024-01-01', 'AmazonEC2', 'BoxUsage:t3.medium', 'i-0123456789abcdef0', 24.0, 0.9984, 'us-east-1', 't3.medium', 'production'),
('123456789012', '2024-01-01', 'AmazonEC2', 'BoxUsage:t3.large', 'i-0123456789abcdef1', 24.0, 1.9968, 'us-east-1', 't3.large', 'production'),
('123456789012', '2024-01-01', 'AmazonEC2', 'BoxUsage:t3.small', 'i-0123456789abcdef2', 24.0, 0.5008, 'us-west-2', 't3.small', 'development'),
('123456789012', '2024-01-01', 'AmazonRDS', 'InstanceUsage:db.t3.micro', 'db-ABCDEFGHIJKLMNOP', 24.0, 0.48, 'us-east-1', 'db.t3.micro', 'production'),
('123456789012', '2024-01-01', 'AmazonRDS', 'InstanceUsage:db.t3.small', 'db-QRSTUVWXYZ123456', 24.0, 0.96, 'us-east-1', 'db.t3.small', 'production'),
('123456789012', '2024-01-01', 'AmazonS3', 'TimedStorage-ByteHrs', 'my-production-bucket', 1000.0, 24.58, 'us-east-1', NULL, 'production'),
('123456789012', '2024-01-01', 'AmazonS3', 'TimedStorage-ByteHrs', 'my-dev-bucket', 500.0, 12.29, 'us-west-2', NULL, 'development'),
('123456789012', '2024-01-01', 'AWSLambda', 'Lambda-Duration-GB-Second', 'my-lambda-function', 150.0, 0.25, 'us-east-1', NULL, 'production'),
('123456789012', '2024-01-01', 'AWSLambda', 'Lambda-Requests', 'my-lambda-function', 50.0, 0.10, 'us-east-1', NULL, 'production'),
('123456789012', '2024-01-01', 'AmazonCloudFront', 'DataTransfer-Out-Bytes', 'E1234567890ABC', 100.0, 8.50, 'Global', NULL, 'production'),
('123456789012', '2024-01-01', 'AmazonVPC', 'NatGateway-Hours', 'nat-0123456789abcdef0', 24.0, 1.08, 'us-east-1', NULL, 'production'),
('123456789012', '2024-01-01', 'AmazonVPC', 'NatGateway-Bytes', 'nat-0123456789abcdef0', 10.0, 0.45, 'us-east-1', NULL, 'production'),
('123456789012', '2024-01-01', 'AmazonEC2', 'EBS:VolumeUsage.gp3', 'vol-0123456789abcdef0', 720.0, 7.008, 'us-east-1', NULL, 'production'),
('123456789012', '2024-01-01', 'AmazonEC2', 'EBS:VolumeUsage.gp2', 'vol-0123456789abcdef1', 720.0, 4.00, 'us-west-2', NULL, 'development'),
('123456789012', '2024-01-01', 'AmazonElastiCache', 'NodeUsage:cache.t3.micro', 'my-redis-cluster-001', 24.0, 1.26, 'us-east-1', 'cache.t3.micro', 'production'),
('123456789012', '2024-01-01', 'AmazonSQS', 'Requests-Tier1', 'my-queue', 1000.0, 0.40, 'us-east-1', NULL, 'production'),
('123456789012', '2024-01-01', 'AmazonSNS', 'Requests-Tier1', 'my-topic', 100.0, 0.05, 'us-east-1', NULL, 'production'),
('123456789012', '2024-01-01', 'AmazonCloudWatch', 'MetricMonitorUsage', 'CloudWatchMetrics', 10.0, 3.00, 'us-east-1', NULL, 'production'),
('123456789012', '2024-01-01', 'AmazonRoute53', 'DNS-Queries', 'mydomain.com', 1000.0, 0.40, 'Global', NULL, 'production'),
('123456789012', '2024-01-01', 'AWSELB', 'LoadBalancerUsage', 'app/my-alb/1234567890123456', 24.0, 5.40, 'us-east-1', NULL, 'production'),
('123456789012', '2024-01-01', 'AmazonEC2', 'BoxUsage:t3.micro', 'i-0dev123456789abcd', 8.0, 0.0668, 'us-west-2', 't3.micro', 'development'),
('123456789012', '2024-01-01', 'AmazonRDS', 'InstanceUsage:db.t3.micro', 'db-DEV456789012345', 8.0, 0.16, 'us-west-2', 'db.t3.micro', 'development'),
('123456789012', '2024-01-01', 'AmazonEC2', 'BoxUsage:t3.small', 'i-0stg123456789abcd', 12.0, 0.2504, 'us-east-1', 't3.small', 'staging'),
('123456789012', '2024-01-01', 'AmazonRDS', 'InstanceUsage:db.t3.small', 'db-STG456789012345', 12.0, 0.48, 'us-east-1', 'db.t3.small', 'staging');

-- Create indexes for better query performance
CREATE INDEX idx_account_date ON aws_cost_usage_report(line_item_usage_account_id, line_item_usage_start_date);
CREATE INDEX idx_product_code ON aws_cost_usage_report(line_item_product_code);
CREATE INDEX idx_environment ON aws_cost_usage_report(resource_tags_user_environment);
CREATE INDEX idx_region ON aws_cost_usage_report(product_region);
CREATE INDEX idx_cost ON aws_cost_usage_report(line_item_unblended_cost);

-- Sample queries to analyze the data
-- Total cost by service
SELECT 
    line_item_product_code,
    SUM(line_item_unblended_cost) as total_cost
FROM aws_cost_usage_report 
GROUP BY line_item_product_code 
ORDER BY total_cost DESC;

-- Cost by environment
SELECT 
    resource_tags_user_environment,
    SUM(line_item_unblended_cost) as total_cost
FROM aws_cost_usage_report 
GROUP BY resource_tags_user_environment 
ORDER BY total_cost DESC;

-- Cost by region
SELECT 
    product_region,
    SUM(line_item_unblended_cost) as total_cost
FROM aws_cost_usage_report 
GROUP BY product_region 
ORDER BY total_cost DESC;

-- Top 10 most expensive resources
SELECT 
    line_item_resource_id,
    line_item_product_code,
    product_instance_type,
    SUM(line_item_unblended_cost) as total_cost
FROM aws_cost_usage_report 
GROUP BY line_item_resource_id, line_item_product_code, product_instance_type
ORDER BY total_cost DESC 
LIMIT 10;