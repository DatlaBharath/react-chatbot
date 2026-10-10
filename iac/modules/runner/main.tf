variable "project" { type = string }
variable "instance_type" { type = string }
variable "volume_size_gb" { type = number }
variable "security_group_id" { type = string }
variable "subnet_id" { type = string }
variable "instance_profile_name" { type = string }
variable "github_repo" { type = string } # owner/name
variable "github_pat_ssm_name" { type = string }
variable "runner_labels" { type = string }

# Ubuntu 22.04 (setup-python / setup-node work out of the box on Ubuntu runners)
data "aws_ssm_parameter" "ubuntu_ami" {
  name = "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id"
}

resource "aws_instance" "runner" {
  ami                    = data.aws_ssm_parameter.ubuntu_ami.value
  instance_type          = var.instance_type
  iam_instance_profile   = var.instance_profile_name
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]

  metadata_options {
    http_tokens                 = "required" # IMDSv2 only
    http_put_response_hop_limit = 2          # lets containers reach the instance role if needed
  }

  root_block_device {
    volume_type = "gp3"
    volume_size = var.volume_size_gb
    encrypted   = true
  }

  user_data = templatefile("${path.module}/templates/user_data.sh.tftpl", {
    github_repo         = var.github_repo
    github_pat_ssm_name = var.github_pat_ssm_name
    runner_labels       = var.runner_labels
    runner_name         = "${var.project}-ec2"
  })
  user_data_replace_on_change = true

  tags = { Name = "${var.project}-runner" }
}

output "instance_id" { value = aws_instance.runner.id }
output "public_ip" { value = aws_instance.runner.public_ip }
