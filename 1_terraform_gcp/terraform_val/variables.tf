variable "project" {
  description = "The project ID"
  default = "dtc-de-419107"
}

variable "region" {
  description = "The region of the project"
  default = "us-central1"
}

variable "bq_dataset_name" {
  description = "The name of the BigQuery dataset"
  default = "demo_dataset"
}

variable "gcs_storage_class" {
  description = "The storage class of the GCS bucket"
  default = "STANDARD"
}

variable "gcs_bucket_name" {
  description = "The name of the GCS bucket"
  default = "dtc-de-419107-terra-bucket"
}

variable "location" {
  description = "The location of the project"
  default = "US"
}

