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
  name        = "lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda function"
  policy      = data.aws_iam_policy_document.lambda_exec_role_policy
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role" "apig-sqs-send-msg-role" {
  name = "${var.app_name}-apig-sqs-send-msg-role"

  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [{
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Effect": "Allow"
    }]
  }
EOF
}

resource "aws_iam_policy" "apig-sqs-send-msg-policy" {
  name = "${var.app_name}-apig-sqs-send-msg-policy"

  policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Resource": [ "*" ],
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
      ]
    }, {
      "Effect": "Allow",
      "Action": "sqs:SendMessage",
      "Resource": aws_sqs_queue.hubspot_fifo.arn
    }]
  }
EOF
}

resource "aws_iam_role_policy_attachment" "terraform_apig_sqs_policy_attach" {
  role   = aws_iam_role.apig-sqs-send-mesg-role.id
  policy = aws_iam_role.apig-sqs-send-mesg-role.arn
}
