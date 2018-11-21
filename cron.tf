# Lambda
resource "aws_lambda_function" "status_cron" {
  filename         = "lambda.zip"
  function_name    = "status-cron"
  role             = "${aws_iam_role.status_cron.arn}"
  handler          = "cron.handler"
  runtime          = "python3.6"
  memory_size      = "128"
  source_code_hash = "${base64sha256(file("./lambda.zip"))}"
  timeout = 300
}

resource "aws_cloudwatch_event_rule" "status_cron" {
  name = "status-cron"
  description = "Update statuses of services on s3"
  schedule_expression = "rate(2 minutes)"
}

resource "aws_lambda_permission" "status_cron" {
  statement_id = "AllowExecutionFromCloudWatch"
  principal = "events.amazonaws.com"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.status_cron.function_name}"
  source_arn = "${aws_cloudwatch_event_rule.status_cron.arn}"
  depends_on = [
    "aws_lambda_function.status_cron"
  ]
}

resource "aws_cloudwatch_event_target" "status_cron" {
  target_id = "invoke-status-cron"
  rule      = "${aws_cloudwatch_event_rule.status_cron.name}"
  arn       = "${aws_lambda_function.status_cron.arn}"
}


# IAM
resource "aws_iam_role" "status_cron" {
  name = "status-cron"

  assume_role_policy = <<POLICY
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
POLICY
}

resource "aws_iam_policy" "status_cron" {
  name = "status-cron-extras"
  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:CreateLogGroup"
            ],
            "Resource": "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/status-cron:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "route53:ListHealthChecks",
                "route53:ListTagsForResources",
                "route53:GetHealthCheckStatus"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:DescribeSecret",
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:status-api/*"
        },
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:UpdateItem"
            ],
            "Resource": "${aws_dynamodb_table.statuses.arn}"
        },
        {
            "Effect": "Allow",
            "Action": "cloudwatch:GetMetricData",
            "Resource": "*"
        }
    ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "status_cron" {
  policy_arn = "${aws_iam_policy.status_cron.arn}"
  role = "${aws_iam_role.status_cron.name}"
}

