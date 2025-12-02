"""
Utility to add an IP/CIDR to a MongoDB Atlas project Access List via Atlas API.

Usage (PowerShell):
  $env:ATLAS_PUBLIC_KEY='yourPublicKey'
  $env:ATLAS_PRIVATE_KEY='yourPrivateKey'
  $env:ATLAS_PROJECT_ID='yourProjectId'
  python backend\atlas_allowlist.py --cidr 0.0.0.0/0

Security: this script requires Atlas API keys with Project Owner or Project Access List privileges.
Adding 0.0.0.0/0 allows connections from any IP to your Atlas cluster — only do this if you understand the risk.
"""

import os
import argparse
import json
import requests
from requests.auth import HTTPDigestAuth

API_BASE = 'https://cloud.mongodb.com/api/atlas/v1.0'


def add_access_list(public_key: str, private_key: str, project_id: str, cidr: str, comment: str = None):
    url = f"{API_BASE}/groups/{project_id}/accessList"
    payload = [{
        'ipAddress': cidr,
    }]
    if comment:
        payload[0]['comment'] = comment

    resp = requests.post(url, auth=HTTPDigestAuth(public_key, private_key), json=payload)
    if resp.status_code in (200, 201):
        print('Success: added access list entry')
        print(json.dumps(resp.json(), indent=2))
    else:
        print('Failed: HTTP', resp.status_code)
        try:
            print(resp.json())
        except Exception:
            print(resp.text)
        resp.raise_for_status()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cidr', default='0.0.0.0/0', help='CIDR to allow (default: 0.0.0.0/0)')
    parser.add_argument('--project-id', dest='project_id', help='Atlas Project ID (group id)')
    parser.add_argument('--public-key', dest='public_key', help='Atlas API Public Key')
    parser.add_argument('--private-key', dest='private_key', help='Atlas API Private Key')
    parser.add_argument('--comment', help='Comment for the access list entry')

    args = parser.parse_args()

    public_key = args.public_key or os.getenv('ATLAS_PUBLIC_KEY')
    private_key = args.private_key or os.getenv('ATLAS_PRIVATE_KEY')
    project_id = args.project_id or os.getenv('ATLAS_PROJECT_ID')

    if not (public_key and private_key and project_id):
        print('ERROR: Provide ATLAS_PUBLIC_KEY, ATLAS_PRIVATE_KEY, and ATLAS_PROJECT_ID (or use flags).')
        exit(2)

    print(f"Adding CIDR {args.cidr} to project {project_id} (THIS ALLOWS WIDE ACCESS)")
    add_access_list(public_key, private_key, project_id, args.cidr, comment=args.comment)
