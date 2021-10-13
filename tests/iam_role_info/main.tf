resource "aws_iam_user" "rebelykos" {
  name = "rebelykos"
}

resource "aws_iam_access_key" "rebelykos" {
  user = aws_iam_user.rebelykos.name
  pgp_key = filebase64(var.pgp_key)
}

resource "aws_iam_user_policy" "rebelykos" {
  name = "rebelykos"
  user = aws_iam_user.rebelykos.name

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "iam:ListRoles",
        "iam:ListAttachedRolePolicies",
        "iam:ListPolicyVersions",
        "iam:GetPolicyVersion",
        "iam:ListRolePolicies",
        "iam:GetRolePolicy"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "inline_policy" {
  statement {
    actions = ["iam:ListUsers"]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "override_inline_policy" {
  override_json = data.aws_iam_policy_document.inline_policy.json
  statement {
    actions = ["iam:ListGroups"]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "inline_policy2" {
  source_json = data.aws_iam_policy_document.override_inline_policy.json
  override_json = data.aws_iam_policy_document.inline_policy.json
}

resource "aws_iam_role" "rebelykos" {
  name = "rebelykos"
  inline_policy {
      name = "rebelykos1"
      policy = data.aws_iam_policy_document.override_inline_policy.json
  }
  inline_policy {
      name = "rebelykos2"
      policy = data.aws_iam_policy_document.inline_policy2.json
  }
  inline_policy {
      name = "rebelykos1"
      policy = data.aws_iam_policy_document.inline_policy2.json
  }
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid = ""
        Principal = {
          "Service": "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "rebelykos" {
  name = "rebelykos"
  role = aws_iam_role.rebelykos.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "sts:GetCallerIdentity"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "rebelykos2" {
  name = "rebelykos2"
  role = aws_iam_role.rebelykos.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "iam:GetUser"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "rebelykos" {
  name = "rebelykos"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "ec2:Describe*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "rebelykos2" {
  name = "rebelykos2"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "iam:ListUsers"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "rebelykos" {
  role = aws_iam_role.rebelykos.name
  policy_arn = aws_iam_policy.rebelykos.arn
}

resource "aws_iam_role_policy_attachment" "rebelykos2" {
  role = aws_iam_role.rebelykos.name
  policy_arn = aws_iam_policy.rebelykos2.arn
}
