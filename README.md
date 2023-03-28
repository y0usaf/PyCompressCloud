# Advanced File Archiver

This repository contains an advanced file archiver utility that demonstrates the ability to compress and decompress files using various compression algorithms, a command-line interface, recursive folder compression, cloud storage integration, progress reporting, error handling, logging, and unit testing.

## Features:
* Support for multiple compression algorithms: gzip, zlib, bz2, and lzma
* Command-line interface for user interaction
* Recursive folder compression and decompression, preserving the directory structure
* Integration with Amazon S3 and Google Cloud Storage for direct file upload and download
* Logging for improved robustness and maintainability

Dependencies

To use this utility, you'll need to install the following Python libraries:

    boto3: for Amazon S3 integration
    google-cloud-storage: for Google Cloud Storage integration
    tqdm: for progress reporting (optional, but recommended)

You can install them using the following command:


    pip install boto3 google-cloud-storage tqdm
# Usage
## Basic Usage

Compress a file:

    python PyCompressCloud.py compress input.txt output.gz --algorithm gzip

Decompress a file:

    python PyCompressCloud.py decompress input.gz output.txt --algorithm gzip

## Advanced Usage

Compress a directory:

    python PyCompressCloud.py compress input_directory output_directory --algorithm gzip

Decompress a directory:

    python PyCompressCloud.py decompress input_directory output_directory --algorithm gzip

## Cloud Storage Integration

Upload a file to Amazon S3:

    python PyCompressCloud.py cloud s3 upload local_file.txt my-bucket-name s3_object_key

Download a file from Amazon S3:

    python PyCompressCloud.py cloud s3 download local_file.txt my-bucket-name s3_object_key

Upload a file to Google Cloud Storage:

    python PyCompressCloud.py cloud gcs upload local_file.txt my-bucket-name gcs_blob_name

Download a file from Google Cloud Storage:

    python PyCompressCloud.py cloud gcs download local_file.txt my-bucket-name gcs_blob_name

Credentials

To use the cloud storage features, you'll need to set up the necessary credentials for AWS and GCP, following their respective documentation:

- [AWS Credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)
- [GCP Credentials](https://cloud.google.com/docs/authentication/client-libraries)

License

This project is released under the [MIT License.](https://opensource.org/license/mit/)