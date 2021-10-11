resource "aws_iam_user" "rebelykos" {
  name = "rebelykos"
}

resource "aws_iam_access_key" "rebelykos" {
  user = aws_iam_user.rebelykos.name
  pgp_key = filebase64(var.pgp_key)
}

resource "aws_iam_policy" "rebelykos" {
  name = "rebelykos"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "iam:GetUserPolicy"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "rebelykos" {
  name = "rebelykos"
  users = [aws_iam_user.rebelykos.name]
  policy_arn = aws_iam_policy.rebelykos.arn
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
        "iam:ListAttachedUserPolicies",
        "iam:ListPolicyVersions",
        "iam:GetPolicyVersion",
        "iam:ListUserPolicies"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_user_policy" "rebelykos2" {
  name = "rebelykos2"
  user = aws_iam_user.rebelykos.name

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
