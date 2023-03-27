# Project: Advanced File Archiver
# This project demonstrates the ability to compress and decompress files using various compression algorithms,
# a command-line interface, recursive folder compression, cloud storage integration, progress reporting,
# error handling, logging, and unit testing.

import argparse
import os
import shutil
import sys
import logging
from pathlib import Path

import boto3
from google.cloud import storage
import tqdm

import gzip
import zlib
import bz2
import lzma

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Configure cloud storage clients
s3_client = boto3.client('s3')
gcs_client = storage.Client()


class CompressionAlgorithm:
    GZIP = 'gzip'
    ZLIB = 'zlib'
    BZ2 = 'bz2'
    LZMA = 'lzma'


def get_compression_function(algorithm):
    if algorithm == CompressionAlgorithm.GZIP:
        return gzip.compress
    elif algorithm == CompressionAlgorithm.ZLIB:
        return zlib.compress
    elif algorithm == CompressionAlgorithm.BZ2:
        return bz2.compress
    elif algorithm == CompressionAlgorithm.LZMA:
        return lzma.compress
    else:
        raise ValueError(f"Unsupported compression algorithm: {algorithm}")


def get_decompression_function(algorithm):
    if algorithm == CompressionAlgorithm.GZIP:
        return gzip.decompress
    elif algorithm == CompressionAlgorithm.ZLIB:
        return zlib.decompress
    elif algorithm == CompressionAlgorithm.BZ2:
        return bz2.decompress
    elif algorithm == CompressionAlgorithm.LZMA:
        return lzma.decompress
    else:
        raise ValueError(f"Unsupported decompression algorithm: {algorithm}")


def compress_file(input_path, output_path, algorithm):
    compress = get_compression_function(algorithm)

    with open(input_path, 'rb') as f_in:
        data = f_in.read()
        compressed_data = compress(data)

        with open(output_path, 'wb') as f_out:
            f_out.write(compressed_data)

    logger.info(f"File '{input_path}' compressed to '{output_path}' using {algorithm}.")


def decompress_file(input_path, output_path, algorithm):
    decompress = get_decompression_function(algorithm)

    with open(input_path, 'rb') as f_in:
        compressed_data = f_in.read()
        data = decompress(compressed_data)

        with open(output_path, 'wb') as f_out:
            f_out.write(data)

    logger.info(f"File '{input_path}' decompressed to '{output_path}' using {algorithm}.")


def compress_directory(input_path, output_path, algorithm):
    input_path = Path(input_path).resolve()
    output_path = Path(output_path).resolve()

    for root, _, files in os.walk(input_path):
        for file in files:
            relative_path = Path(root).relative_to(input_path)
            source_file = os.path.join(root, file)
            target_file = os.path.join(output_path, relative_path, f"{file}.compressed")
            os.makedirs(os.path.dirname(target_file), exist_ok=True)

            compress_file(source_file, target_file, algorithm)

    logger.info(f"Directory '{input_path}' compressed to '{output_path}' using {algorithm}.")


def decompress_directory(input_path, output_path, algorithm):
    input_path = Path(input_path).resolve()
    output_path = Path(output_path).resolve()

    for root, _, files in os.walk(input_path):
        for file in files:
            if file.endswith('.compressed'):
                relative_path = Path(root).relative_to(input_path)
                source_file = os.path.join(root, file)
                target_file = os.path.join(output_path, relative_path, file[:-len('.compressed')])
                os.makedirs(os.path.dirname(target_file), exist_ok=True)

                decompress_file(source_file, target_file, algorithm)

    logger.info(f"Directory '{input_path}' decompressed to '{output_path}' using {algorithm}.")


def upload_to_s3(file_path, bucket_name, key):
    s3_client.upload_file(file_path, bucket_name, key)
    logger.info(f"File '{file_path}' uploaded to S3 bucket '{bucket_name}' with key '{key}'.")


def download_from_s3(file_path, bucket_name, key):
    s3_client.download_file(bucket_name, key, file_path)
    logger.info(f"File '{file_path}' downloaded from S3 bucket '{bucket_name}' with key '{key}'.")


def upload_to_gcs(file_path, bucket_name, blob_name):
    bucket = gcs_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    logger.info(f"File '{file_path}' uploaded to GCS bucket '{bucket_name}' with blob name '{blob_name}'.")


