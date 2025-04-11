import requests
import json
import argparse
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError

API_VERSION = "2022-08-01"
RESOURCE = "https://management.azure.com/"

credential = DefaultAzureCredential()

def get_token():
    try:
        token = credential.get_token(f"{RESOURCE}/.default")
        return token
    except ClientAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        exit(1)

def list_subscriptions(apim, token):
    url = f"https://management.azure.com/subscriptions/{apim['subscription_id']}/resourceGroups/{apim['resource_group']}/providers/Microsoft.ApiManagement/service/{apim['name']}/subscriptions?api-version={API_VERSION}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Print # of subscriptions retrieved
        print(f"✅ Retrieved {len(response.json().get('value', []))} subscriptions.")
        return response.json().get("value", [])
    else:
        print(f"❌ Failed to list subscriptions: {response.status_code} {response.text}")
        exit(1)

def get_subscription(apim, subscription_id, token):
    url = f"https://management.azure.com/subscriptions/{apim['subscription_id']}/resourceGroups/{apim['resource_group']}/providers/Microsoft.ApiManagement/service/{apim['name']}/subscriptions/{subscription_id}?api-version={API_VERSION}"
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get subscription: {response.status_code} {response.text}")
        exit(1)

def get_subscription_keys(apim, subscription_id, token):
    url = f"https://management.azure.com/subscriptions/{apim['subscription_id']}/resourceGroups/{apim['resource_group']}/providers/Microsoft.ApiManagement/service/{apim['name']}/subscriptions/{subscription_id}/listSecrets?api-version={API_VERSION}"
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        # Return a string tuple with the following properties from the JSON: "primaryKey", "secondaryKey"
        keys = response.json()
        return keys.get("primaryKey"), keys.get("secondaryKey")

    else:
        print(f"❌ Failed to get subscription keys: {response.status_code} {response.text}")
        exit(1)

def migrate_subscriptions(source_apim, target_apim):
    token = get_token()
    subscriptions = list_subscriptions(source_apim, token.token)
    return token

def main():
    parser = argparse.ArgumentParser(description="Migrate APIM subscriptions (with keys) between APIM instances.")
    parser.add_argument("--source-subscription-id", required=True, help="Azure Subscription ID for source APIM instance")
    parser.add_argument("--source-apim-name", required=True, help="Name of the source APIM instance")
    parser.add_argument("--target-subscription-id", required=True, help="Azure Subscription ID for target APIM instance")
    parser.add_argument("--target-apim-name", required=True, help="Name of the target APIM instance")
    parser.add_argument("--source-resource-group", required=True, help="Resource group of the source APIM instance")
    parser.add_argument("--target-resource-group", required=True, help="Resource group of the target APIM instance")

    args = parser.parse_args()

    source_apim = {
        "name": args.source_apim_name,
        "resource_group": args.source_resource_group,
        "subscription_id": args.source_subscription_id
    }

    target_apim = {
        "name": args.target_apim_name,
        "resource_group": args.target_resource_group,
        "subscription_id": args.target_subscription_id
    }

    migrate_subscriptions(source_apim, target_apim)

if __name__ == "__main__":
    main()