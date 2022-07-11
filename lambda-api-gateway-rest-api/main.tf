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
  bucket = "lambda-source-code-carro-1"
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


resource "aws_api_gateway_rest_api" "rest_api"{
    name        = "acoustic-apigateway-carro"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "rest_api_resource" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id = aws_api_gateway_rest_api.rest_api.root_resource_id
  path_part = "produce_10s"
}

resource "aws_api_gateway_method" "rest_api_get_method"{
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.rest_api_resource.id
  http_method = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "rest_api_get_method_integration" {
  rest_api_id             = aws_api_gateway_rest_api.rest_api.id
  resource_id             = aws_api_gateway_resource.rest_api_resource.id
  http_method             = aws_api_gateway_method.rest_api_get_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.produce_10s.invoke_arn
}

resource "aws_api_gateway_deployment" "rest_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.rest_api_resource.id,
      aws_api_gateway_method.rest_api_get_method.id,
      aws_api_gateway_integration.rest_api_get_method_integration.id
    ]))
  }
}
resource "aws_api_gateway_stage" "rest_api_stage" {
  deployment_id = aws_api_gateway_deployment.rest_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  stage_name    = "STG"
}

resource "aws_api_gateway_method_settings" "example" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  stage_name  = aws_api_gateway_stage.rest_api_stage.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}

resource "aws_lambda_permission" "apigw" {
   #statement_id  = "AllowAPIGatewayInvoke"
   statement_id = "AllowExecutionFromAPIGateway"
   action        = "lambda:InvokeFunction"
   function_name = aws_lambda_function.produce_10s.function_name
   principal     = "apigateway.amazonaws.com"
   source_arn = "${aws_api_gateway_rest_api.rest_api.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "produce_10s_api_gw" {
  name = "/aws/produce_10s_api_gw/${aws_api_gateway_rest_api.rest_api.name}"

  retention_in_days = 30
}

output "function_name_v1" {
  description = "ARN."
  value = aws_api_gateway_rest_api.rest_api.execution_arn
}
