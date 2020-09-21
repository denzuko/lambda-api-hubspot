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
  }
}

data "archive_file" "init" {
  type        = "zip"
  source_dir = "${path.module}/../src"
  output_path = "${path.module}/files/init.zip"
}
