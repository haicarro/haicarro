terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2.0"
    }
  }

  required_version = "~> 1.0"
}

provider "aws" {
  region = var.aws_region
}

# create a bucket on S3
resource "aws_s3_bucket" "bucket_lambda" {
  bucket = "lambda-source-code-carro"
}

# Generate an archive from content, a file or directory of files
data "archive_file" "compress_source_code" {
  type = "zip"
  source_dir  = "${path.module}/produce-10s"
  output_path = "${path.module}/produce_10s.zip"
}

# Uploading a file to a bucket
resource "aws_s3_object" "produce_10s_source_code" {
  bucket = aws_s3_bucket.bucket_lambda.id
  key = "produce_10s.zip"
  source = data.archive_file.compress_source_code.output_path
  etag = filemd5(data.archive_file.compress_source_code.output_path)
}

# Deploy lambda 
resource "aws_lambda_function" "produce_10s" {
  function_name = "produce-10s"
  s3_bucket = aws_s3_bucket.bucket_lambda.id
  s3_key = aws_s3_object.produce_10s_source_code.key
  runtime = "python3.8"
  handler = "produce_10s.lambda_handler"
  timeout = 300
  memory_size = 128
  role = aws_iam_role.lambda_exec.arn
}

# define cloudwatch group for this lambda
resource "aws_cloudwatch_log_group" "produce_10s_cloudwatch_group" {
  name = "/aws/lambda/${aws_lambda_function.produce_10s.function_name}"
  retention_in_days = 30
}

# Define role and attach to this lambda 
resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_apigatewayv2_api" "produce_10s_apigateway" {
  name          = "produce_10s_apigateway"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "produce_10s_stage" {
  api_id = aws_apigatewayv2_api.produce_10s_apigateway.id

  name        = "STG"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.produce_10s_api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "produce_10s" {
  api_id = aws_apigatewayv2_api.produce_10s_apigateway.id

  integration_uri    = aws_lambda_function.produce_10s.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "produce_10s" {
  api_id = aws_apigatewayv2_api.produce_10s_apigateway.id

  route_key = "GET /hello"
  target    = "integrations/${aws_apigatewayv2_integration.produce_10s.id}"
}

resource "aws_cloudwatch_log_group" "produce_10s_api_gw" {
  name = "/aws/produce_10s_api_gw/${aws_apigatewayv2_api.produce_10s_apigateway.name}"

  retention_in_days = 30
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.produce_10s.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.produce_10s_apigateway.execution_arn}/*/*"
}