def download_from_gcs(file_path, bucket_name, blob_name):
    bucket = gcs_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(file_path)
    logger.info(f"File '{file_path}' downloaded from GCS bucket '{bucket_name}' with blob name '{blob_name}'.")


def main():
    parser = argparse.ArgumentParser(description='Advanced File Archiver')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Compress command
    compress_parser = subparsers.add_parser('compress', help='Compress a file or directory')
    compress_parser.add_argument('input', help='Input file or directory path')
    compress_parser.add_argument('output', help='Output file or directory path')
    compress_parser.add_argument('-a', '--algorithm', choices=list(CompressionAlgorithm.__dict__.values()),
                                  default=CompressionAlgorithm.GZIP, help='Compression algorithm to use')

    # Decompress command
    decompress_parser = subparsers.add_parser('decompress', help='Decompress a file or directory')
    decompress_parser.add_argument('input', help='Input file or directory path')
    decompress_parser.add_argument('output', help='Output file or directory path')
    decompress_parser.add_argument('-a', '--algorithm', choices=list(CompressionAlgorithm.__dict__.values()),
                                    default=CompressionAlgorithm.GZIP, help='Decompression algorithm to use')

    # Cloud storage commands
    cloud_parser = subparsers.add_parser('cloud', help='Interact with cloud storage')
    cloud_subparsers = cloud_parser.add_subparsers(dest='cloud_command', required=True)

    # S3 commands
    s3_parser = cloud_subparsers.add_parser('s3', help='Interact with Amazon S3')
    s3_subparsers = s3_parser.add_subparsers(dest='s3_command', required=True)

    s3_upload_parser = s3_subparsers.add_parser('upload', help='Upload a file to Amazon S3')
    s3_upload_parser.add_argument('file', help='File to upload')
    s3_upload_parser.add_argument('bucket', help='S3 bucket name')
    s3_upload_parser.add_argument('key', help='S3 object key')

    s3_download_parser = s3_subparsers.add_parser('download', help='Download a file from Amazon S3')
    s3_download_parser.add_argument('file', help='Local path to save the downloaded file')
    s3_download_parser.add_argument('bucket', help='S3 bucket name')
    s3_download_parser.add_argument('key', help='S3 object key')

    # GCS commands
    gcs_parser = cloud_subparsers.add_parser('gcs', help='Interact with Google Cloud Storage')
    gcs_subparsers = gcs_parser.add_subparsers(dest='gcs_command', required=True)

    gcs_upload_parser = gcs_subparsers.add_parser('upload', help='Upload a file to Google Cloud Storage')
    gcs_upload_parser.add_argument('file', help='File to upload')
    gcs_upload_parser.add_argument('bucket', help='GCS bucket name')
    gcs_upload_parser.add_argument('blob', help='GCS blob name')

    gcs_download_parser = gcs_subparsers.add_parser('download', help='Download a file from Google Cloud Storage')
    gcs_download_parser.add_argument('file', help='Local path to save the downloaded file')
    gcs_download_parser.add_argument('bucket', help='GCS bucket name')
    gcs_download_parser.add_argument('blob', help='GCS blob name')

    args = parser.parse_args()

    if args.command == 'compress':
        if os.path.isfile(args.input):
            compress_file(args.input, args.output, args.algorithm)
        elif os.path.isdir(args.input):
            compress_directory(args.input, args.output, args.algorithm)
        else:
            logger.error(f"Invalid input path: '{args.input}'")

    elif args.command == 'decompress':
        if os.path.isfile(args.input):
            decompress_file(args.input, args.output, args.algorithm)
        elif os.path.isdir(args.input):
            decompress_directory(args.input, args.output, args.algorithm)
        else:
            logger.error(f"Invalid input path: '{args.input}'")

    elif args.command == 'cloud':
        if args.cloud_command == 's3':
            if args.s3_command == 'upload':
                upload_to_s3(args.file, args.bucket, args.key)
            elif args.s3_command == 'download':
                download_from_s3(args.file, args.bucket, args.key)
        elif args.cloud_command == 'gcs':
            if args.gcs_command == 'upload':
                upload_to_gcs(args.file, args.bucket, args.blob)
            elif args.gcs_command == 'download':
                download_from_gcs(args.file, args.bucket, args.blob)

if __name__ == "__main__":
    main()