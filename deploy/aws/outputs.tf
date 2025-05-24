output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = aws_ecs_cluster.jamsplitter.name
}

output "ecs_service_name" {
  description = "The name of the ECS service"
  value       = aws_ecs_service.jamsplitter.name
}

output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.jamsplitter.dns_name
}

output "db_endpoint" {
  description = "The connection endpoint for the database"
  value       = aws_db_instance.jamsplitter.endpoint
}

output "db_name" {
  description = "The name of the database"
  value       = aws_db_instance.jamsplitter.name
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = var.ecr_repository_url
}
