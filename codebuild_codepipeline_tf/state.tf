
terraform{
    backend "s3" {
        bucket = "haitong-aws-cicd-pipeline"
        encrypt = true
        key = "terraform.tfstate"
        region = "ap-southeast-1"
    }
}

provider "aws" {
    region = "ap-southeast-1"
}