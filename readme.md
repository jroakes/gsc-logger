# GSC Logger: A Tool To Log GSC Data to BigQuery
Google App Engine provides a Cron service for logging daily Google Search Console (GSC) data to BigQuery for use in
Google Data Studio or for separate analysis beyond 3 months.

## Configuration

This script runs daily and pulls data as specified in config.py file to BigQuery.  There is little to configure without some programming experience.  
Generally, this script is designed to be a set-it-and-forget-it in that once deployed to app engine, you should be able to add your service account
email as a full user to any GSC project and the data will be logged daily to BigQuery.  By default the data is set to pull from GSC 7 days earler every day 
to ensure the data is available.

* **Note: This script should be deployed on the Google Account with access to your GSC data to ensure it is available to Google Data Studio**
* **Note: This script has not been widely tested and is considered a POC.  Use at your own risk!!!**
* **Note: This script only works for Python 2.7 which is a restriction for GAE currently**

More installation details located [here](https://adaptpartners.com/technical-seo/a-tool-for-saving-google-search-console-data-to-bigquery/). 
Developed by [Technical SEO Agency, Adapt Partners](https://adaptpartners.com)

## Deploying
The overview for configuring and running this sample is as follows:

### 1. Prerequisites

* If you don’t already have one, create a
    [Google Account](https://accounts.google.com/SignUp).

* Create a Developers Console project.
    1. Install (or check that you have previously installed)
        * [`git`](https://git-scm.com/downloads)
        * [Python 2.7](https://www.python.org/download/releases/2.7/)
        * [Python `pip`](https://pip.pypa.io/en/latest/installing.html)
        * [Google Cloud SDK](http://cloud.google.com/sdk/)
    2. [Enable the BigQuery API](https://console.cloud.google.com/apis/api/bigquery-json.googleapis.com/overview)
    3. [Enable the GSC API](https://console.cloud.google.com/apis/api/webmasters.googleapis.com/overview)
    4. [Enable Project Billing](https://support.google.com/cloud/answer/6293499#enable-billing)


### 2. Clone this repository

To clone the GitHub repository to your computer, run the following command:

    $ git clone https://github.com/jroakes/gsc-logger.git

Change directories to the `gsc-logger` directory. The exact path
depends on where you placed the directory when you cloned the sample files from
GitHub.

    $ cd gsc-logger


### 3. Create a Service Account

1. Go to https://console.cloud.google.com/projectselector/iam-admin/serviceaccounts and create a Service Account in your project.
2. Download the json file.
3. Upload replacing the file in the `credentials` directory.


### 4. Deploy to App Engine

1. Configure the `gcloud` command-line tool to use the project your Firebase project.
```
$ gcloud config set project <your-project-id>
```
2. Change directory to `appengine/`
```
$ cd appengine/
```
3. Install the Python dependencies
```
$ pip install -t lib -r requirements.txt
```
4. Create an App Engine App
```
$ gcloud app create
```
5. Deploy the application to App Engine.
```
$ gcloud app deploy app.yaml \cron.yaml \index.yaml
```

### 4. Verify your Cron Job
Go to the [Task Queue](https://console.cloud.google.com/appengine/taskqueues) tab in AppEngine and
click on **Cron Jobs** to verify that the daily cron is set up correctly. The job should have a **Run Now** button next to it.

### 4. Verify App
Once deployed, you should be able to load your GAE deployment url in a browser and see a screen that lists your service account email and also attached GSC sites.  This screen will also list the last cron save date for each site
that you have access to.

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
