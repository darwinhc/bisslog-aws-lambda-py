# bisslog-lambda-aws

[![PyPI](https://img.shields.io/pypi/v/bisslog-aws-lambda)](https://pypi.org/project/bisslog-aws-lambda/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**bisslog-lambda-aws** is a lightweight Python library for integrating AWS Lambda with a clean, hexagonal architecture. It helps decouple domain logic from infrastructure by generating AWS-compatible handlers and deployment packages — all from metadata.

---

## ✨ Features

- 🧱 **Hexagonal architecture-first**: Keeps your domain logic isolated from AWS-specific code.
- ⚙️ **Automatic Lambda handler generation**: Based on YAML/JSON metadata.
- 📦 **ZIP packager for deployment**: Easily create deployable `.zip` archives.
- 🧪 **CLI for automation**: Analyze, generate and package with terminal commands.

---

## 📦 Installation

```bash
pip install bisslog-lambda-aws
```

## 🚀 Command Line Interface (CLI)

The library includes a CLI tool for metadata-driven Lambda handler generation and packaging.


~~~bash
bisslog_aws_lambda <command> [options]
~~~

### Available Commands

#### 🔍 print_lambda_handlers

Prints the generated AWS Lambda handlers to stdout without creating any files.
##### Example

~~~bash
bisslog_aws_lambda print_lambda_handlers \
  --metadata-file ./metadata/use_cases.yaml \
  --use-cases-folder-path ./src/domain/use_cases
~~~

##### Options

-  `--metadata-file`: Path to the metadata file (YAML or JSON). [required]

- `--use-cases-folder-path`: Path to the folder containing use case classes. [required]

- `--filter-uc`: Optional regex to filter which use cases are processed.

- `--encoding`: File encoding (default: utf-8).

#### 💾 generate_lambda_handlers

Generates AWS Lambda handler Python files and saves them to a specified folder.
##### Example

~~~bash
bisslog_aws_lambda generate_lambda_handlers \
  --metadata-file ./metadata/use_cases.yaml \
  --use-cases-folder-path ./src/domain/use_cases \
  --target-folder ./generated_handlers
~~~

##### Options

- `--metadata-file`: Path to the metadata file. [required]

- `--use-cases-folder-path`: Folder with use case classes. [required]

- `--target-folder`: Folder where the generated handlers will be saved. [required]

- `--filter-uc`: Optional use case name filter (regex).

- `--encoding`: File encoding (default: utf-8).

#### 📦 generate_lambda_zips

Packages AWS Lambda handlers into .zip files ready for deployment.
##### Example

~~~shell
bisslog_aws_lambda generate_lambda_zips \
  --handler-name user_create_handler \
  --src-folders ./src ./libs \
  --handlers-folder ./generated_handlers
~~~

##### Options

- `--handler-name`: Name of the Lambda handler to package. [required]

- `--src-folders`: One or more source folders to include in the ZIP. [required]

- `--handlers-folder`: Folder where handler files are located. [required]


## ✅ Requirements

    Python 3.7+

    AWS Lambda-compatible Python project

## 🔧 Development

~~~shell
git clone https://github.com/your-org/bisslog-lambda-aws.git
cd bisslog-lambda-aws
pip install -e .
~~~

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
