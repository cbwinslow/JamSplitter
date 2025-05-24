variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "ecr_repository_url" {
  description = "The URL of the ECR repository"
  type        = string
}

variable "image_tag" {
  description = "The Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "db_username" {
  description = "The username for the database"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "The password for the database"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "The name of the database"
  type        = string
  default     = "jamsplitter"
}

variable "desired_count" {
  description = "The number of ECS tasks to run"
  type        = number
  default     = 1
}

variable "private_subnets" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
