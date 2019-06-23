# DNA search

## Try it out

The client url is https://straz.github.io/dna_search/client/

## Components

### Client

The client is a simple static front end using just bootstrap and jquery.
For local development, run `serve.sh`

The client makes two API calls:
  * upload files to S3 (in `{s3}/inbox/`)
  * get status of current and pending jobs (from {api}/queries/{user})

The logged-in user is currently hard-coded ('guest@example.com') in the client,
but jobs are tagged so only the relevant data is displayed to the logged-in user.

When uploading to S3, the files are tagged with metadata which is captured in the jobs table.

Files:
```
  client/index.html
  client/script.js
  client/style.css
  client/serve.sh
```

### S3

There are three folders on S3:
```
  {s3}/inbox    # for transient incoming files. Permissions are globally writable, not readable.
  {s3}/queries  # incoming files are validated, normalized, and placed here for processing
  {s3}/data     # reference data pulled from NCBI for searching
```

The data folder is a convenient cache for large sequence files downloaded from NCBI. In practice
we don't really need/use it, because the `processor` lambda uses data cached in the `biopython`
lambda layer.

### DynamoDB

There is one table in Dynamo holding all jobs. The fields are:

```
   guid         # primary key
   start_time   # start of job
   email        # email of user who submitted job
   filename     # original filename (directory not included) of file submitted by user
   status       # one of: uploading, uploaded, done, error
   results      # list of dicts. Each describes either sequence matches or errors
```

### SQS

When files arrive in S3, they are minimally processed and a message is queued on SQS for processing.
The worker code is in the `processor` lambda.

### Lambda

There are three Lambdas and one layer

Files:
```
   lambdas/bucket_watcher/
   lambdas/processor/
   lambdas/queries/
   layers/biopython/
```

#### bucket_watcher

`bucket_watcher` watches `{s3}/inbox` for incoming files. When a file is uploaded to S3:
 * the file is validated (trivially)
 * enter record in the database
 * move file to /queries folder
 * send message to SQS to notify workers

#### processor

`processor` listens to the SQS queue for awaiting processing. When a message is received:
 * reference data is loaded (cached in memory, as far as lambda will allow) from the `biopython` layer.
 * the query is retrieved from {s3}/queries
 * search using biopython
 * record results in DynamoDB

#### queries

`queries` listens to http requests from API Gateway. Currently it's open to the public, no authentication.
A query is `GET /queries/{email}`, and returns a list of the database items for that user, including
the status and any results.

#### biopython

The `biopython` layer contains large python libraries and a copy of the reference data files.
These are available to the lambda at runtime, they are mounted in `/opt/data` while the lambda runs.

The `build.sh` script for the layer is basically `pip install` plus `gzip`. You might think it's ok
to build this layer on your mac, but not so. Apparently there are binaries involved, and any error
messages you might see are quite deceptive. So you have to build the layer on a CentOS image
(or an authentic Amazon AMI).

## Install and configure

One of the requirements in this exercise is that local dev install has to be a one-click script.
You can run `start.py` and it'll fire up a local AWS SAM environment (assumes you have docker).
The template file is not properly configured, so this won't do much good. 

I'm not sure I'll have the time it would take to tune the template, so this is mostly to give you
an impression of what a solution might look like.

Files:
```
  aws-template.yaml   # AWS cloud formation template (incomplete and inaccurate)
  start.py            # The one-click script (incomplete)
  layers/build.sh     # A one-click script to build the biopython layer with cached data (works fine)
```
