# Status API

This application returns build and application status badges for services and builds in the
[Human Cell Atlas Data Coordination Platform](https://humancellatlas.org/data-sharing).

* `build` statuses are retrieved from GitLab CI/CD pipelines
* `service` statuses are retrieved from AWS Route53 health checks

## Deployment

1. Create a secret in AWS Secrets Manager with the key `status-api/_/config.json` and the following format.
```json
{
  "domain_name": "...",
  "parent_zone_domain_name": "...",
  "terraform_bucket": "...",
  "aws_region": "..."
}
```
1. Create a secret in AWS Secrets manager with the key `status-api/_/gitlab.json` and the following format.
```json
{
  "gitlab_api_token": "...",
  "gitlab_base_url": "..."
}
```
1. Set you `AWS_PROFILE` environment variable.
1. `make build deploy`

## Endpoints

### `GET /build/{group}/{build}/{branch}`

Returns a status badge from a GitLab build.

### `GET /service/{service_name}`

Returns a status badge from a Route53 health check. `service_name` is, in fact, the name of the health check.

## Security

**Please note**: If you believe you have found a security issue, _please responsibly disclose_ by contacting us at [security-leads@data.humancellatlas.org](mailto:security-leads@data.humancellatlas.org).
