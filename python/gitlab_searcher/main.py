import json
import logging
import os

import gitlab
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

gitlab_token = os.environ["GITLAB_TOKEN"]
gitlab_url = f"https://{os.environ['GITLAB_HOST']}"

search_string = ""

gl = gitlab.Gitlab(
    private_token=gitlab_token,
    url=gitlab_url,
    pagination="keyset",
    order_by="id",
    per_page=100,
)
gl.auth()

logging.info(
    "Calling Gitlab API for details about all projects, this will take a couple of minutes.."
)

all_projects = list(gl.projects.list(get_all=True, lazy=True))

total_projects = len(all_projects)

logging.info(
    f"Total amount of projects: {total_projects}, will now proceed to search projects for {search_string}."
)


def search_projects(project_ids):
    result_json = {}
    result_txt = ""

    for project in tqdm(project_ids, desc="Searching projects"):
        project_id = project.attributes["id"]
        current_project_object = gl.projects.get(project_id, lazy=True)
        search = current_project_object.search(
            gitlab.const.SearchScope.BLOBS,
            search_string,
            iterator=True,
            total=total_projects,
        )

        if search:
            result_json[project_id] = search._data
            result_txt += f"{project.attributes['http_url_to_repo']}\n"

    return result_json, result_txt


with open("projects.json", "w", encoding="utf-8") as f:
    json.dump(search_projects(all_projects)[0], f, indent=2, ensure_ascii=False)

with open("repos.txt", "w", encoding="utf-8") as f:
    f.write(search_projects(all_projects)[1])
