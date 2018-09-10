variable "aws_profile" {
  type = "string"
}

variable "aws_region" {
  type = "string"
}

variable "domain_name" {
  default = "status.dev.data.humancellatlas.org"
}

variable "parent_zone_domain_name" {
  default         = "dev.data.humancellatlas.org."
}
