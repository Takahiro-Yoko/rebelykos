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
        "sts:AssumeRole"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role" "rebelykos" {
  name = "rebelykos"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "AWS": "${aws_iam_user.rebelykos.arn}"
      },
      "Effect": "Allow",
      "Sid": ""
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
        "iam:ListRoles"
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
