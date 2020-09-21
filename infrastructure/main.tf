resource "aws_cloudwatch_log_group" "lambda-api-hubspot" {
	name = "lambda-api-hubspot"
	retention_in_days = "90"
	tags = {
		Environment = "production"
		Application = "lambda-api-hubspot"
		Owner = "dwightaspencer@gmail.com"
	}
}
