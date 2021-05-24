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

#### Embedded SQL support

You can access embedded sql with: `sql = nimbella.esql()`

Available methods are:

> `sql.exec(sql, *arg)` 

Excecute an `sql` statement. The statement is either a string in [SQL](https://sqlite.org/lang.html) or an id returned by `sql.prep` (a prepared statement). 

You can also pass multiple additional `args`, for parametric statementns.

It returns an array of `[lastId, changedRows]`

Values are significant where relevant (for insert or delete, but not for create for example).

Example:

```
# single statement
res = sql.exec("create table t(i int)")
# parametric statement
res = sql.exec("insert into t(i) values(?),(?),(?)",1,2,3)
# returns [3,3]
```

> `sql.map(sql, *args [,limit=<n>])`

Execute an `sql` statement. The statement is either a string in [SQL](https://sqlite.org/lang.html) or an id returned by `sql.prep` (a prepared statement). 

You can also pass multiple additional `args`, for parametric statementns.

It returns the result of an SQL query (like a `SELECT`) as an an array of dictionaries. Each dictionary is a record, where the keys are the fields and the values are the field values.

The optional keyword argument is the maximum number of records returned, it will limit the size of the returned array to the first `<n>`


Examples:

```
sql.map("select * from t")
# returns [{"i":1},{"i":2},{"i":3}]
sql.map("select * from t where i >?",1)
# returns [{"i":2},{"i":3}]
sql.map("select * from t where i >?",1,limit=1)
# returns [{"i":2}]
```

> `sql.arr(sql, *args [,limit=<n>])`

Execute an `sql` statement. The statement is either a string in [SQL](https://sqlite.org/lang.html) or an id returned by `sql.prep` (a prepared statement). 

You can also pass multiple additional `args`, for parametric statements.

It returns the result of an SQL query (like a `SELECT`) as an an array of arrays. Each array includes the field values of a record.

The optional keyword argument is the maximum number of records returned, it will limit the size of the returned array to the first `<n>`

Examples:

```
sql.map("select * from t")
# returns [[1],[2],[3]]
sql.map("select * from t where i >?",1)
# returns [[2],[3]]
sql.map("select * from t where i >?",1,limit=1)
# returns [[2]]
```

> `prep(sql)`


You can prepare statements to save time from precompiling.

```
ins =  sql.prep("insert into t(i) values(?)")
sel = sql.prep("select * from t where i>?")
```

The returned value is a number and can be used to execute the statement with `exec`, `map` and `arr`.

```
# executing statement
res = sql.exec(ins,1)
# executing query
m = sql.map(sel,1,limit=1)
```

When you do not need any more you can close the statement running prep again with the returned value.

```
# closing prepared statements
sql.prep(ins)
sql.prep(sel)
```

Note that you can prepare up to 10000 statement at the same time without closing them, otherwise you will get an error `too many prepared statement`. In the unfortunate accident you fill the prepared statement cache, you can clear it with `prep("clean_prep_cache")`

## Support

We're always happy to help you with any issues you encounter. You may want to [join our Slack community](https://nimbella-community.slack.com/) to engage with us for a more rapid response.

## License

Apache-2.0. See [LICENSE](LICENSE) to learn more.
