module "ecr" {
  source  = "../../modules/ecr"
  project = var.project
}

module "network" {
  source            = "../../modules/network"
  project           = var.project
  app_ingress_cidrs = var.app_ingress_cidrs
}

module "secrets" {
  source      = "../../modules/secrets"
  secret_name = var.app_secret_name
}

module "iam" {
  source              = "../../modules/iam"
  project             = var.project
  ecr_repository_arns = module.ecr.repository_arns
  github_pat_ssm_name = var.github_pat_ssm_name
  app_secret_arn      = module.secrets.secret_arn
}

module "runner" {
  source                = "../../modules/runner"
  project               = var.project
  instance_type         = var.instance_type
  volume_size_gb        = var.volume_size_gb
  security_group_id     = module.network.security_group_id
  instance_profile_name = module.iam.instance_profile_name
  github_repo           = var.github_repo
  github_pat_ssm_name   = var.github_pat_ssm_name
  runner_labels         = var.runner_labels
}
