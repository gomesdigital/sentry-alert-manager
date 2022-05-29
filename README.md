# sentry-alert-manager

![](https://img.shields.io/github/issues/gomesdigital/sentry-alert-manager?color=yellow)
![](https://img.shields.io/github/languages/code-size/gomesdigital/sentry-alert-manager?color=green)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://github.com/gomesdigital/gomesdigital/LICENSE)

[Sentry](https://sentry.io) doesn't support editing alerts in bulk from the GUI or open API. This tool is built from their private API - reverse engineered - so you can:

1. Edit alerts for multiple projects at the same time.
2. Version control alert configurations.
3. Ensure alert configurations are consistent across projects.

## Getting Started

### Prerequisites

* Python 3.6+

### Setup
1. Clone this repo:
   ```
   git clone https://github.com/gomesdigital/sentry-alert-manager.git
   cd sentry-alert-manager
   ```
   
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a ```.env``` file to store your environment variables:
   ```
   cat .env.example >> .env
   ```
   
4. Create an auth token in Sentry - https://sentry.io/settings/account/api/auth-tokens/.

   You'll need to attatch these permissions:
   * org:read 
   * project:read 
   * alerts:write   
    
5. Assign your auth token from Sentry to the ```AUTH_TOKEN``` variable in the ```.env``` file.

6. Fetch the rest of your ```env's``` by running:
   ```
   python3 main.py
   ```
   and then using the ```ping``` command:
   ```
   > ping
   ```
   If your setup is correct, you should see more information being output. 
   
   You can use this command to discover information about your organization so you can use it in your payloads. The ```AUTH_TOKEN``` and ```ORGANIZATION``` environment variables **are required** at a minimum. 

     \- see the [Features](#features) section for more on commands.
   
## Demo

https://user-images.githubusercontent.com/69418528/166883386-cd724d03-7780-4b7c-9be1-edf1f60ecb63.mp4


## Payloads
To create alerts you must define them in the ```alerts.json``` file. This contains an array of _alert payloads_. You can add as many as you need, environment variables are optional. 
```
# alerts.json

{
  "alerts": [
    {
      "actionMatch": "all",
      "filterMatch": "all",
      "actions": [
        {
          "workspace": "$SLACK_WORKSPACE_ID",
          "id": "sentry.integrations.slack.notify_action.SlackNotifyServiceAction",
          "channel": "$SLACK_CHANNEL_NAME"
        }
      ],
      "conditions": [
        {
          "id": "sentry.rules.conditions.first_seen_event.FirstSeenEventCondition"
        }
      ],
      "filters": [
        {
          "level": "40",
          "match": "gte",
          "id": "sentry.rules.filters.level.LevelFilter"
        }
      ],
      "name": "A new error occurred...",
      "frequency": "1440",
      "owner": "$OWNER"
    },
    {
      # another alert
    },
    {
      # another alert
    }
  ]
}
```

You can edit this file in-place to adjust your alerts, but the easiest way to build one is by using the GUI - click _**Save Rule**_ , then drag and drop the payload from Sentry to the ```alerts.json``` file.

## Features
```
SYNOPSIS
    ping    Fetches data that is associated with the supplied AUTH_TOKEN.
            Use it to lookup values if you want to use env's in your template.
            
    add [PROJECT_NAME|*]
            Adds the alert config to the project with name PROJECT_NAME.
            Use * to add the config to all projects.

    remove [PROJECT_NAME|*]
            Removes all the alerts from the project with name PROJECT_NAME.
            Use * to remove alerts from  all projects.

    list    List project names.
    help    Print this help menu.
    exit    Kill this script.
```

## Help
See the synopsis in the [Features](#features) section above.

Open an issue if you need help with anything else!

## Contributing

Please read the [CONTRIBUTING](CONTRIBUTING.md) file for details on code of conduct, and the process for submitting pull requests.

There is a Postman collection inlcuded in the repo if you'd like to inspect the endpoints.

## License

This project is licensed under the GNU General Public License v2.0. See the [LICENSE](LICENSE) file for details.

## Author Info

* **Daniel Gomes-Sebastiao** - *Initial work* - [gomesdigital](https://github.com/gomesdigital)

See also the list of [contributors](https://github.com/gomesdigital/sentry-alert-manager/graphs/contributors) who participated in this project.

## Acknowledgements

I've been managing a large Sentry organization for work. It is important for the dev team to be notified about the errors that matter and to not be spammed by the ones that don't. Achieving that is a gradual process though, and it takes a lot of fine tuning.

I designed this tool so we can:

1. Track our alert configurations in templates.
2. Make it faster to adjust which errors the dev team will hear about.
3. Ensure the alert configurations are consistent across projects.
