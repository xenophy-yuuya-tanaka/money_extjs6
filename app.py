#!/usr/bin/env python2
# coding: utf-8

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import cgitb
cgitb.enable()

from bottle import *
import datetime
import json
import time
import MySQLdb

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = ''
DB_NAME = 'money_mgr'

# {{{ class Connection(object)

class Connection(object):
    """
    DB操作のための規定クラス

    :statement _connector: 接続インスタンス
    """

    __instance = None

    def __init__(self, db=None, host=None, user=None, passwd=None, conf_cls=None):
        """
        初期化処理

        :params db: データベース名
        :params table: テーブル名
        :params host: ホスト名
        :params user: ユーザ名
        :params passwd: パスワード
        """
        """
        既に接続済みのインスタンスがある場合は流用
        ない場合はインスタンスを生成する
        """
        if Connection.__instance is None:
            """
            設定用クラス生成
            設定情報が足りてない場合は例外
            """
            if None in [host, user, passwd, db]:
                raise('database setting error')

            Connection.__instance = MySQLdb.connect(
                host=host,
                db=db,
                user=user,
                passwd=passwd,
                charset='utf8')

        super(Connection, self).__init__()

    @property
    def connector(self):
        """
        DB接続インスタンス
        """
        return Connection.__instance

    @property
    def cursor(self):
        """
        DB操作のためのカーソルオブジェクト取得処理
        """
        return Connection.__instance.cursor(MySQLdb.cursors.DictCursor)

    def close(self):
        """
        DB切断処理
        """
        Connection.__instance.close()

    def dump(self, dirname = 'backup'):
        """
        DBバックアップ処理
        """

        dirpath = os.path.dirname(os.path.abspath(__file__))
        path = fullpath = '{0}/{1}'.format(dirpath, dirname)

        if not os.path.isdir(fullpath):
            os.makedirs(fullpath)

        cursor = Connection.__instance.cursor()
        cursor.execute("SHOW TABLES")
        data = ""
        tables = []
        for table in cursor.fetchall():
            tables.append(table[0])

        for table in tables:
            data += "DROP TABLE IF EXISTS `" + str(table) + "`;"
            cursor.execute("SHOW CREATE TABLE `" + str(table) + "`;")
            data += "\n" + str(cursor.fetchone()[1]) + ";\n\n"

            cursor.execute("SELECT * FROM `" + str(table) + "`;")
            for row in cursor.fetchall():
                data += "INSERT INTO `" + str(table) + "` VALUES("
                first = True
                for field in row:
                    if not first:
                        data += ', '
                    data += '"' + u"%s" % field  + '"'
                    first = False
                data += ");\n"
            data += "\n\n"

        now = datetime.datetime.now()
        filename = '{0}{1}{2}.sql'.format(
                str(path),
                "/backup_",
                now.strftime("%Y-%m-%d_%H:%M"))
        dumpf = open(filename, 'w')
        dumpf.writelines(data.encode('utf8'))
        dumpf.close()

# }}}
# {{{ class Model(Connection)

