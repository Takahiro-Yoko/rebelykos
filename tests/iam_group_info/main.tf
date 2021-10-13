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
        "iam:ListPolicyVersions",
        "iam:GetPolicyVersion",
        "iam:ListGroups"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_group" "rebelykos" {
  name = "rebelykos"
}

resource "aws_iam_group_membership" "rebelykos" {
  name = "rebelykos"
  users = [
    aws_iam_user.rebelykos.name
  ]
  group = aws_iam_group.rebelykos.name
}

resource "aws_iam_group_policy" "rebelykos" {
  name = "rebelykos"
  group = aws_iam_group.rebelykos.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sts:GetCallerIdentity"
        ]
        Effect = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_policy" "rebelykos" {
  name = "rebelykos"
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

resource "aws_iam_group_policy_attachment" "rebelykos" {
  group = aws_iam_group.rebelykos.name
  policy_arn = aws_iam_policy.rebelykos.arn
}
