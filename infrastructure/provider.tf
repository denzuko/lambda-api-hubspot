provider "aws" {
  version = "~> 3.0"
  region  = "us-east-1"
  default_tags = {
    Environment = "production",
    Application = "lambda-api-hubspot",
    Owner       = "dwightaspencer@gmail.com"
  }
}
