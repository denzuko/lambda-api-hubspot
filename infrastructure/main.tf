resource "aws_cloudwatch_log_group" "lambda-api-hubspot" {
  name = "lambda-api-hubspot"
  retention_in_days = "90"
  tags = "${local.common_tags}"
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
}
