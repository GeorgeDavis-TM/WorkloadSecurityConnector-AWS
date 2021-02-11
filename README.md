# WorkloadSecurityConnector-AWS Integration

Automation scripts to setup the AWS Connector on Trend Micro Cloud One Workload Security / Deep Security (On-Prem on AWS)


## Setup Instructions

Step 1: Create a Cloud One Workload Security API Key. Refer to the Workload Security documentation for steps to create this API key - https://cloudone.trendmicro.com/docs/workload-security/api-send-request/#create-an-api-key

Step 2: Setup the Cloud One Workload Security and AWS Account information

Step 3: Run the Python script `python3 workloadsecurityconnector_aws.py`


## How it works

The Python utility script calls Trend Micro Cloud One Workload Security / Deep Security APIs to connect your AWS Account to the dashboard. Connecting AWS Accounts enable the visiblity into the EC2 instances and Amazon Workspaces in your account so that you can manage agents from various different AWS Accounts remotely, from a single console.

For the integration, the python script creates the following -

- IAM User with Programmatic Access (API Access and Secret Keys)
- IAM Policy that is attached to the newly created IAM User account

### IAM Policy Document

`{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeImages",
                "ec2:DescribeRegions",
                "ec2:DescribeVpcs",
                "ec2:DescribeSubnets",
                "ec2:DescribeTags",
                "workspaces:DescribeWorkspaces",
                "workspaces:DescribeWorkspaceDirectories",
                "workspaces:DescribeWorkspaceBundles"
            ],
            "Resource": "*"
        }
    ]
}`


### Connector Options

Cloud One Workload Security / Deep Security Manager uses one of three methods to understand how your resources are deployed on AWS

- Use an Instance Role - Uses the EC2 Instance Role attached to the DSM instance on AWS
- Use a Cross-Account Role - Uses the IAM Cross-Account Access role for     
- Use Access and Secret Keys - Uses the API Access and Secret keys to access Cloud metadata


### Cloud One Workload / Deep Security Manager API Support

This AWS Connector Configurator tool supports a subset of the Cloud One Workload Security / Deep Security APIs. Here is a list of all the values that is supported with this tool.

| API Parameter  | Tool Support Status |
| ------------- | ------------- |
| displayName  | Supported  |
| accountId  | Supported  |
| accountAlias  | Supported  |
| accessKey  | Supported  |
| secretKey  | Supported  |
| seedRegion  | Unsupported  |
| useInstanceRole  | Supported  |
| crossAccountRoleArn  | Supported  |
| lastSyncTime  | Unsupported  |
| syncedRegions  | Unsupported  |
| workspacesEnabled  | Supported  |


### Tool Config parameters

The `config.json` file is crucial for using this tool. Please provide all required values on the config.json file for the script to run successfully.

| Parameter  | Datatype | Description | Required/Not required |
| ------------- | ------------- | ------------- | ------------- |
| dsmHost  | String  | `https://dsm.example.com:4119` for On-Prem instances or `https://cloudone.trendmicro.com` for Cloud One SaaS | Required |
| c1wsApiKey  | String  | `<Your-API-Key>` | Required |
| awsDisplayName  | String  | The script uses this value for both displayName and accountAlias | Required |
| awsAccountId  | String  | 123456789012 | Required |
| accessKey  | String  | AKIA***************KB | Not required based on the Connector options chosen during runtime. The value is taken from the local `~/.aws/credentials` or `~/.aws/config` files or request for one during runtime. |
| secretKey  | String  | Xla**************************63L/+ | Not required based on the Connector options. The value is taken from the local `~/.aws/credentials` or `~/.aws/config` files or request for one during runtime. |
| useInstanceRole  | Boolean  | Defaults to False | Not required based on the Connector options chosen during runtime |
| crossAccountRoleArn  | String  | ARN of the IAM Cross-Account Access Role | Not required based on the Connector options chosen during runtime |
| workspacesEnabled  | Boolean  | Defaults to False | Required |

### Related Projects

| GitHub Repository Name  | Description |
| ------------- | ------------- |
| [cloudOneWorkloadSecurityDemo](https://github.com/GeorgeDavis-TM/cloudOneWorkloadSecurityDemo) | Run an attack simulation on your workload to test policy events and alerts |
| [WorkloadSecurity-AWS-SNS](https://github.com/GeorgeDavis-TM/WorkloadSecurity-AWS-SNS) | Setup Event forwarding with AWS SNS to build custom rules and workflow based on detection events |


## Contributing

If you encounter a bug or think of a useful feature, or find something confusing in the docs, please
**[Create a New Issue](https://github.com/GeorgeDavis-TM/WorkloadSecurity-AWS-SNS/issues/new)**

 **PS.: Make sure to use the [Issue Template](https://github.com/GeorgeDavis-TM/WorkloadSecurity-AWS-SNS/tree/master/.github/ISSUE_TEMPLATE)**

We :heart: pull requests. If you'd like to fix a bug or contribute to a feature or simply correct a typo, please feel free to do so.

If you're thinking of adding a new feature, consider opening an issue first to
discuss it to ensure it aligns to the direction of the project (and potentially
save yourself some time!).