class Model(Connection):
    """
    DB接続を行うクラスの規定クラス

    :statement use_table: クラス内で利用するテーブル名
    :statement primary_key: 対象テーブルのプライマリキー
    :statement schema: 対象テーブルのスキーマ
    """

    use_table = None

    primary_key = 'id'

    schema = None

    def __init__(self, db=None, table=None, host=None, user=None, passwd=None):
        """
        初期化処理

        :params db: データベース名
        :params table: テーブル名
        :params host: ホスト名
        :params user: ユーザ名
        :params passwd: パスワード
        """
        """ 利用テーブル設定 """
        if table is not None:
            self.use_table = table
        """ DB接続インスタンス初期化 """
        super(Model, self).__init__(db, host, user, passwd)

    def get_rows_count(self):
        """
        レコード数取得

        :return レコードのトータル数
        """
        ret = self._select(fields=('count(*) as count',))
        return (lambda v: v[0]['count'] if len(v) else 0)(ret)

    def get_rows_all(self, table=None, fields=('*',)):
        """
        対象テーブルのレコード全取得

        :params table: 対象テーブル名

        :return レコードのdict配列
        """
        if table is None:
            table = self.use_table

        return self._select(table, fields)

    def get_rows(self, table=None, fields=('*',), wheres=((),()), start=None, limit=None):
        """
        指定条件でレコード取得

        :params table: テーブル名
        :params fields: 検索対象フィールドを格納したtuple
        :params wheres: ((対象キーおよび接続句),(対象キーの対になる値))
        :params start: 開始値
        :params limit: リミット値
        """
        if table is None:
            table = self.use_table

        return self._select(table, fields, wheres, start, limit)

    def get_row_by_primary_key(self, value, table=None, key=None):
        """
        プロパティに指定されているプライマリキーで
        単一レコードの取得処理

        :params value: 対象のプライマリキー値
        :params table: 対象テーブル名
        :params key: 対象プライマリキー

        :return 取得したレコードのdict
        """
        if key is None:
            key = self.primary_key
        if table is None:
            table = self.use_table
        ret = self._select(table=table,wheres=((key,),(value,)))
        return (lambda v: v[0] if len(v) else None)(ret)

    def add_rows(self, fields=None, values=()):
        """
        外部から実行されるレコード追加IF

        :params fields: 挿入対象のフィールド名
                設定されていない場合はクラスプロパティに設定されている
                スキーマを利用する
        :params values: 挿入対象のフィールド値
                複数レコード挿入の場合は((x,x),(x,x))
        """
        if fields is None:
            fields = self.schema

        self._insert(fields=fields,values=values)

    def update_row(self, value, table=None, fields=None, values=()):
        """
        外部から実行されるレコード更新IF

        :params value: 対象レコード識別値
        :params table: 対象テーブル名
        :params fields: 挿入対象のフィールド名
                設定されていない場合はクラスプロパティに設定されている
                スキーマを利用する
        :params values: 挿入対象のフィールド値
                複数レコード挿入の場合は((x,x),(x,x))
        """
        # TODO: 要調整
        if fields is None:
            fields = self.schema

        self._update(value, table, fields, values)

    def delete_row(self, value, table=None, logic=True, del_key='state'):
        """
        引数にテーブル名が設定されていない場合は
        クラスに設定されているプロパティをデフォ値として利用

        :params value: 削除対象レコード対象キー
        :params table: 対象テーブル名
        :params logic: 論理削除フラグ
        :params del_key: 論理削除時の対象フィールド名
        """
        if not table:
            table = self.use_table

        self._delete(value, table, logic, del_key)

    def _select(self, table=None, fields=('*',), wheres=((),()), start=None, limit=None):
        """
        レコード取得処理

        :params table: テーブル名
        :params fields: 検索対象フィールドを格納したtuple
        :params wheres: ((対象キーおよび接続句),(対象キーの対になる値))
        :params start: 開始値
        :params limit: リミット値

        :return 取得したレコードのdict配列
        """
        """ 操作用カーソルインスタンス取得 """
        cursor = self.cursor
        """ WHERE句のリソース """
        where_keys = wheres[0]
        where_vals = wheres[1]
        """
        引数にテーブル名が設定されていない場合は
        クラスに設定されているプロパティをデフォ値として利用
        """
        if not table:
            table = self.use_table
        """ 取得対象フィールド結合 """
        fields = ','.join(fields)
        """ SQL文生成 """
        sql = 'SELECT {0} FROM {1}'.format(fields, table)
        """
        WHERE句が設定されている場合はSQL文を拡張
        """
        # TODO: WHERE句の生成処理は要調整
        if len(where_keys) > 0:
            where_sql = 'WHERE'
            for k in where_keys:
                if k[:1] is '_' and k[-1:] is '_':
                    where_sql = '{0} {1}'.format(where_sql, k[1:-1])
                else:
                    where_sql = '{0} {1}=%s'.format(where_sql, k)
            sql = '{0} {1}'.format(sql, where_sql)
        """
        LIMITが設定されている場合はSQL文を拡張
        LIMITのみ設定されている場合は、STARTを0に設定
        """
        if limit is not None and limit is not 0:
            if start is None:
                start = 0
            sql = '{0} LIMIT {1}, {2}'.format(sql, start, limit)
        """ SQL発行 """
        if len(where_vals) > 0:
            cursor.execute(sql, where_vals)
        else:
            cursor.execute(sql)
        """ レコード取得 """
        return cursor.fetchall()

    def _insert(self, table=None, fields=(), values=()):
        """
        レコード追加処理

        :params table: テーブル名
        :params fields: 挿入対象のフィールド名
        :params values: 挿入対象のフィールド値
                複数レコード挿入の場合は((x,x),(x,x))
        """
        """ 操作用カーソルインスタンス取得 """
        cursor = self.cursor
        """ 複数レコードかどうか """
        is_multiple = type(values[0]) is tuple
        """
        引数にテーブル名が設定されていない場合は
        クラスに設定されているプロパティをデフォ値として利用
        """
        if not table:
            table = self.use_table
        """ 取得対象フィールド結合 """
        fields = ','.join(fields)
        """ 最終的にSQLに埋め込む更新値 """
        all_values = values
        """ SQL文生成 """
        sql = 'INSERT INTO {0} ({1}) VALUES'.format(table, fields)
        if is_multiple:
            sql = '{0} {1}'.format(sql,('({0}),'*len(values))[:-1].format(('%s,'*len(values[0]))[:-1]))
            all_values = values[:1][0]
            for value in values[1:]: all_values = all_values + value
        else:
            sql = '{0} ({1})'.format(sql, ('%s,'*len(values))[:-1])
        """ SQL発行 """
        try:
            cursor.execute(sql, all_values)
            self.connector.commit()
        except Exception as e:
            print e
            print sql
            self.connector.rollback()
            sys.exit(1)

    def _update(self, value, table=None, fields=(), values=()):
        """
        レコード更新処理

        :params table: テーブル名
        :params value: 対象レコードの識別値
        :params fields: 挿入対象のフィールド名
        :params values: 挿入対象のフィールド値
        """
        """ 操作用カーソルインスタンス取得 """
        cursor = self.cursor
        """
        引数にテーブル名が設定されていない場合は
        クラスに設定されているプロパティをデフォ値として利用
        """
        if not table:
            table = self.use_table
        """ SQL文生成 """
        sql = 'UPDATE {0} SET {2} WHERE {1}=%s'.format(
                table,
                self.primary_key,
                ','.join(['{0}=%s'.format(f) for f in fields]))
        """ SQL発行 """
        try:
            cursor.execute(sql, values+(value,))
            self.connector.commit()
        except Exception as e:
            print e
            print sql
            self.connector.rollback()
            sys.exit(1)

    def _delete(self, value, table=None, logic=True, del_key='state'):
        """
        レコード削除処理

        :params table: テーブル名
        :params value: 対象レコードの識別値
        :params logic: 論理削除フラグ
        :params del_key: 論理削除時の対象フィールド
        """
        # TODO: 論理削除処理実装
        """ 操作用カーソルインスタンス取得 """
        cursor = self.cursor
        """ SQL文生成 """
        sql = 'DELETE FROM {0} WHERE {1}=%s'.format(table, self.primary_key)
        """ SQL発行 """
        try:
            cursor.execute(sql, (value,))
            self.connector.commit()
        except Exception as e:
            print e
            print sql
            self.connector.rollback()
            sys.exit(1)

