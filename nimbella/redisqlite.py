import json


def _decode(a):
    return [ json.loads(x.decode('utf-8')) for x in a]

class Redisqlite:
    def __init__(self, redis):
        self.redis = redis
    
    def exec(self, *sql):
        return self.redis.execute_command("SQLEXEC", *sql)

    def prep(self, sql):
        return self.redis.execute_command("SQLPREP", sql)

    def map(self, *args, **kwargs):
        limit = kwargs.get("limit",0)
        return _decode(self.redis.execute_command("SQLMAP", limit, *args))

    def arr(self, *args, **kwargs):
        limit = kwargs.get("limit",0)
        return _decode(self.redis.execute_command("SQLARR", limit, *args))
