variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "app_secret_name" {
  description = "Secrets Manager secret holding runtime secrets (JSON key/values become .env entries)"
  type        = string
  default     = "chatbot/prod/app"
}

variable "project" {
  type    = string
  default = "chatbot"
}

variable "github_repo" {
  description = "owner/name of the GitHub repository the runner serves"
  type        = string
}

variable "github_pat_ssm_name" {
  description = "SSM SecureString holding a PAT able to create runner registration tokens (create it manually; keeps it out of tf state)"
  type        = string
  default     = "/chatbot/github-runner-pat"
}

variable "instance_type" {
  type    = string
  default = "t2.xlarge"
}

variable "volume_size_gb" {
  type    = number
  default = 60
}

variable "app_ingress_cidrs" {
  description = "Who can reach ports 80 and 8000"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "runner_labels" {
  type    = string
  default = "ec2-deploy"
}
