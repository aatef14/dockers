# EC2 Details Extractor

This script extracts detailed information about EC2 instances across all AWS regions and exports the data to an Excel file.

## Prerequisites

- Python 3.x
- AWS account with appropriate permissions
- AWS credentials configured (see below)
- Required Python packages:
  - boto3
  - pandas
  - pytz
  - requests

## AWS Credentials Configuration

The script supports multiple ways to provide AWS credentials:

### 1. Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
# If using temporary credentials:
export AWS_SESSION_TOKEN=your_session_token
```

### 2. AWS CLI Configuration
```bash
# Run this command and enter your credentials
aws configure
```
This creates/updates `~/.aws/credentials` file with:
```
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
```

### 3. AWS CloudShell
- If running in AWS CloudShell, the script automatically detects and uses CloudShell credentials
- No additional configuration needed

You can verify your credentials are working by running:
```bash
aws sts get-caller-identity
```

The script checks for credentials in this order:
1. Environment variables
2. CloudShell environment
3. AWS CLI configuration

## Installation

1. Clone this repository
2. Install required packages:
```bash
pip install boto3 pandas pytz requests
```

## Usage

### Running with Python

The script can be run in two ways:

#### 1. With Default Filename (Auto-generated with timestamp)
```bash
python ec2_details_to_excel.py
```
This will create a file named `ec2_details_YYYYMMDD_HHMMSS.xlsx` in the `ec2_reports` directory.

#### 2. With Custom Filename
```bash
python ec2_details_to_excel.py your_custom_filename
```
This will create a file named `your_custom_filename.xlsx` in the `ec2_reports` directory.

### Running with Docker

#### 1. With Default Filename (Auto-generated with timestamp)
```bash
docker run \
--rm \
--network host \
-v $(pwd)/reports:/app/ec2_reports \
-e AWS_CONTAINER_CREDENTIALS_FULL_URI=$AWS_CONTAINER_CREDENTIALS_FULL_URI \
-e AWS_CONTAINER_AUTHORIZATION_TOKEN=$AWS_CONTAINER_AUTHORIZATION_TOKEN  \
-e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
aatef14/ec2-report:03
```
This will create a file named `ec2_details_YYYYMMDD_HHMMSS.xlsx` in your local `reports` directory and remove the container after execution.

#### 2. With Custom Filename
```bash
docker run \
 --rm \
--network host \
-v $(pwd)/reports:/app/ec2_reports \
-e AWS_CONTAINER_CREDENTIALS_FULL_URI=$AWS_CONTAINER_CREDENTIALS_FULL_URI \
-e AWS_CONTAINER_AUTHORIZATION_TOKEN=$AWS_CONTAINER_AUTHORIZATION_TOKEN \
-e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
aatef14/ec2-report:03 \
"your_custom_filename"
```
This will create a file named `your_custom_filename.xlsx` in your local `reports` directory and remove the container after execution.

### Examples

1. Using default filename:
```bash
# Python
python ec2_details_to_excel.py
# Output: ec2_reports/ec2_details_20240315_123456.xlsx

# Docker
docker run \
--rm \
--network host \
-v $(pwd)/reports:/app/ec2_reports \
-e AWS_CONTAINER_CREDENTIALS_FULL_URI=$AWS_CONTAINER_CREDENTIALS_FULL_URI \
-e AWS_CONTAINER_AUTHORIZATION_TOKEN=$AWS_CONTAINER_AUTHORIZATION_TOKEN \
-e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
aatef14/ec2-report:03 
# Output: reports/ec2_details_20240315_123456.xlsx
```

2. Using custom filename:
```bash
# Python
python ec2_details_to_excel.py production_servers
# Output: ec2_reports/production_servers.xlsx

# Docker
docker run --rm --network host -v $(pwd)/reports:/app/ec2_reports -e AWS_CONTAINER_CREDENTIALS_FULL_URI=$AWS_CONTAINER_CREDENTIALS_FULL_URI -e AWS_CONTAINER_AUTHORIZATION_TOKEN=$AWS_CONTAINER_AUTHORIZATION_TOKEN -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION aatef14/ec2-report:03 "production_servers"
# Output: reports/production_servers.xlsx
```

3. Using custom filename with spaces:
```bash
# Python
python ec2_details_to_excel.py "Production Servers Report"
# Output: ec2_reports/Production Servers Report.xlsx

# Docker
docker run --rm --network host -v $(pwd)/reports:/app/ec2_reports -e AWS_CONTAINER_CREDENTIALS_FULL_URI=$AWS_CONTAINER_CREDENTIALS_FULL_URI -e AWS_CONTAINER_AUTHORIZATION_TOKEN=$AWS_CONTAINER_AUTHORIZATION_TOKEN -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION aatef14/ec2-report:03 "Production Servers Report"
# Output: reports/Production Servers Report.xlsx
```

## Output

- The script creates an Excel file containing detailed information about all EC2 instances
- Files are saved in the `ec2_reports` directory (Python) or mounted volume (Docker)
- The directory is automatically created if it doesn't exist
- The Excel file includes information such as:
  - Instance ID
  - Instance Type
  - State
  - Region
  - Launch Time
  - Tags
  - And more...

## Notes

- The script requires valid AWS credentials to run
- It will automatically check for credentials in:
  - Environment variables
  - AWS CLI configuration
  - CloudShell environment
- The script handles errors gracefully and provides informative messages

### Checking AWS Environment Variables in CloudShell

To verify your AWS environment variables in CloudShell, run:
```bash
env | grep AWS
```

This will show all AWS-related environment variables, including:
- AWS_CONTAINER_CREDENTIALS_FULL_URI
- AWS_CONTAINER_AUTHORIZATION_TOKEN
- AWS_DEFAULT_REGION
- AWS_EXECUTION_ENV

These variables are automatically set in CloudShell and are used by the Docker container to authenticate with AWS services

### Creating a Shortcut Command

To make the command shorter, you can create an alias in your shell:

```bash
alias ec2-report='docker run --rm --network host -v $(pwd)/reports:/app/ec2_reports -e AWS_CONTAINER_CREDENTIALS_FULL_URI=$AWS_CONTAINER_CREDENTIALS_FULL_URI -e AWS_CONTAINER_AUTHORIZATION_TOKEN=$AWS_CONTAINER_AUTHORIZATION_TOKEN -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION aatef14/ec2-report:03'
```

Then you can simply run:
```bash
ec2-report
```

Or with a custom filename:
```bash
ec2-report "your_custom_filename"
```

To make the alias permanent, add it to your `~/.bashrc` file.

License
NO-COPYRIGHT FREECENSE 
