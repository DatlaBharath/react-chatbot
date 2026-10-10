variable "secret_name" { type = string }

resource "random_password" "mysql_root" {
  length  = 32
  special = false # keeps the generated .env / compose interpolation safe
}

resource "random_password" "mysql_app" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "app" {
  name                    = var.secret_name
  description             = "Runtime secrets rendered into /opt/chatbot/.env at deploy time"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    MYSQL_ROOT_PASSWORD = random_password.mysql_root.result
    MYSQL_PASSWORD      = random_password.mysql_app.result
  })

  # Add/rotate keys in the console or CLI without terraform reverting them.
  lifecycle {
    ignore_changes = [secret_string]
  }
}

output "secret_arn" {
  value = aws_secretsmanager_secret.app.arn
}
