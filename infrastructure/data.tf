data "aws_iam_policy_document" "lambda_exec_role_policy" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:*:*:*"
    ]
    effect = "Allow"
  }
}

data "archive_file" "init" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/files/init.zip"
}

data "aws_secretmanager_secret_version" "master_user" {
  secret_id = "MYSQL_USER"
}

data "aws_secretmanager_secret_version" "master_password" {
  secret_id = "MYSQL_PASSWORD"
}

data "aws_caller_identiy" "current" {}
