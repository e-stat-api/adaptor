#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import csv
import random
import pandas as pd
from flask import Flask
sys.path.append('../python/')

import e_Stat_API_Adaptor

app = Flask(__name__)
eStatAPI = e_Stat_API_Adaptor.e_Stat_API_Adaptor({
    # 取得したappId
    'appId'	: '#appID#'   
    , 'limit' : '10000'    # データをダウンロード時に一度に取得するデータ件数
    , 'next_key': False # next_keyに対応するか否か(非対応の場合は上記のlimitで設定した件数のみしかダウンロードされない)  対応時はTrue/非対応時はFalse
    , 'directory': '#絶対パス# /foo/bar/'     # 中間アプリの設置ディレクトリ
    , 'ver'		: '2.0'      # APIのバージョン
    , 'format'	: 'json'     # データを取得形式
})


@app.route(eStatAPI.path['http-public'] + '<appId>/search/<q>.<ext>', methods=['GET'])
def _search_id(appId, q, ext):
    eStatAPI._['appId'] = appId
    return eStatAPI.response(eStatAPI.get_output(eStatAPI.search_id(q, eStatAPI.path['dictionary-index']), ext), ext)


@app.route(eStatAPI.path['http-public'] + '<appId>/<cmd>/<id>.<ext>', methods=['GET'])
def _get_data(appId, cmd, id, ext):
    eStatAPI._['appId'] = appId
    return eStatAPI.response(eStatAPI.get_output(eStatAPI.get_csv(cmd, id), ext), ext)


@app.route(eStatAPI.path['http-public'] + '<appId>/merge/<ids>/<group_by>.<ext>', methods=['GET'])
def _merge_data(appId, ids, group_by, ext):
    eStatAPI._['appId'] = appId
    aggregate = request.args.get('aggregate') if request.args.get(
        'aggregate') is not None else ''
    data = eStatAPI.merge_data(ids, group_by, aggregate)
    eStatAPI.path['tmp_merge'] = eStatAPI.path['tmp'] + '.'.join(
        [eStatAPI._['appId'], ''.join([l for l in random.choice(eStatAPI.random_str)]), 'csv'])
    data.to_csv(eStatAPI.path['tmp_merge'],
                quoting=csv.QUOTE_NONNUMERIC, index=None)
    tmp_csv = eStatAPI.cmd_line(eStatAPI.build_cmd(
        ['cat', eStatAPI.path['tmp_merge']]))
    eStatAPI.cmd_line(eStatAPI.build_cmd(['rm', eStatAPI.path['tmp_merge']]))
    return eStatAPI.response(eStatAPI.get_output(tmp_csv, ext), ext)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
