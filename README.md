ShopVerse Lambda Project
A serverless AWS project for the ShopVerse application. It demonstrates
an API Gateway endpoint backed by AWS Lambda and DynamoDB, plus
supporting Lambda functions and AWS services for image processing,
scheduled maintenance, encryption, logging, and asynchronous failure
handling.
Note: This README documents the configuration discussed during the
lab. Verify resource names, routes, and settings in your AWS account
before running commands. Never commit real API keys, AWS credentials,
or other secrets.

Architecture
Client
  |
  | POST /products
  v
Amazon API Gateway (HTTP API)
  |
  v
AWS Lambda: ShopVerseApiIngest
  |
  v
Amazon DynamoDB: ShopVerseProducts

Amazon S3 object events ---> ShopVerseImageThumb Lambda
Amazon EventBridge schedule -> ShopVerseNightlyMaintenance Lambda
Lambda asynchronous failures -> Amazon SQS dead-letter queue (DLQ)

Shared Python code/dependencies -> Lambda Layer: ShopVerseCommonPython
Environment-variable encryption -> AWS KMS customer-managed key
Logs and monitoring -> Amazon CloudWatch
AWS resources
  Resource                Name used in the lab            Purpose
  API Lambda              ShopVerseApiIngest            Receives product
                                                          requests

  Image Lambda            ShopVerseImageThumb           Processes image objects

  Maintenance Lambda      ShopVerseNightlyMaintenance   Runs scheduled
                                                          maintenance

  DynamoDB table          ShopVerseProducts             Stores product records

  Lambda Layer            ShopVerseCommonPython         Shares Python
                                                          code/dependencies

  AWS region              us-east-1                     Region used by the lab

  AWS CLI profile         shopverse                     Local CLI profile used
                                                      in examples
The S3 bucket name, SQS DLQ name, API Gateway ID, and EventBridge
schedule should be confirmed in your AWS account. Do not assume example
names are the names of your deployed resources.
Prerequisites
- AWS CLI installed and configured.
- PowerShell (for the commands below).
- An AWS profile named shopverse with permissions to access the
  resources required by the lab.
- Access to the AWS Lambda, API Gateway, DynamoDB, S3, SQS, IAM, KMS,
  EventBridge, and CloudWatch resources used by your implementation.
Check the active AWS identity:
aws sts get-caller-identity --profile shopverse
Set the region for the current PowerShell session:
$region = "us-east-1"
Test the API
The API endpoint used during the lab was:
https://2ksoqetolc.execute-api.us-east-1.amazonaws.com
Test the POST /products route from PowerShell:
$apiEndpoint = "https://2ksoqetolc.execute-api.us-east-1.amazonaws.com"
$url = "$apiEndpoint/products"

