# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name = "status-api"
}

# /availability/{service_name}
resource "aws_api_gateway_resource" "availability" {
  path_part = "availability"
  parent_id = "${aws_api_gateway_rest_api.api.root_resource_id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_resource" "availability_service_name" {
  path_part = "{service_name}"
  parent_id = "${aws_api_gateway_resource.availability.id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_method" "availability_method" {
  rest_api_id   = "${aws_api_gateway_rest_api.api.id}"
  resource_id   = "${aws_api_gateway_resource.availability_service_name.id}"
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "availability_integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.api.id}"
  resource_id             = "${aws_api_gateway_resource.availability_service_name.id}"
  http_method             = "${aws_api_gateway_method.availability_method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.lambda.arn}/invocations"
}

# /service/{service_name}
resource "aws_api_gateway_resource" "service" {
  path_part = "service"
  parent_id = "${aws_api_gateway_rest_api.api.root_resource_id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_resource" "service_name" {
  path_part = "{service_name}"
  parent_id = "${aws_api_gateway_resource.service.id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_method" "service_method" {
  rest_api_id   = "${aws_api_gateway_rest_api.api.id}"
  resource_id   = "${aws_api_gateway_resource.service_name.id}"
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "service_integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.api.id}"
  resource_id             = "${aws_api_gateway_resource.service_name.id}"
  http_method             = "${aws_api_gateway_method.service_method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.lambda.arn}/invocations"
}

# /build/{build_name}
resource "aws_api_gateway_resource" "build" {
  path_part = "build"
  parent_id = "${aws_api_gateway_rest_api.api.root_resource_id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_resource" "group_param" {
  path_part = "{group}"
  parent_id = "${aws_api_gateway_resource.build.id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_resource" "build_param" {
  path_part = "{build}"
  parent_id = "${aws_api_gateway_resource.group_param.id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_resource" "branch_param" {
  path_part = "{branch}"
  parent_id = "${aws_api_gateway_resource.build_param.id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_method" "branch_method" {
  rest_api_id   = "${aws_api_gateway_rest_api.api.id}"
  resource_id   = "${aws_api_gateway_resource.branch_param.id}"
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "build_integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.api.id}"
  resource_id             = "${aws_api_gateway_resource.branch_param.id}"
  http_method             = "${aws_api_gateway_method.branch_method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.lambda.arn}/invocations"
}

# Lambda
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda.arn}"
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/GET*"
}

resource "aws_lambda_function" "lambda" {
  filename         = "lambda.zip"
  function_name    = "status-api"
  role             = "${aws_iam_role.status_api.arn}"
  handler          = "app.app"
  runtime          = "python3.6"
  memory_size      = "128"
  source_code_hash = "${base64sha256(file("./lambda.zip"))}"
  timeout = 5
  environment {
    variables {
      SERVER_NAME = "status-api"
    }
  }
}

# IAM
resource "aws_iam_role" "status_api" {
  name = "status-api"

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

resource "aws_iam_policy" "status_api" {
  name = "status-api-extras"
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
            "Resource": "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/status-api:*"
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
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:BatchGetItem"
            ],
            "Resource": "${aws_dynamodb_table.statuses.arn}"
        }
    ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "status-api" {
  policy_arn = "${aws_iam_policy.status_api.arn}"
  role = "${aws_iam_role.status_api.name}"
}

resource "aws_api_gateway_deployment" "status_api" {
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  stage_name  = "dev"
}


// DNS
data "aws_route53_zone" "primary" {
  name         = "${var.parent_zone_domain_name}."
  private_zone = false
}

resource "aws_acm_certificate" "cert" {
  domain_name = "${var.domain_name}"
  validation_method = "DNS"
}

resource "aws_route53_record" "cert_validation" {
  name = "${aws_acm_certificate.cert.domain_validation_options.0.resource_record_name}"
  type = "${aws_acm_certificate.cert.domain_validation_options.0.resource_record_type}"
  zone_id = "${data.aws_route53_zone.primary.id}"
  records = ["${aws_acm_certificate.cert.domain_validation_options.0.resource_record_value}"]
  ttl = 60
}

resource "aws_acm_certificate_validation" "cert" {
  certificate_arn = "${aws_acm_certificate.cert.arn}"
  validation_record_fqdns = ["${aws_route53_record.cert_validation.fqdn}"]
}

resource "aws_api_gateway_domain_name" "status_api" {
  domain_name = "${var.domain_name}"

  certificate_arn = "${aws_acm_certificate.cert.arn}"
}

resource "aws_route53_record" "status" {
  zone_id = "${data.aws_route53_zone.primary.id}" # See aws_route53_zone for how to create this

  name = "${var.domain_name}"
  type = "A"

  alias {
    name                   = "${aws_api_gateway_domain_name.status_api.cloudfront_domain_name}"
    zone_id                = "${aws_api_gateway_domain_name.status_api.cloudfront_zone_id}"
    evaluate_target_health = false
  }
}

resource "aws_api_gateway_base_path_mapping" "status_api" {
  api_id      = "${aws_api_gateway_rest_api.api.id}"
  stage_name  = "${aws_api_gateway_deployment.status_api.stage_name}"
  domain_name = "${aws_api_gateway_domain_name.status_api.domain_name}"
}
