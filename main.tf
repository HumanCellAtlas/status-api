provider "aws" {
  region  = "${var.aws_region}"
  profile = "${var.aws_profile}"
}

terraform {
  backend "s3" {
    key = "status-api/terraform.tfstate"
  }
}

data "aws_caller_identity" "current" {}

resource "aws_dynamodb_table" "statuses" {
  name           = "application_statuses"
  read_capacity  = 2
  write_capacity = 2
  hash_key       = "service_name"

  attribute {
    name = "service_name"
    type = "S"
  }

  ttl {
    attribute_name = "time_to_exist"
    enabled = true
  }

  tags {
    Name = "application_statuses"
  }
}

