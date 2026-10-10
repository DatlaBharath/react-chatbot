variable "project" { type = string }
variable "app_ingress_cidrs" { type = list(string) }

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "runner" {
  name        = "${var.project}-runner"
  description = "App ports for ${var.project}; no SSH (use SSM)"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "frontend"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.app_ingress_cidrs
  }

  ingress {
    description = "backend"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = var.app_ingress_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "subnet_id" {
  value = sort(data.aws_subnets.default.ids)[0]
}

output "security_group_id" {
  value = aws_security_group.runner.id
}
