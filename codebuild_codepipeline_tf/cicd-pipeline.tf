resource "aws_codebuild_project" "tf-plan" {
  name          = var.codebuild_project_name
  description   = "Plan stage for terraform"
  service_role  = var.tf_codebuild_role

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "hashicorp/terraform:0.14.3"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
    # registry_credential{
    #     credential = var.dockerhub_credentials
    #     credential_provider = "SECRETS_MANAGER"
    # }
 }

 source {
     type   = "CODEPIPELINE"
     buildspec = file("plan-buildspec.yml")
 }
    
}

resource "aws_codepipeline" "cicd_pipeline" {

    name = var.codepipeline_name
    role_arn = var.tf_codepipeline_role

    artifact_store {
        type="S3"
        location = var.codepipeline_artifacts
    }

    stage {
        name = "Source"
        action{
            name = "Source"
            category = "Source"
            owner = "AWS"
            provider = "CodeStarSourceConnection"
            version = "1"
            output_artifacts = ["tf-code"]
            configuration = {
                FullRepositoryId = var.git_repo_id
                BranchName   = var.branch
                ConnectionArn = var.codestar_connector_credentials
                OutputArtifactFormat = "CODE_ZIP"
            }
        }
    }

    stage {
        name ="Plan"
        action{
            name = "Build"
            category = "Build"
            provider = "CodeBuild"
            version = "1"
            owner = "AWS"
            input_artifacts = ["tf-code"]
            configuration = {
                ProjectName = aws_codebuild_project.tf-plan.name
            }
        }
    }

}