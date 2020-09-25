resource "aws_lambda_function" "lambda_s3" {
  s3_bucket        = aws_s3_bucket.bucket.id
  s3_key           = aws_s3_bucket_object.lambda_code.id
  source_code_hash = data.archive_file.lambda_zip_dir.outputbse64sha256
  runtime          = "python3.6"
  role             = aws_iam_role.iam_for_lambdaiam_for_lambda.arn
  function_name    = "lambda_api_hubspot"
  memory_size      = var.lambda_size
  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.lambda_api_hubspot
  ]
}

resource "aws_sqs_queue" "hubspot_fifo" {
  content_based_deduplication = true
  name                        = "lambda_s3_hubspot-inbound-queue.fifo"
  fifo_queue                  = true
}

resource "aws_api_gateway_rest_api" "hubspot_apigateway" {
  name = "hubspot-apig"
}

resource "aws_api_gateway_resource" "webhook_resource" {
  path_part   = "contacts"
  parrent_id  = aws_api_gateway_rest_api.hubspot_apigateway.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.hubspot_apigateway.id
}
resource "aws_api_gateway_method_settings" "webhook_post_method_settings" {
  rest_api_id = aws_api_gateway_rest_api.hubspot_apigateway.id
  stage_name = aws_api_gateway_stage.deployment.stage_name

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}

resource "aws_api_gateway_integration" "webhook_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.hubspot_apigateway.id
  resource_id = aws_api_gateway_rest_api.hubspot_apigateway.root_resource_id
  http_method = aws_api_gateway_method_settings.webhook_post_method_settings.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  credentials             = aws_iam_role.apig-sqs-send-msg-role.arn

  passthrough_behavior    = "WHEN_NO_TEMPLATES"

  request_parameters = {
    "integration.request.header.Content-Type" = "'application/x-www-form-urlencoded'"
  }

  request_templates = {
    "application/json" = <<EOF
Action=SendMessage&MessageGroupId=1&MessageBody={
    "body": "$input.json('$')",
    "headers": {
      #foreach($header in $input.params().header.keySet())
      "$header": "$util.excapeJavaScript($input.params().header.get($header))" #if($foreach.hasNext),#end
      #end
    },
    "method": "$context.httpMethod",
    "params": {
      #foreach($param in $input.params().path.keySet())
      "$param": "$util.excapeJavaScript($input.params().path.get($param))" #if($foreach.hasNext),#end
      #end
    },
    "query": {
      #foreach($queryParam in $input.params().querystring.keySet())
      "$queryParam": "$util.excapeJavaScript($input.params().querystring.get($queryParam))" #if($foreach.hasNext),#end
      #end
    }
  }
  }
EOF
}

resource "aws_api_gateway_method" "webhook_method_post" {
  path_part   = "contacts"
  rest_api_id = aws_api_gateway_rest_api.hubspot_apigateway.id
  resource_id = aws_api_gateway_resource.webhook_resource

  http_method = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "webhook_method_get" {
  rest_api_id = aws_api_gateway_rest_api.hubspot_apigateway.id
  resource_id = aws_api_gateway_resource.webhook_resource

  http_method = "GET"
  authorization = "NONE"
}

resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  batch_size        = 1
  event_source_arn  = "${aws_sqs_queue.hubspot_fifo.arn}"
  enabled           = true
  function_name     = "${aws_lambda_function.lambda_s3.arn}"
}
