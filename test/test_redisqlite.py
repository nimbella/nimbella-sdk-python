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

import unittest
import os
import nimbella

class TestRedisqlite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['__NIM_REDIS_IP'] = '127.0.0.1'
        os.environ['__NIM_REDIS_PASSWORD'] = 'password'
        os.system("docker run -d --name redisqlite --rm -p 6379:6379 sciabarracom/redisqlite:v1.0.4 --requirepass password >/dev/null")

    @classmethod
    def tearDownClass(cls):
        os.system("docker kill redisqlite >/dev/null")

    def setUp(self):
        self.sql = nimbella.esql()
        try: 
            self.sql.exec("drop table t")
        except:            
            pass

    def test_basic(self):
        res = self.sql.exec("create table t(i int)")
        self.assertEqual(len(res),2)

        ins = self.sql.exec("insert into t(i) values(1),(2),(3)")
        self.assertEqual(ins, [3,3])
    
        m = self.sql.map("select * from t")
        self.assertEqual(m, [{"i":1},{"i":2},{"i":3}])
 
        m1 = self.sql.map("select * from t", limit=1)
        self.assertEqual(m1, [{"i":1}])

        m2 = self.sql.map("select * from t", limit=2)
        self.assertEqual(m2, [{"i":1},{"i":2}])

        a = self.sql.arr("select * from t")
        self.assertEqual(a, [[1],[2],[3]])

        a1 = self.sql.arr("select * from t", limit=1)
        self.assertEqual(a1,[[1]])

        a2 = self.sql.arr("select * from t", limit=2)
        self.assertEqual(a2, [[1],[2]])

    def test_with_args(self):
        sql = self.sql
        assertEqual = self.assertEqual
        res =  sql.exec("create table t(i int)")
        assertEqual(len(res), 2)
        
        ins = sql.exec("insert into t(i) values(?),(?),(?)",1,2,3)
        assertEqual(ins,[3,3])
        
        m = sql.map("select * from t where i>?",1)
        assertEqual(m,[{"i":2},{"i":3}])

        m1 = sql.map("select * from t where i>?",1,limit=1)
        assertEqual(m1,[{"i":2}])

        a = sql.arr("select * from t where i<?",3)
        assertEqual(a,[[1],[2]])

        a1 = sql.arr("select * from t where i<?",3,limit=1)
        assertEqual(a1,[[1]])

    def test_prepared(self):
        sql = self.sql
        expect = self.assertEqual

        sql.exec("create table t(i int, s varchar)")

        sel = sql.prep("select s from t where i <?")
        expect(type(sel), int)

        ins = sql.prep("insert into t(i, s) values(?,?)")
        expect(type(ins), int)

        sql.exec(ins, 1, 'a')
        sql.exec(ins, 2, 'b')
        sql.exec(ins, 3, 'c')

        m = sql.map(sel, 3)
        expect(m, [ { 's': 'a' }, { 's': 'b' } ])

        a  = sql.arr(sel, 3, limit=1)
        expect(a, [ [ 'a' ] ])

        ok = sql.prep(sel)
        expect(ok, b'OK')
        sql.prep(ins)

        with self.assertRaises(Exception) as ctx:
            sql.prep(sel)
        expect(str(ctx.exception), 'invalid prepared statement index')
 
    def test_errors(self):
        with self.assertRaises(Exception) as ctx:
            self.sql.exec('xxx')
        self.assertEqual(str(ctx.exception), 'near "xxx": syntax error')
        with self.assertRaises(Exception) as ctx:
            self.sql.prep('xxx')
        self.assertEqual(str(ctx.exception), 'near "xxx": syntax error')
        with self.assertRaises(Exception) as ctx:
            self.sql.map('xxx')
        self.assertEqual(str(ctx.exception), 'near "xxx": syntax error')
        with self.assertRaises(Exception) as ctx:
            self.sql.arr('xxx')
        self.assertEqual(str(ctx.exception), 'near "xxx": syntax error')
