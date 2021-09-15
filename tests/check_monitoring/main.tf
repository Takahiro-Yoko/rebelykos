resource "aws_iam_user" "rebelykos" {
  name = "rebelykos"
}

resource "aws_iam_access_key" "rebelykos" {
  user = aws_iam_user.rebelykos.name
  pgp_key = filebase64(var.pgp_key)
}

resource "aws_iam_user_policy" "rebelykos_ro" {
  name = "rebelykos"
  user = aws_iam_user.rebelykos.name

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "cloudtrail:DescribeTrails",
        "guardduty:ListDetectors",
        "access-analyzer:ListAnalyzers"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

data "aws_caller_identity" "current" {}

resource "aws_cloudtrail" "rebelykos" {
  name                          = "rebelykos"
  s3_bucket_name                = aws_s3_bucket.rebelykos.id
  s3_key_prefix                 = "prefix"
  include_global_service_events = true
}

resource "aws_s3_bucket" "rebelykos" {
  bucket        = "rebelykos"
  force_destroy = true

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::rebelykos"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::rebelykos/prefix/AWSLogs/${data.aws_caller_identity.current.account_id}/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}
POLICY
}

resource "aws_accessanalyzer_analyzer" "rebelykos" {
  analyzer_name = "rebelykos"
}

output "key" {
  value = aws_iam_access_key.rebelykos.id
}
output "secret" {
  value = aws_iam_access_key.rebelykos.encrypted_secret
}
