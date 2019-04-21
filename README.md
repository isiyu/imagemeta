# imagemeta
python cli that outputs metadata of images on Google Cloud Storage as json

## Getting started
### Prerequisites
Requires: python3, docker, pip3, venv

### Running Script using Docker
Docker image is hosted at: https://cloud.docker.com/repository/docker/isiyu/imagemeta/general

*note this repo is missing the client secret needed to authenticate

##### Launching Docker with interactive shell
1. Pull the latest docker image :
`docker pull isiyu/imagemeta:03`
2. Run Docker image with interactive shell. This command mounts the /app/out directory to your local current dir outside of the Docker instance:
`docker run -it -v $(pwd):/app/out --rm isiyu/imagemeta:03 /bin/bash`

##### Authenticating
The first time running `imagemeta` in the interactive Docker shell, you'll be prompted to authenticate the app. Copy+paste the URL into a browser and login to a valid Google account to get the authorization code. You will have access to all buckets and objects assocaited with that Google account.
```
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?...access_type=offline
Enter the authorization code:
```
This process will need to be repeated when the token expires or when the Docker image is restarted

##### Running
```
usage: imagemeta [-h] [--bucket BUCKET] [--file FILE] [--write WRITE]
cli that outputs metadata of images onGoogle Cloud Storage as json

optional arguments:
  -h, --help       show this help message and exit
  --bucket BUCKET  Get metadata for all files in given bucket
  --file FILE      Get metadata given file path including bucket
                    ex. /my-bucket/image.jpg
  --write WRITE    write meta data json to file
```

example commands:
```
imagemeta --file /siyusong/greece.jpg
```
 - will print the metadata of in the shell
```
imagemeta --bucket my-bucket --write out/my_images_meta.json
```
 - acquires metadata of all the images in the bucket and writes to the output json file "out/my_images_meta.json"

##### Tests
Tests and mock responses are located in the /test directory and can be run with this command

```
 python -m unittest test.test_imageMetaLib
```

## Deploying To Production

### Code refactor
The authentication method needs to be refactored to use the server to server method outlined [here](https://cloud.google.com/docs/authentication/production#auth-cloud-implicit-python). The main steps would be to create a service account that has access to the buckets where the incoming images are located, use those credentials in the Docker/deploy step.

The current implmentation uses OAuth 2.0 associated with a Google user account - to give access to all buckets and files a given user has permissions for.

### Message Queue and Stack

Assuming the cloud storage and compute instances run on the same Google Cloud project/account - we can create an autoscaling stack that will run `imagemeta` on individual images that come into the stream.

Using Google Cloud's Pub/Sub service, set the Google Cloud bucket to append messages to the queue when the bucket is updated. Per -  https://cloud.google.com/storage/docs/pubsub-notifications

The worker instances consume messages from the stack. Each message corresponds with one object. The worker will run `imagemeta` and write the resulting json to the given data store.
In instances of worker failure, include logic in the worker stack to only acknowledge message after metadata from the image has been written to the document store, if there is a failure, the message will time out and be requeued.

### Throughput and load
We can autoscale the worker stack based on size of the message queue. Minimum number of workers can also be raised in anticipation of high volume.

##### Bottlenecks
The main bottlenecks are file transfers from Google Cloud, pup/sub, write limits of the data store.

Size of stack - In situations of high volume we can scale the number of worker instances. In theory this could be increased arbitrarily, in practice the max will be based on provisioning with the vendor.

File transfers - running the script on a local machine, the transfer of the images is the bottle neck. Assuming the compute cluster and the storage are in the same data center, there should be enough throughput. However, there can be bottlenecks if the number of workers are scaled high, and images are stored on the same physical machine, you could max out the read throughput of the machine the images are located on.

Datastore Write limits - if there are too many workers, it could max the write throughput of the datastore. In this case, if the JSON is not able to be written to the data store, the job would need to be failed, and message requeued.

##### Failover and Recovery
If we need to failover because of increased load, we stop sending messages from buckets until workers have reduced the size of the queue.
Assuming we have not dropped messages because of queue capacity - we can begin queueing messages for images uploaded after the newest processed image, and reconnect bucket notifiations.
Pub/Sub limits: https://cloud.google.com/pubsub/quotas#resource_limits

### Other considerations
##### Google Cloud Functions
Since this service wouldn't require state and is a fairly uncomplicated operation, using Google Cloud Functions instead of starting a compute stack was considered. The advantage being not having to manage a stack. Limits for that service are listed [here](https://cloud.google.com/functions/quotas#scalability) - since it is a managed service, there is less control during heavy load.
