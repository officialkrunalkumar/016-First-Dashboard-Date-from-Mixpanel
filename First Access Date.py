import requests, os
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, timezone, timedelta
import time

def main(event):
  token = os.getenv("mixpanel")
  domain = event.get("inputFields").get("domain")
  eventName = "Dashboard"
  base_url = 'https://data.mixpanel.com/api/2.0/export/'
  yesterday = datetime.today() - timedelta(days=1)
  params = {
    'from_date': '2011-07-10',
    'to_date': yesterday.strftime('%Y-%m-%d'),
    'event': f'["{eventName}"]',
    'where': f'properties["tenant_email_domain"] == "{domain}"',
  }
  response = requests.get(base_url, params=params, auth=HTTPBasicAuth(token, ''))
  if response.status_code == 200:
    events = response.text.splitlines()
    if events:
      first_event = min(events, key=lambda event: json.loads(event)['properties']['time'])
      first_event_data = json.loads(first_event)
      timestamp_unix = first_event_data['properties'].get('time')
      first_dashboard_date = datetime.fromtimestamp(timestamp_unix, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
      datetime_obj = datetime.strptime(first_dashboard_date, "%Y-%m-%dT%H:%M:%SZ")
      timestamp_seconds = int(time.mktime(datetime_obj.timetuple()))
      hubspot_timestamp = timestamp_seconds * 1000
      return {
        "outputFields": {
          "firstAccessDate": hubspot_timestamp
        }
      }
    else:
        print(f"No onboarding events found for tenant domain {domain}")
  else:
    print(f"Request failed with status code: {response.status_code}")
    print("Response content:", response.text)