$body = @{
    name  = "Camera Bag"
    price = 39.95
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri $url `
  -Method POST `
  -Headers @{ "x-correlation-id" = "demo-lesson5" } `
  -ContentType "application/json" `
  -Body $body
A successful response depends on the Lambda implementation and API
Gateway configuration. Verify the item in DynamoDB as well.
Verify the API configuration
List API Gateway HTTP APIs and their endpoints:
aws apigatewayv2 get-apis `
  --region us-east-1 `
  --profile shopverse `
  --query "Items[*].[Name,ApiId,ApiEndpoint]" `
  --output table `
  --no-cli-pager
Verify DynamoDB
List the table's items:
aws dynamodb scan `
  --table-name ShopVerseProducts `
  --region us-east-1 `
  --profile shopverse `
  --output table `
  --no-cli-pager
The AWS identity running this command needs dynamodb:Scan. This
permission is separate from the Lambda execution role's permissions.
Verify Lambda configuration
Check the API Lambda's state and KMS key:
aws lambda get-function-configuration `
  --function-name ShopVerseApiIngest `
  --region us-east-1 `
  --profile shopverse `
  --query "{State:State,LastUpdateStatus:LastUpdateStatus,KMSKeyArn:KMSKeyArn}" `
  --output json `
  --no-cli-pager
Check the image Lambda's configured layers:
aws lambda get-function-configuration `
  --function-name ShopVerseImageThumb `
  --region us-east-1 `
  --profile shopverse `
  --query "Layers[*].Arn" `
  --output table `
  --no-cli-pager
Verify S3 buckets
List the buckets available to your AWS identity:
aws s3api list-buckets `
  --profile shopverse `
  --query "Buckets[*].Name" `
  --output table
Set $bucket to the actual bucket name returned by that command before
using it in any S3 command:
$bucket = "REPLACE_WITH_YOUR_ACTUAL_BUCKET_NAME"
KMS encryption
A customer-managed KMS key (CMK) was configured for Lambda
environment-variable encryption. To inspect a known key, use its actual
ARN:
aws kms describe-key `
  --key-id "REPLACE_WITH_YOUR_CMK_ARN" `
  --query "KeyMetadata.{Arn:Arn,Enabled:Enabled,KeyState:KeyState,KeyManager:KeyManager}" `
  --output json `
  --profile shopverse `
  --region us-east-1
The Lambda execution role and KMS key policy must allow the required KMS
operations. Do not put secrets or credentials in this README.
Dead-letter queue (DLQ)
The maintenance Lambda was configured to use an SQS dead-letter queue
for supported asynchronous invocation failures. Confirm the actual queue
URL and ARN in your account before configuring it.

List queues:
aws sqs list-queues `
  --region us-east-1 `
  --profile shopverse `
  --no-cli-pager
The Lambda execution role must have sqs:SendMessage permission for the
configured queue, and the queue must be in a compatible region/account
configuration.
Concurrency
The lab account reported an account concurrency limit of 10 and required
at least 10 unreserved executions. As a result, setting reserved
concurrency on ShopVerseImageThumb to 10 (or even 1) was rejected.
Reserved concurrency requires enough account capacity to preserve the
required unreserved capacity.

Check the current account limits:
aws lambda get-account-settings `
  --region us-east-1 `
  --profile shopverse `
  --query "AccountLimit.[ConcurrentExecutions,UnreservedConcurrentExecutions]" `
  --output table `
  --no-cli-pager
If the educational account cannot increase its quota, document the
limitation and leave reserved concurrency unconfigured unless your lab
instructor provides an approved alternative.
Troubleshooting
  Error                               What to check
  dynamodb:PutItem                  Add least-privilege
  AccessDeniedException             dynamodb:PutItem permission for
                                      the ShopVerseProducts table to
                                      the Lambda execution role.

  KMS AccessDeniedException         Check the Lambda execution role
                                      policy and the KMS key policy.

  --layers invalid JSON or includes Retrieve valid layer-version ARNs
  null                              and pass a valid JSON array; remove
                                      empty values.

  Lambda reserved concurrency error   Check account concurrency limits
                                      and the minimum unreserved capacity
                                      requirement.

  SQS DLQ configuration fails         Confirm the queue ARN exists and
                                      the role has sqs:SendMessage.

  API returns HTTP 500                Inspect the relevant Lambda's
                                      CloudWatch logs for the underlying
                                      error.

  API returns HTTP 404                Verify the API endpoint, stage,
                                  route, HTTP method, and deployment.
Security notes
- Do not commit AWS access keys, secret keys, third-party API keys, or
  real credentials.
- Replace placeholder values such as change_me before using an
  external API.
- Prefer least-privilege IAM permissions scoped to the specific
  resources required.
- Avoid putting account-specific ARNs in public documentation unless
  necessary.
- Review AWS charges and account quotas before creating KMS keys or
  other billable resources.
Status checklist
Use this checklist to track completion in your own account:
- [ ] ShopVerseApiIngest exists and is active.
- [ ] API Gateway has a deployed POST /products route integrated
  with the API Lambda.
- [ ] A test request succeeds and the product is present in
  ShopVerseProducts.
- [ ] ShopVerseImageThumb is configured with the required S3 trigger
  and layer.
- [ ] ShopVerseNightlyMaintenance is configured with the required
  EventBridge schedule.
- [ ] The KMS key and Lambda environment-variable encryption are
  verified.
- [ ] CloudWatch log retention and monitoring are configured as
  required by the lab.
- [ ] The SQS DLQ is configured and permissions are verified.
- [ ] Concurrency settings are documented according to the account's
  quota.
Project: ShopVerse Lambda
Region: us-east-1
CLI profile used in examples: shopverse