terraform {
  backend "s3" {
    # These values must be provided via backend config during init or via -backend-config flags
    # Example: terraform init -backend-config="key=dev/terraform.tfstate" -backend-config="bucket=<app-slug>-tf-state-123456789" -backend-config="dynamodb_table=<app-slug>-tf-lock"
    encrypt = true
  }
}
