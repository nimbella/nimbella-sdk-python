# Nimbella SDK for Python

A Python package to interact with [`nimbella.com`](https://nimbella.com) services.

## Installation

```
pip install nimbella
```

## Usage

This SDK provides access to the following cloud services on Nimbella.com:

- [Redis](https://redis.io/)
- [Object Storage](https://en.wikipedia.org/wiki/Object_storage)

### Redis

The `nimbella.redis()` method returns a pre-configured Redis client for use in your application. See the [Redis client library documentation](https://pypi.org/project/redis/) for the methods provided.

```python
import nimbella

# Redis
redis = nimbella.redis()
redis.set("key", "value")
value = redis.get("key")
```

### Object Storage (GCP & S3)

The `nimbella.storage()` method returns a pre-configured object storage client. This client exposes a high-level storage API (details below) - which hides the underlying storage provider implementation. The storage client is automatically configured to use the storage service for the cloud it is running on - which is [GCS](https://cloud.google.com/storage/) on GCP and [S3 on AWS](https://aws.amazon.com/s3/).

```python
import nimbella

# Storage
bucket = nimbella.storage()
filename = "test.txt"
file = bucket.file(filename)
file.save('Expected %s contents' % filename, 'text/plain')
```

The `nimbella.storage()` constructor takes a single parameter `web` to determine whether the storage bucket is for a website (`nimbella.storage(web=True)`) or files (`nimbella.storage()`). Website buckets can be used for store web content (e.g. HTML & JS files) to host static websites.

#### Object Storage API

```python
# Storage API
class StorageProvider(web=False):    
    # External bucket URL
    @property
    def url() -> Union[str, None]:

    # Configure website for web storage buckets
    def setWebsite(mainPageSuffix, notFoundPage):

    # Remove all files from the bucket (using optional prefix)    
    def deleteFiles(force, prefix):

    # Upload new file from path to bucket destination.
    def upload(path, destination, contentType, cacheControl):

    # Return storage file instance from bucket
    def file(destination) -> StorageFile:

    # Return all storage files (with optional prefix) instance from bucket
    def getFiles(prefix) -> list:
      
# Storage File Class
class StorageFile():
    # Name of the bucket file
    @property
    def name() -> str:

    # key/value pairs for provider-specific object metadata
    @property
    def metadata() -> dict:

    # does file exist?
    def exists() -> bool:

    # delete file from bucket
    def delete() -> None:

    # update file contents from string or bytes with content-type
    def save(data: Union[str, bytes], contentType: str) -> None:

    # return file contents as bytes
    def download() -> bytes:

    # return pre-signed url from file for external access
    def signed_url(version: str, action: str, expires: int, contentType: str) -> str:
```

## Support

We're always happy to help you with any issues you encounter. You may want to [join our Slack community](https://nimbella-community.slack.com/) to engage with us for a more rapid response.

## License

Apache-2.0. See [LICENSE](LICENSE) to learn more.
