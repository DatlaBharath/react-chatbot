output "instance_id" {
  value = module.runner.instance_id
}

output "app_url" {
  value = "http://${module.runner.public_ip}"
}

output "app_secret_arn" {
  value = module.secrets.secret_arn
}

output "ecr_repository_urls" {
  value = module.ecr.repository_urls
}
