import os
import requests
from requests.auth import HTTPBasicAuth
import json
from progress.bar import Bar

findings = {}

#Authentication
email="atlassian@adm.com"
atlassian_api_key=''

# Fetch User Function

def atlassian_get_user(email, api_token, account_id):
  # This code sample uses the 'requests' library:
  # http://docs.python-requests.org
  url = "https://atlassian-org.atlassian.net/wiki/rest/api/user"

  auth = HTTPBasicAuth(email, api_token)

  headers = {
    "Accept": "application/json"
  }

  query = {
    'accountId': account_id
  }

  response = requests.request(
    "GET",
    url,
    headers=headers,
    params=query,
    auth=auth
  )

  return json.loads(response.text)

# Fetch Spaces Function

def atlassian_spaces(email, api_token):
  # This code sample uses the 'requests' library:
  # http://docs.python-requests.org
  import requests
  from requests.auth import HTTPBasicAuth
  import json

  url = "https://atlassian-org.atlassian.net/wiki/api/v2/spaces"

  auth = HTTPBasicAuth(email, api_token)

  headers = {
    "Accept": "application/json"
  }

  response = requests.request(
    "GET",
    url,
    headers=headers,
    auth=auth,
  )

  jsonload_response = json.loads(response.text)
  results = jsonload_response['results']

  if jsonload_response.get('_links').get('next') is not None:
    run = 1

    while run != 0:
      if jsonload_response.get('_links').get('next') is not None:
        new_url = "https://atlassian-org.atlassian.net"+jsonload_response['_links']['next']
        new_response = requests.request(
          "GET",
          new_url,
          headers=headers,
          auth=auth,
        )
        jsonload_response = json.loads(new_response.text)
        for i in jsonload_response['results']:
          results.append(i)
      else:
        run = 0

  return results

spaces = atlassian_spaces(email, atlassian_api_key)

with Bar('Processing...', max=len(spaces)) as bar:
  for space in spaces:
      user = atlassian_get_user(email, atlassian_api_key, space['authorId'])
      findings.update({ user['email']: { 
        "user_name": user['publicName'],
        "author_of_space": space['name'],
        "user_id": user['accountId'],
        "space_key": space['key'],
        "url": space['_links']['webui'],
        "created_at": space['createdAt']
        }
      })
      bar.next()

#Write file
f = open("spaceAuthors.json", "a")
f.write(json.dumps(findings, indent = 4))
f.close()
