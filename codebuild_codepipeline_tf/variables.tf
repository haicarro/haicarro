# connections to github
variable codestar_connector_credentials {
    type = string
}

variable "tf_codebuild_role" {
  type = string
}

variable "codebuild_project_name" {
  type = string
}

variable "codepipeline_name" {
  type = string
}

variable "tf_codepipeline_role" {
  type = string 
}

variable "codepipeline_artifacts" {
  type = string
}

variable "git_repo_id" {
  type = string
}

variable "branch" {
  type = string
}