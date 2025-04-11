"""if you wanto to run this script standalone, you can do it by running the following command: 
but first run this 
pip install boto3
pip install pandas
pip install openpyxl
pip install pytz
pip install requests

then run this command:
python ec2_details_to_excel.py

"""





import boto3
import pandas as pd
from datetime import datetime
import pytz
import sys
import os
import json
import configparser
from botocore.exceptions import ClientError, NoCredentialsError
import requests

def check_aws_credentials():
    """Check if AWS credentials are available and valid."""
    print("\nChecking AWS credentials...")
    
    try:
        # First try to get credentials from environment
        if all(k in os.environ for k in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY')):
            print("Found AWS credentials in environment variables")
            try:
                session = boto3.Session()
                sts = session.client('sts')
                identity = sts.get_caller_identity()
                print(f"Successfully authenticated as: {identity['Arn']}")
                return True
            except Exception as e:
                print(f"Error verifying environment credentials: {str(e)}")
        
        # Check if we're in CloudShell
        if os.environ.get('AWS_EXECUTION_ENV') == 'CloudShell':
            print("Found CloudShell environment")
            try:
                # Try to create a client to verify credentials
                session = boto3.Session()
                sts = session.client('sts')
                identity = sts.get_caller_identity()
                print(f"Successfully authenticated as: {identity['Arn']}")
                return True
            except Exception as e:
                print(f"Error verifying CloudShell credentials: {str(e)}")
        
        # Try AWS CLI configuration
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials is not None:
                # Verify the credentials
                sts = session.client('sts')
                identity = sts.get_caller_identity()
                print(f"Successfully authenticated using AWS CLI configuration as: {identity['Arn']}")
                return True
        except Exception as e:
            print(f"Error verifying AWS CLI credentials: {str(e)}")
        
        # If we get here, no valid credentials were found
        print("\nError: No valid AWS credentials found.")
        print("\nTroubleshooting steps:")
        print("1. For CloudShell:")
        print("   - Make sure you're running in AWS CloudShell")
        print("   - Check if AWS_EXECUTION_ENV is set correctly")
        print("   - Try running 'aws sts get-caller-identity' to verify credentials")
        print("\n2. For AWS CLI:")
        print("   - Run 'aws configure' to set up credentials")
        print("   - Check if ~/.aws/credentials exists and has valid credentials")
        print("   - Try running 'aws sts get-caller-identity' to verify")
        print("\n3. For environment variables:")
        print("   - Make sure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set")
        print("   - If using temporary credentials, ensure AWS_SESSION_TOKEN is set")
        print("\nCurrent environment variables:")
        for key in os.environ:
            if key.startswith('AWS_'):
                print(f"{key}: {'*' * 10}")  # Don't print actual values for security
        return False
        
    except Exception as e:
        print(f"\nError checking credentials: {str(e)}")
        return False

def get_volume_details(ec2_client, instance_id):
    volumes = ec2_client.describe_volumes(
        Filters=[{'Name': 'attachment.instance-id', 'Values': [instance_id]}]
    )['Volumes']
    
    volume_ids = []
    volume_types = []
    volume_sizes = []
    total_size = 0
    
    for volume in volumes:
        volume_ids.append(volume['VolumeId'])
        volume_types.append(volume['VolumeType'])
        volume_sizes.append(volume['Size'])
        total_size += volume['Size']
    
    return {
        'Volume_IDs': ', '.join(volume_ids),
        'Volume_Types': ', '.join(volume_types),
        'Volume_Sizes': ', '.join(str(size) for size in volume_sizes),
        'Total_Volume_Size': total_size
    }

def get_ec2_details():
    # Initialize boto3 clients with a specific region
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    
    try:
        # Get all regions
        regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    except Exception as e:
        print(f"Error getting regions: {str(e)}")
        regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']  # Fallback to major regions
    
    # List to store instance details
    instances_data = []
    
    # IST timezone for conversion
    ist = pytz.timezone('Asia/Kolkata')
    
    for region in regions:
        try:
            print(f"Checking region: {region}")
            # Create new client for each region
            ec2_client = boto3.client('ec2', region_name=region)
            
            # Describe instances in the region
            response = ec2_client.describe_instances()
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    # Get instance name from tags
                    instance_name = ''
                    if 'Tags' in instance:
                        for tag in instance['Tags']:
                            if tag['Key'] == 'Name':
                                instance_name = tag['Value']
                                break
                    
                    # Get volume details
                    volume_info = get_volume_details(ec2_client, instance['InstanceId'])
                    
                    # Get IAM Role
                    iam_role = ''
                    if 'IamInstanceProfile' in instance:
                        iam_role = instance['IamInstanceProfile']['Arn'].split('/')[-1]
                    
                    # Get network interface details
                    network_interface_id = ''
                    attach_time = ''
                    if instance['NetworkInterfaces']:
                        network_interface_id = instance['NetworkInterfaces'][0]['NetworkInterfaceId']
                        attach_time = instance['NetworkInterfaces'][0]['Attachment']['AttachTime']
                        # Convert to IST
                        attach_time = attach_time.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S %Z')
                    
                    # Get IPv6 address if available
                    ipv6_address = ''
                    if instance['NetworkInterfaces']:
                        ipv6_addresses = instance['NetworkInterfaces'][0].get('Ipv6Addresses', [])
                        if ipv6_addresses:
                            ipv6_address = ipv6_addresses[0]['Ipv6Address']
                    
                    instance_data = {
                        'Instance Name': instance_name,
                        'Instance ID': instance['InstanceId'],
                        'Instance State': instance['State']['Name'],
                        'Private IP': instance.get('PrivateIpAddress', ''),
                        'Public IP': instance.get('PublicIpAddress', ''),
                        'IPv6 IP': ipv6_address,
                        'Availability_Zone': instance['Placement']['AvailabilityZone'],
                        'Platform': instance.get('Platform', 'Linux/UNIX'),
                        'Instance Type': instance['InstanceType'],
                        'vCPU': instance['CpuOptions']['CoreCount'] * instance['CpuOptions']['ThreadsPerCore'],
                        'Memory (GiB)': '',  # This requires a separate lookup table as AWS API doesn't provide memory info
                        'Volume ID(s)': volume_info['Volume_IDs'],
                        'Volume Type(s)': volume_info['Volume_Types'],
                        'Volume Size (GB)': volume_info['Volume_Sizes'],
                        'Total Volume Size (GB)': volume_info['Total_Volume_Size'],
                        'Key Pair': instance.get('KeyName', ''),
                        'IAM Role': iam_role,
                        'Region': region,
                        'Network Interface ID': network_interface_id,
                        'Attach Time (IST)': attach_time
                    }
                    
                    instances_data.append(instance_data)
                    
        except Exception as e:
            print(f"Error processing region {region}: {str(e)}")
            continue
    
    return instances_data

def main():
    try:
        print("\n=== EC2 Instance Details Exporter ===\n")
        
        # Check AWS credentials first
        if not check_aws_credentials():
            sys.exit(1)
        
        # Get filename from command line argument or use default
        if len(sys.argv) > 1:
            fname = sys.argv[1]
            print(f"Using custom filename: {fname}")
        else:
            # Use default filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            fname = f'ec2_details_{timestamp}'
            print(f"Using default filename: {fname}")
        
        # Add .xlsx extension if not present
        if not fname.endswith('.xlsx'):
            output_file = f'{fname}.xlsx'
        else:
            output_file = fname
            
        # Get EC2 instance details
        print("\nFetching EC2 instance details across all regions...")
        instances_data = get_ec2_details()
        
        if not instances_data:
            print("\nNo EC2 instances found in any region.")
            sys.exit(0)
        
        # Create DataFrame
        print("\nProcessing instance data...")
        df = pd.DataFrame(instances_data)
        
        # Create output directory if it doesn't exist
        output_dir = 'ec2_reports'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Full path for output file
        output_path = os.path.join(output_dir, output_file)
        
        # Export to Excel
        print(f"\nExporting data to {output_path}...")
        df.to_excel(output_path, index=False, sheet_name='EC2 Instances')
        
        print(f"\nSuccess! EC2 instance details have been exported to: {output_path}")
        print(f"Total instances found: {len(instances_data)}")
        
        # Print summary
        print("\nSummary of instances by region:")
        region_summary = df['Region'].value_counts()
        for region, count in region_summary.items():
            print(f"{region}: {count} instance(s)")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 