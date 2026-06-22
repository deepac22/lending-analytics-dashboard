terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Create a security group for RDS
resource "aws_security_group" "rds_sg" {
  name        = "lending_rds_sg"
  description = "Allow PostgreSQL access"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lending-rds-sg"
  }
}

# Create the PostgreSQL RDS instance (Free Tier)
resource "aws_db_instance" "lending_db" {
  identifier     = "lending-analytics-db"
  engine         = "postgres"
  engine_version = "16.3"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  storage_type   = "gp2"

  db_name  = "lendingdb"
  username = "lending_admin"
  password = "LendingSecurePass123!"

  port = 5432

  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  publicly_accessible = true
  skip_final_snapshot = true

  tags = {
    Name        = "lending-analytics-db"
    Environment = "demo"
    Project     = "lending-analytics"
  }
}

output "db_endpoint" {
  value = aws_db_instance.lending_db.endpoint
  description = "The endpoint URL for the PostgreSQL database"
}

output "db_name" {
  value = aws_db_instance.lending_db.db_name
  description = "The database name"
}

output "db_username" {
  value = aws_db_instance.lending_db.username
  description = "The database username"
  sensitive = true
}