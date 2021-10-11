resource "null_resource" "iam-user-policy-version-2" {
  provisioner "local-exec" {
    command = "aws iam create-policy-version --policy-arn ${aws_iam_policy.rebelykos.arn} --policy-document file://policies/v2.json --no-set-as-default --profile ${var.profile} --region ${var.region}"
  }
}
