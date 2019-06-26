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

The logged-in user is currently hard-coded ('guest@example.com') in the client settings,
but jobs are tagged - multiple users are supported. Only the relevant data is
displayed to the logged-in user.

When uploading to S3, the files are tagged with metadata which is captured in the jobs table.

Files:
```
  client/index.html
  client/script.js
  client/style.css
  client/serve.sh
```

### S3

S3 uses one bucket (`ginkgo-search`), with top-level folders for each environment (`prd`, `dev`, `bob`, etc.)

Within each environment, there are two folders:
```
  {s3}/{env}/inbox    # for transient incoming files. Permissions are globally writable, not readable.
  {s3}/{env}/queries  # incoming files are validated, normalized, and placed here for processing
```
In addition, `{s3}/prd/artifacts/functions.zip` is the deploy package for the lambdas.

### DynamoDB

There is one table in Dynamo holding all jobs. The fields are:

```
   guid         # primary key
   env          # production, or one of several developers
   start_time   # start of job
   email        # email of user who submitted job
   filename     # original filename (directory not included) of file submitted by user
   status       # one of: uploading, uploaded, done, error
   results      # list of dicts. Each describes either sequence matches or errors
```

The SAM local developer environments use the cloud-hosted DynamoDB instance for everything.
Since it's sharded by env and is NoSQL, the developers can coexist peacefully.

### SQS

When files arrive in S3, they are minimally processed and a message is queued on SQS for processing.

There is a separate SQS queue for each environment, with names `GinkgoSQS-prd`, `GinkgoSQS-dev`, etc.

`GinkgoSQS-prd` behaves specially. It only carries 'process' messages, issued after `bucket_watcher` runs.

All the other (developer) queues carry both `upload` and `process messages`. Since S3 has no path to trigger
the SAM local environment on uploads, `bucket_watcher` forwards `upload` events to the appropriate developer
queue, which eventually end up in that developer's SAM local environment for processing.

### Lambda

There are four Lambdas and one layer
The worker code is in the `processor` lambda.

Files:
```
   functions/bucket_watcher.py
   functions/processor.py
   functions/queries.py
   functions/dev_proxy.py
   functions/common.py       # shared code

```

#### bucket_watcher

`bucket_watcher` watches `{s3}/{env}/inbox` for incoming files. When a file is uploaded to S3:
 * the file is validated (trivially)
 * enter record in the database
 * move file to {s3}/{env}/queries folder
 * send message to SQS to notify workers

In addition, the `bucket_watcher` instance on `prd` will forward events to each developer's queue
so it can be handled by the developer's `bucket_watcher` instance.

#### processor

`processor` listens to the SQS queue for awaiting processing. When a message is received:
 * reference data is loaded (cached in memory, as far as lambda will allow) from the `biopython` layer.
 * the query is retrieved from {s3}/{env}/queries
 * search using biopython
 * record results in DynamoDB

#### queries

`queries` listens to http requests from API Gateway. Currently it's open to the public, no authentication.
A query is `GET /{env}/queries/{email}`, and returns a list of the database items for that user, including
the status and any results.


#### dev_proxy

`dev_proxy` is a cloud-based API endpoint lets the developer poll for pending messages in that
developer's queue.

#### biopython

The `biopython` layer contains large python libraries and a copy of the reference data files.
These are available to the lambda at runtime, they are mounted in `/opt/data` while the lambda runs.

The `build.sh` script for the layer is basically `pip install` plus `gzip`. You might think it's ok
to build this layer on your mac, but not so. Apparently there are binaries involved, and any error
messages you might see are quite deceptive. So you have to build the layer on a CentOS image
(or an authentic Amazon AMI).

## Install and configure

See [Install](install/readme.md)

