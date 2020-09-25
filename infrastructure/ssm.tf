resource "aws_secretsmanager_secret" "lambda_s3" {
  name                = "rotation-example"
  rotation_lambda_arn = aws_lambda_function.lambda_s3.arn

  rotation_rules {
    automatically_after_days = 7
  }
}
