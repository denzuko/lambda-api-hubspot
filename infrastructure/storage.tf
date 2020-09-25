resource "aws_s3_bucket" "bucket" {
  force_destroy = true
}

resource "aws_s3_bucket_object" "lambda_code" {
  key    = "${random_id.id.hex}-object"
  bucket = aws_s3_bucket.bucket.id
  source = data.archive_file.lambda_zip_dir.output_path
  etag   = data.archive_file.lambda_zip_dir.output_base64sha256
}
