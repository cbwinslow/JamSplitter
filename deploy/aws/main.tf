provider "aws" {
  region = var.aws_region
}

resource "aws_ecs_cluster" "jamsplitter" {
  name = "jamsplitter-${var.environment}"
}

resource "aws_ecs_task_definition" "jamsplitter" {
  family                   = "jamsplitter-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  
  container_definitions = jsonencode([
    {
      name      = "jamsplitter"
      image     = "${var.ecr_repository_url}:${var.image_tag}"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "JAMSPLITTER_ENV"
          value = var.environment
        },
        {
          name  = "JAMSPLITTER_DATABASE_URL"
          value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.jamsplitter.endpoint}/${var.db_name}"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/jamsplitter-${var.environment}"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "jamsplitter" {
  name            = "jamsplitter-${var.environment}"
  cluster         = aws_ecs_cluster.jamsplitter.id
  task_definition = aws_ecs_task_definition.jamsplitter.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = var.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.jamsplitter.arn
    container_name   = "jamsplitter"
    container_port   = 8000
  }
  
  depends_on = [aws_lb_listener.jamsplitter]
}

# Add other necessary resources like RDS, ElastiCache, IAM roles, etc.