# }}}
# {{{ class DateParser(json.JSONEncoder)

class DateParser(json.JSONEncoder):
    """
    DBから取得したデータをJSONに変換する際に
    datetimeのデータをintにキャストするための
    コンバート用クラス
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, obj)

# }}}
# {{{ payments_model

payments_model = Model(
    host=DB_HOST,
    table='tbl_payments',
    db=DB_NAME,
    user=DB_USER,
    passwd=DB_PASS
)
payments_model.primary_key = 'id'
payments_model.schema = (
    'name',
    'category_id',
    'price',
    'member_id',
    'creditcard_id',
    'date',
    'note',
    'created',
    'modified'
)

# }}}
# {{{ revenues_model

revenues_model = Model(
    host=DB_HOST,
    table='tbl_revenues',
    db=DB_NAME,
    user=DB_USER,
    passwd=DB_PASS
)
revenues_model.primary_key = 'id'
revenues_model.schema = (
    'name',
    'category_id',
    'price',
    'total_price',
    'member_id',
    'date',
    'note',
    'created',
    'modified'
)

# }}}
# {{{ categories_model

categories_model = Model(
    host=DB_HOST,
    table='tbl_categories',
    db=DB_NAME,
    user=DB_USER,
    passwd=DB_PASS
)
categories_model.primary_key = 'id'
categories_model.schema = (
    'name',
    'type',
    'fixed',
    'created',
    'modified'
)

# }}}
# {{{ members_model

members_model = Model(
    host=DB_HOST,
    table='tbl_members',
    db=DB_NAME,
    user=DB_USER,
    passwd=DB_PASS
)
members_model.primary_key = 'id'
members_model.schema = (
    'name',
    'created',
    'modified'
)

# }}}
# {{{ creditcards_model

creditcards_model = Model(
    host=DB_HOST,
    table='tbl_creditcards',
    db=DB_NAME,
    user=DB_USER,
    passwd=DB_PASS
)
creditcards_model.primary_key = 'id'
creditcards_model.schema = (
    'name',
    'cutoff',
    'debit',
    'member_id',
    'created',
    'modified'
)

# }}}
# {{{ クロスドメイン許可用処理

@hook('after_request')
def enable_corssdomain():
    response.set_header('Access-Control-Allow-Origin','*')
    response.set_header('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
    response.set_header('Access-Control-Allow-Headers', 'Origin, Accept, Content-Type, X-Requested-With')

# }}}
# {{{ 各APIレスポンスオブジェクト生成処理

def do_create_response(raw=None):
    rst = {
        'success': True,
        'total': len(raw),
        'data': raw
    }
    if not raw:
        rst['success'] = False

    response.content_type = 'application/json; charset=UTF8'

    return json.dumps(
        rst,
        cls = DateParser
    )

# }}}
# {{{ OPTIONS

@route('/api/:name/:pid', method='OPTIONS')
def options_all_api(name, pid):
    pass

# }}}
# {{{ 支出レコード生成処理

@route('/api/payments', method='POST')
def create_payments():
    payments_name = request.json.get('name')
    payments_category_id = request.json.get('category_id')
    payments_member_id = request.json.get('member_id')
    payments_creditcard_id = request.json.get('creditcard_id')
    payments_price = request.json.get('price')
    payments_date = request.json.get('date')
    payments_note = request.json.get('note')

    try:
        payments_model.add_rows(values=(
            payments_name,
            payments_category_id,
            payments_price,
            payments_member_id,
            payments_creditcard_id,
            payments_date,
            payments_note,
            datetime.datetime.now(),
            datetime.datetime.now()
        ))
        response = do_create_response([{
            'id'            : payments_model.connector.insert_id(),
            'name'          : payments_name,
            'category_id'   : payments_category_id,
            'price'         : payments_price,
            'member_id'     : payments_member_id,
            'creditcard_id' : payments_creditcard_id,
            'date'          : payments_date,
            'note'          : payments_note
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ 支出レコード更新処理

@route('/api/payments/:pid', method='PUT')
def update_payments(pid):
    payments_id = pid
    payments_name = request.json.get('name')
    payments_category_id = request.json.get('category_id')
    payments_price = request.json.get('price')
    payments_member_id = request.json.get('member_id')
    payments_creditcard_id = request.json.get('creditcard_id')
    payments_date = request.json.get('date')
    payments_note = request.json.get('note')

    try:
        payments_model.update_row(payments_id,
            fields=(
                'name',
                'category_id',
                'price',
                'member_id',
                'creditcard_id',
                'date',
                'note',
                'modified'
            ),
            values=(
                payments_name,
                payments_category_id,
                payments_price,
                payments_member_id,
                payments_creditcard_id,
                payments_date,
                payments_note,
                datetime.datetime.now()
            )
        )
        response = do_create_response([{
            'id'            : payments_id,
            'name'          : payments_name,
            'category_id'   : payments_category_id,
            'price'         : payments_price,
            'member_id'     : payments_member_id,
            'creditcard_id' : payments_creditcard_id,
            'date'          : payments_date,
            'note'          : payments_note
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ 支出レコード削除処理

@route('/api/payments/:pid', method='DELETE')
def delete_payments(pid):
    payments_id = pid

    try:
        payments_model.delete_row(payments_id,
            logic=False
        )
        response = do_create_response([{
            'id': payments_id
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ 支出レコード全取得

@route('/api/payments', method=['GET', 'OPTIONS'])
def get_payments():
    return do_create_response(payments_model.get_rows_all())

# }}}
# {{{ 収入レコード生成処理

@route('/api/revenues', method='POST')
def create_revenues():
    revenues_name = request.json.get('name')
    revenues_category_id = request.json.get('category_id')
    revenues_price = request.json.get('price')
    revenues_total_price = request.json.get('total_price')
    revenues_member_id = request.json.get('member_id')
    revenues_date = request.json.get('date')
    revenues_note = request.json.get('note')

    try:
        revenues_model.add_rows(values=(
            revenues_name,
            revenues_category_id,
            revenues_price,
            revenues_total_price,
            revenues_member_id,
            revenues_date,
            revenues_note,
            datetime.datetime.now(),
            datetime.datetime.now()
        ))
        response = do_create_response([{
            'id'         : revenues_model.connector.insert_id(),
            'name'       : revenues_name,
            'category_id': revenues_category_id,
            'price'      : revenues_price,
            'total_price': revenues_total_price,
            'member_id'  : revenues_member_id,
            'date'       : revenues_date,
            'note'       : revenues_note
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ 収入レコード更新処理

@route('/api/revenues/:pid', method='PUT')
def update_revenues(pid):
    revenues_id = pid
    revenues_name = request.json.get('name')
    revenues_category_id = request.json.get('category_id')
    revenues_price = request.json.get('price')
    revenues_total_price = request.json.get('total_price')
    revenues_member_id = request.json.get('member_id')
    revenues_date = request.json.get('date')
    revenues_note = request.json.get('note')

    try:
        revenues_model.update_row(revenues_id,
            fields=(
                'name',
                'category_id',
                'price',
                'total_price',
                'member_id',
                'date',
                'note',
                'modified'
            ),
            values=(
                revenues_name,
                revenues_category_id,
                revenues_price,
                revenues_total_price,
                revenues_member_id,
                revenues_date,
                revenues_note,
                datetime.datetime.now()
            )
        )
        response = do_create_response([{
            'id'         : revenues_id,
            'name'       : revenues_name,
            'category_id': revenues_category_id,
            'price'      : revenues_price,
            'total_price': revenues_total_price,
            'member_id'  : revenues_member_id,
            'date'       : revenues_date,
            'note'       : revenues_note
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ 収入レコード削除処理

@route('/api/revenues/:pid', method='DELETE')
def delete_revenues(pid):
    revenues_id = pid

    try:
        revenues_model.delete_row(revenues_id,
            logic=False
        )
        response = do_create_response([{
            'id': revenues_id
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ 収入レコード全取得

@route('/api/revenues', method=['GET', 'OPTIONS'])
def get_revenues():
    return do_create_response(revenues_model.get_rows_all())

# }}}
# {{{ カテゴリレコード生成処理

@route('/api/categories', method='POST')
def create_categories():
    categories_name = request.json.get('name')
    categories_type = request.json.get('type')
    categories_fixed = request.json.get('fixed')

    try:
        categories_model.add_rows(values=(
            categories_name,
            categories_type,
            categories_fixed,
            datetime.datetime.now(),
            datetime.datetime.now()
        ))
        response = do_create_response([{
            'id'    : categories_model.connector.insert_id(),
            'name'  : categories_name,
            'type'  : categories_type,
            'fixed' : categories_fixed
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ カテゴリレコード更新処理

@route('/api/categories/:pid', method='PUT')
def update_categories(pid):
    categories_id = pid
    categories_name = request.json.get('name')
    categories_type = request.json.get('type')
    categories_fixed = request.json.get('fixed')

    try:
        categories_model.update_row(categories_id,
            fields=(
                'name',
                'type',
                'fixed',
                'modified'
            ),
            values=(
                categories_name,
                categories_type,
                categories_fixed,
                datetime.datetime.now()
            )
        )
        response = do_create_response([{
            'id'    : categories_id,
            'name'  : categories_name,
            'type'  : categories_type,
            'fixed' : categories_fixed
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ カテゴリレコード削除処理

@route('/api/categories/:pid', method='DELETE')
def delete_categories(pid):
    categories_id = pid

    try:
        categories_model.delete_row(categories_id,
            logic=False
        )
        response = do_create_response([{
            'id': categories_id
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ カテゴリレコード全取得

@route('/api/categories', method=['GET', 'OPTIONS'])
def get_categories():
    return do_create_response(categories_model.get_rows_all())

# }}}
# {{{ クレジットカードレコード生成処理

@route('/api/creditcards', method='POST')
def create_creditcards():
    creditcards_name = request.json.get('name')
    creditcards_cutoff = request.json.get('cutoff')
    creditcards_debit = request.json.get('debit')
    creditcards_member_id = request.json.get('member_id')

    try:
        creditcards_model.add_rows(values=(
            creditcards_name,
            creditcards_cutoff,
            creditcards_debit,
            creditcards_member_id,
            datetime.datetime.now(),
            datetime.datetime.now()
        ))
        response = do_create_response([{
            'id'        : creditcards_model.connector.insert_id(),
            'name'      : creditcards_name,
            'cutoff'    : creditcards_cutoff,
            'debit'     : creditcards_debit,
            'member_id' : creditcards_member_id
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ クレジットカードレコード更新処理

@route('/api/creditcards/:pid', method='PUT')
def update_creditcards(pid):
    creditcards_id = pid
    creditcards_name = request.json.get('name')
    creditcards_cutoff = request.json.get('cutoff')
    creditcards_debit = request.json.get('debit')
    creditcards_member_id = request.json.get('member_id')

    try:
        creditcards_model.update_row(creditcards_id,
            fields=(
                'name',
                'cutoff',
                'debit',
                'member_id',
                'modified'
            ),
            values=(
                creditcards_name,
                creditcards_cutoff,
                creditcards_debit,
                creditcards_member_id,
                datetime.datetime.now()
            )
        )
        response = do_create_response([{
            'id'        : creditcards_id,
            'name'      : creditcards_name,
            'cutoff'    : creditcards_cutoff,
            'debit'     : creditcards_debit,
            'member_id' : creditcards_member_id
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ クレジットカードレコード削除処理

@route('/api/creditcards/:pid', method='DELETE')
def delete_creditcards(pid):
    creditcards_id = pid

    try:
        creditcards_model.delete_row(creditcards_id,
            logic=False
        )
        response = do_create_response([{
            'id': creditcards_id
        }])
    except:
        response = do_create_response([])

    return response

# }}}
# {{{ クレジットカードレコード全取得

@route('/api/creditcards', method=['GET', 'OPTIONS'])
def get_creditcards():
    return do_create_response(creditcards_model.get_rows_all())

# }}}
# {{{ メンバーレコード全取得

@route('/api/members', method=['GET', 'OPTIONS'])
def get_members():
    return do_create_response(members_model.get_rows_all())

# }}}
# {{{ DBバックアップ

@route('/api/backup', method=['GET', 'OPTIONS'])
def do_backup_database():
    payments_model.dump()
    return do_create_response([{}])

# }}}

# {{{ Template Path setting

TEMPLATE_PATH.insert(0, 'app')

# }}}
# {{{ Router Index

@route('/')
def router_index():
    return template('index')

# }}}
# {{{ Router Static

@route('/<filepath:path>', name='static_file')
def router_static(filepath):
    return static_file(filepath, root='app')

# }}}

if __name__ == '__main__':
    """
    ローカルサーバー起動処理
    """
    app = default_app()
    run(
        app = app,
        host = 'localhost',
        port = 8000,
        debug = True,
        reloader = True
    )

