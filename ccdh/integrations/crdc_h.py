"""CRDCH Integration: Refresh CCDH model functionality

This is used by a GitHub action which rebuilds ccdh-terminology-service and
follows up by initiating a refresh of the CCDH model which depends on it.
"""
import os
import sys

import requests

from ccdh.config import get_settings


def trigger_refresh():
    """Triggers refresh in the CCDH model."""
    token = os.getenv('USER_ACCESS_TOKEN', get_settings().user_access_token)
    if not token:
        print('Error: Attempted to trigger update in CCDH Model repository, '
            'but "USER_ACCESS_TOKEN" was not found in environment.',
            file=sys.stderr)
    else:
        r = requests.post(
            'https://api.github.com/repos/cancerDHC/ccdhmodel/dispatches',
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            json={
                "event_type": "refreshModel"
            })
        if r.status_code >= 400:  # errors defined as codes 400 and above
            print(
                'Error: Triggering update in CCDH Model repository failed.',
                file=sys.stderr)


if __name__ == '__main__':
    trigger_refresh()
