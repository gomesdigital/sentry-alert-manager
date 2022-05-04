"""
Script to configure alerts in Sentry.io, individually or
in bulk.

Copyright (C) 2022 Daniel Gomes-Sebastiao

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import os
from dotenv import load_dotenv
import requests
import json
import sys
import collections

# TODO
#
# build and include the postman workspace
#
# awesome README.md

load_dotenv()  # loads .env to system env variables
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
HEADERS = {'Authorization': f'Bearer {AUTH_TOKEN}'}
ORGANIZATION = os.getenv('ORGANIZATION')
BASE_URL = 'https://sentry.io/api/0'


def load_template(path):
    """
    Interprets the JSON file at the passed path and expands any environment
    variables.

    Returns:
        dict: An array of JSON alert payloads.

    Args:
        path (str): The path to the alert config file.
    """

    with open(path, 'r') as template:
        content = template.read()
        for subtring in content.split('$')[1:]:
            env = subtring.split('"')[0]
            try:
                content = content.replace(f'${env}', os.getenv(env))
            except Exception:
                print(f'Error: {env} is not defined in the .env file.')
    return json.loads(content)['alerts']


def ping():
    """
    Prints details that are associated with the supplied auth token.
    """

    teams_url = f"{BASE_URL}/organizations/gomesdigital/teams/"
    organizations_url = f"{BASE_URL}/organizations/"
    integrations_url = f"{BASE_URL}/organizations/gomesdigital/integrations/"

    teams = ''
    try:
        teams = requests.get(teams_url, headers=HEADERS)
        teams.raise_for_status()
        teams = json.loads(teams.text)
        print('\033[1mTeams\033[0m')
        for team in teams:
            print(f'    {team["slug"]} | team:{team["id"]}')
        print()
    except requests.exceptions.HTTPError as error:
        print("Error: Could not get teams data.")
        print(error)

    organizations = ''
    try:
        organizations = requests.get(organizations_url, headers=HEADERS)
        organizations.raise_for_status()
        organizations = json.loads(organizations.text)
        print('\033[1mOrganizations\033[0m')
        for organization in organizations:
            print(f'    {organization["slug"]} | {organization["id"]}')
        print()
    except requests.exceptions.HTTPError as error:
        print("Error: Could not get organizations data.")
        print(error)

    integrations = ''
    try:
        integrations = requests.get(integrations_url, headers=HEADERS)
        integrations.raise_for_status()
        integrations = json.loads(integrations.text)
        print('\033[1mIntegrations\033[0m')
        for integration in integrations:
            print(f'    {integration["name"]} | {integration["id"]} | {integration["domainName"]}')
    except requests.exceptions.HTTPError as error:
        print("Error: Could not get integrations data.")
        print(error)


def get_projects():
    """
    Fetches all projects associated with the supplied auth token.

    Returns:
        dict: Contains project slug-ID pairs in alphabetical order by name.

    Raises:
        HTTPError: If unprocessable data is returned from the API.
    """

    url = f'{BASE_URL}/projects/'
    response = []
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        # exit the program as no operations can be performed
        print('Error: Could not get projects.')
        print(error)
        print('Exiting...')
        exit()
    response = json.loads(response.text)
    projects = {}
    for project in response:
        projects[project.get('slug')] = project.get('id')
    return collections.OrderedDict(sorted(projects.items()))


def print_projects(projects):
    """
    Prints projects' details to stdout.

    Args:
        projects (dict): Contains project slug-ID pairs.
    """

    for slug, _ in projects.items():
        print(slug)


def add_alerts(alerts, projects):
    """
    Adds all alerts specified in the alerts arg to all the projects specified
    in the projects arg.

    Prints request details to stdout.

    Args:
        alerts (list): Contains JSON alert payloads.
        projects: (dict): Contains project slug-ID pairs.
    """

    for project_slug, _ in projects.items():
        url = f'{BASE_URL}/projects/{ORGANIZATION}/{project_slug}/rules/'
        for alert in alerts:
            response = requests.post(url, json=alert, headers=HEADERS)
            print_response('Add', alert['name'], project_slug, response)


def get_remote_alerts(project_id):
    """
    Fetches all the alerts for the project associated with the project_id arg.

    Returns:
        dict: Contains alert ID-name pairs for the project with ID project_id.

    Args:
        project_id (str): An ID of a single project.

    Raises:
        HTTPError: If unprocessable data is returned from the API.
    """

    url = f'{BASE_URL}/organizations/{ORGANIZATION}/combined-rules/?project={project_id}'
    response = []
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print('Error: Could not get alert ids.')
        print(error)
    response = json.loads(response.text)
    remote_alerts = {}
    for alert in response:
        remote_alerts[alert.get('id')] = alert.get('name')
    return remote_alerts


def remove_alerts(projects):
    """
    Removes all alerts from all the projects specified in the projects arg.
    Prints requests' details to stdout.

    Args:
        projects (dict): A dictionary of project slug-ID pairs.
    """

    for project_slug, id in projects.items():
        remote_alerts = get_remote_alerts(id)
        for alert_id in remote_alerts:
            url = f'{BASE_URL}/projects/{ORGANIZATION}/{project_slug}/rules/{alert_id}/'
            response = requests.delete(url, headers=HEADERS)
            print_response('Remove', remote_alerts[alert_id], project_slug,
                           response)


def print_response(intention, alert_name, project_slug, response):
    """
    Prints a user friendly message about the details of an HTTP request.

    Args:
        intention (str): What was the requests intention.
        alert_name (str): The name of the alert.
        project_slug (str): The project being operated on.
        response (requests.models.Response): The response object of the
        request.
    """

    response_message = ''
    if response.ok:
        # in green
        response_message = f'\033[1;32;40m{response.status_code}\033[0m'
    else:
        # in red
        response_message = f'\033[1;31;40m{response.status_code}\033[0m'

    print(f'{intention} | {alert_name} | {project_slug} | {response_message}')


def print_help_menu():
    """
    Prints a help menu about this scripts features and how to use them.
    """

    print('\033[1mSYNOPSIS\033[0m')
    print('    \033[1mping\033[0m    Fetches data that is associated with the supplied AUTH_TOKEN.')
    print('            Use it to lookup values if you want to use env\'s in your template.')
    print()
    print('    \033[1madd [PROJECT_NAME|*]\033[0m')
    print('            Adds the alert config to the project with name PROJECT_NAME.')
    print('            Use * to add the config to all projects.')
    print()
    print('    \033[1mremove [PROJECT_NAME|*]\033[0m')
    print('            Removes all the alerts from the project with name PROJECT_NAME.')
    print('            Use * to remove alerts from  all projects.')
    print()
    print('    \033[1mlist\033[0m    List projects in name-id pairs.')
    print('    \033[1mhelp\033[0m    Print this help menu.')
    print('    \033[1mexit\033[0m    Kill this script.')


if __name__ == '__main__':
    alerts = load_template('./alerts.json')
    projects = get_projects()
    while True:
        print('> ', end='')
        command = input()
        if len(command.split()) == 2:
            command, arg = command.split()
            if command == 'add':
                if arg == '*':
                    add_alerts(alerts, projects)
                else:
                    try:
                        add_alerts(alerts, {arg: projects[arg]})
                    except Exception:
                        # catch typo errors in project name input
                        # do nothing
                        pass
            elif command == 'remove':
                if arg == '*':
                    remove_alerts(projects)
                else:
                    try:
                        remove_alerts({arg: projects[arg]})
                    except Exception:
                        # catch typo errors in project name input
                        # do nothing
                        pass
        if command == 'help':
            print_help_menu()
        elif command == 'list':
            print_projects(projects)
        elif command == 'ping':
            ping()
        elif command == 'exit':
            exit()
