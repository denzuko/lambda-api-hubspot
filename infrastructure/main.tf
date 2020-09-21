resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


resource "aws_iam_policy" "lambda_logging" {
  name = "lambda_logging"
  path = "/"
  description = "IAM policy for logging from a lambda function"
  policy = <<EOL
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_cloudwatch_log_group" "lambda-api-hubspot" {
  name = "/aws/lambda/${aws_lambda_function.lambda_s3.function_name}"
  retention_in_days = 28
}

resource "aws_s3_bucket" "bucket" {
  force_destroy = true
  tags = "${local.common_tags}"
}

resource "aws_s3_bucket_object" "lambda_code" {
  key	= "${random_id.id.hex}-object"
  bucket	= aws_s3_bucket.bucket.id
  source	= data.archive_file.lambda_zip_dir.output_path
  etag	= data.archive_file.lambda_zip_dir.output_base64sha256
  tags = "${local.common_tags}"
}

resource "aws_lambda_function" "lambda_s3" {
  s3_bucket	= aws_s3_bucket.bucket.id
  s3_key		= aws_s3_bucket_object.lambda_code.id
  source_code_hash = "${data.archive_file.lambda_zip_dir.outputbse64sha256}"
  tags = "${local.common_tags}"
  runtime = "python3.6"
  role = aws_iam_role.iam_for_lambdaiam_for_lambda.arn
  function_name="lambda-api-hubspot"
  memory_size: 256
  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs
    aws_cloudwatch_log_group.lambda-api-hubspot
  ]
}

resource "aws_rds_cluster" "default" {
  cluster_identifier = "example-cluster-demo"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  database_name = "contacts"
  engine = "aurora-mysql5.7"
  engine_version = "5.7.12"
  master_username = "zaphod"
  master_password = "breeblebox42"
  backup_retention_period = 1
  preferred_backup_window = "07:00-09:00"
  skip_final_snapshot = true
}
