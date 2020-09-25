resource "aws_cloudwatch_log_group" "lambda_api_hubspot" {
  name              = "/aws/lambda/${aws_lambda_function.lambda_s3.function_name}"
  retention_in_days = vars.log_retention
}
