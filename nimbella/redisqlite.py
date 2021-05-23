"""
/**
 * Copyright (c) 2020-present, Nimbella, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
"""

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
