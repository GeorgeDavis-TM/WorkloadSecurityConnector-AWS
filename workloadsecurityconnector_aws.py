#!/usr/bin/env python3
import json
import urllib3
import boto3
from botocore.exceptions import ClientError
from boto3 import Session

f = open("config.json", "r+")
configObj = json.loads(f.read())
f.close()

headers = {
    "Content-Type": "application/json",
    "api-secret-key": configObj["c1wsApiKey"],
    "api-version": "v1"
}

def buildRequestBody():
    data = {
        "displayName": getConfigValue("awsDisplayName") if checkConfKeyExists("awsDisplayName") else "",
        "accountId": getConfigValue("awsAccountId") if checkConfKeyExists("awsAccountId") else "",
        "accountAlias": getConfigValue("awsDisplayName") if checkConfKeyExists("awsDisplayName") else "",
        "useInstanceRole": getConfigValue("useInstanceRole") if checkConfKeyExists("useInstanceRole") else False,
        "workspacesEnabled": getConfigValue("workspacesEnabled") if checkConfKeyExists("workspacesEnabled") else False
    }
    return data

def selectConnectorOptions():
    print("\n\t1. Use an Instance Role\n\t2. Use a Cross-Account Role\n\t3. Use Access and Secret Keys")
    option = input("\nChoose an option to connect your AWS Account - ")
    return option

def checkConfKeyExists(configKey):
    return configKey in configObj.keys()

def getConfigValue(configKey):
    return configObj[configKey]

def createIAMUser():
    try:
        iamClient = boto3.client('iam')
        iamResponse = iamClient.create_user(
            Path='/',
            UserName='CloudOneWorkloadSecurityConnectorUser',
            Tags=[
                {
                    'Key': 'Owner',
                    'Value': 'TrendMicro'
                },
                {
                    'Key': 'Product',
                    'Value': 'CloudOneWorkloadSecurity'
                },
                {
                    "Key": "Name",
                    "Value": "CloudOneWorkloadSecurityConnectorUser"
                }
            ]
        )

        iamPolicyResponse = iamClient.create_policy(
            PolicyName='CloudOneWorkloadSecurityConnectorPolicy',
            Path='/',
            PolicyDocument='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["ec2:DescribeInstances","ec2:DescribeImages","ec2:DescribeRegions","ec2:DescribeVpcs","ec2:DescribeSubnets","ec2:DescribeTags","workspaces:DescribeWorkspaces","workspaces:DescribeWorkspaceDirectories","workspaces:DescribeWorkspaceBundles"],"Resource":"*"}]}',
            Description='Policy for the AWS Connector for Trend Micro Cloud One Workload Security'
        )

        iamClient.attach_user_policy(
            UserName=iamResponse["User"]["UserName"],
            PolicyArn=iamPolicyResponse["Policy"]["Arn"]
        )

        return iamResponse["User"]["UserName"]
    except ClientError as err:
        print("\n\nError: " + str(err))
        print("\n\nExiting..\n\n")
        return False

def createAccessKeyForIAMUser(username):
    iamClient = boto3.client('iam')
    iamResponse = iamClient.create_access_key(
        UserName=username
    )
    return iamResponse["AccessKey"]["AccessKeyId"], iamResponse["AccessKey"]["SecretAccessKey"]

def getAwsAccessSecretKeys(data):
    accessKey = ""
    secretKey = ""
    print("\n\t1. Create a new AWS User Access Key and Secret credentials\n\t2. Use an existing credentials from the local workspace\n\t3. Manually enter an Access and Secret Key")
    option = input("\nChoose an option to get credentials for your AWS Account - ")
    if option == "1":
        username = createIAMUser()
        if username:
            accessKey, secretKey = createAccessKeyForIAMUser(username)
    elif option == "2":
        print("\n\tChecking for aws credentials/config file in the current user directory, if it exists...")
        session = Session()
        credentials = session.get_credentials()
        # Credentials are refreshable, so accessing your access key / secret key
        # separately can lead to a race condition. Use this to get an actual matched
        # set.
        current_credentials = credentials.get_frozen_credentials()

        # I would not recommend actually printing these. Generally unsafe.
        accessKey = current_credentials.access_key
        secretKey = current_credentials.secret_key
        if accessKey and secretKey:
            print("\nLocal credentials accepted.")
    elif option == "3":
        accessKey = str(input("\n\tAWS Access Key : "))
        secretKey = str(input("\n\tAWS Secret Key : "))
    else:
        print("\n\nError: Invalid choice input")
    if accessKey and secretKey:
        data.update({"accessKey": accessKey})
        data.update({"secretKey": secretKey})
        return data
    else:
        return ""

def postAwsConnector(data):
    http = urllib3.PoolManager()
    r = http.request("POST", configObj["dsmHost"] + "/api/awsconnectors", headers=headers, body=json.dumps(data))

    if r.status == 200:
        print("\n\nSuccess: AWS Connector created.")
        print("\n\nExiting..\n\n")
    else:
        print(str(r.data))

def main():
    print("\n\nCloud One Workload Security - AWS Connector Configurator tool\n==================================================================")
    data = buildRequestBody()
    option = selectConnectorOptions()
    if option == "1":
        if checkConfKeyExists("useInstanceRole"):
            if not getConfigValue("useInstanceRole"):
                confirmation = input("\nuseInstanceRole flag is set to false in config.json. Do you want to enable 'useInstanceRole'? [Y/n] - ")
                if confirmation.lower() == "y":
                    data.update({"useInstanceRole": True})
                else:
                    data = None
        else:
            print("\nNo 'useInstanceRole' flag mentioned in config.json")
            data = None
    elif option == "2":
        if checkConfKeyExists("crossAccountRoleArn"):
            data.update({"crossAccountRoleArn": getConfigValue("crossAccountRoleArn")})
        else:
            print("\nNo Cross-Account Access Role ARN mentioned in config.json")
            data = None
    elif option == "3":
        data = getAwsAccessSecretKeys(data)
    else:
        print("\n\nInvalid choice. Try again.")
        print("\n\nExiting..\n\n")

    if data:
        if not data["workspacesEnabled"]:
            confirmation = input("\nAre you sure to proceed without connecting your AWS Workspaces to this connector? [Y/n] - ")
            if confirmation.lower() == "n":
                data["workspacesEnabled"] = True
            else:
                print("\nSkipping AWS Workspaces...")
        postAwsConnector(data)
    else:
        print("\n\nError: Missing or incorrect data parameters used for the tool.")
        print("\n\nExiting..\n\n")


if __name__ == "__main__":
    main()
