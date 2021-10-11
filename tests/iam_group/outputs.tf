output "key" {
  value = aws_iam_access_key.rebelykos.id
}

output "secret" {
  value = aws_iam_access_key.rebelykos.encrypted_secret
}

