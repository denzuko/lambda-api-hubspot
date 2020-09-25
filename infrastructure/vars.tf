variable "cluster_name" {
  default = "rds-lambda-cluster"
}

variable "database_name" {
  default = "contacts"
}

variable "app_name" {
  default = "lambda_s3_hubspot"
}

variable "instance_class" {
  default = "db.t2.small"
}

varaible "lambda_size" {
  default = 256
}

variable "username" {
  default = data.aws_kms_secrets.lambda_s3.plaintext["master_username"]
}

variable "password" {
  default = data.aws_kms_secrets.lambda_s3.plaintext["master_password"]
}
variable "log_retion" {
  default = 28
}
