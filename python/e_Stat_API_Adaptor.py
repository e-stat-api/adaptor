#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # #
#
#  e-Stat API Adaptor
#  (c) 2016 National Statistics Center
#  License: MIT
#
# # # # # # # # # # # # # # # # # # # # # # # #

import os
import subprocess
import unicodedata
import urllib2
import json
import csv
import re
import StringIO
import random
import numpy
import math
import pandas as pd
from flask import request
from flask import Response
from flask import Flask


class e_Stat_API_Adaptor:

    def __init__(self, _):
        # アプリ設定
        self._ = _
        # パス設定
        self.path = {
            # データダウンロード時に使用するディレクトリ
            # CSVのディレクトリ
            # 全ての統計IDを含むJSONファイルのパス
            'tmp'				: self._['directory'] + 'tmp/'            # indexを作成するパス
            # ユーザーindex
            # 統計センターindex
            # 統計センターindexのダウンロード用URL
            # 詳細(n-gram形式)
            # 公開ディレクトリ
            , 'csv'				: self._['directory'] + 'data-cache/', 'statid-json'		: self._['directory'] + 'dictionary/all.json.dic', 'dictionary-index'	: self._['directory'] + 'dictionary/index.list.dic', 'dictionary-user'	: self._['directory'] + 'dictionary/user.csv.dic', 'dictionary-stat-center': self._['directory'] + 'dictionary/stat.center.csv.dic', 'url-dictionary-stat-center': 'http://www.e-stat.go.jp/api/sample2/api-m/stat-center-index.csv', 'dictionary-detail': self._['directory'] + 'dictionary/detail/', 'http-public'		: '/'
        }
        self.msg = {
            'check-extension': 'Oops! check your extension!'
        }
        self.url = {
            'host'		: 'http://api.e-stat.go.jp', 'path': '/'.join([
                'rest', self._['ver'], 'app', 'json', 'getStatsData'
            ])
        }
        self.csv_header = {
            'index': ['statsDataId', '調査名', '調査年月', '組織名', 'カテゴリー'], 'user': ['statsDataId', '検索語']
        }
        self.header = {'Access-Control-Allow-Origin': '*'}
        self.random_str = 'ABCDEFGHIJKLMNOPQRTSUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
        self.cache = {}
        # N-グラムの設定
        self.gram = 2
    # 全ての統計IDをダウンロード

    def load_all_ids(self):
        load_uri = self.build_uri({
            'appId': self._['appId'], 'searchWord': ''
        }).replace('getStatsData', 'getStatsList')
        self.cmd_line(self.build_cmd([
            'curl', '-o', self.path['statid-json'], '"' + load_uri + '"'
        ]))
    # ダウンロードした統計表からインデックスファイルを作成する

    def build_statid_index(self):
        jd = self.load_json(
            self.path['statid-json'])['GET_STATS_LIST']['DATALIST_INF']['TABLE_INF']
        rows = '\n'.join([
            '-'.join([
                         j['@id'], j['STAT_NAME']['$'], str(j['SURVEY_DATE']), j['GOV_ORG']['$'], j[
                             'MAIN_CATEGORY']['$'], j['SUB_CATEGORY']['$']
                         ]) + '.dic'
            for j in jd
        ]).encode('utf-8')
        with open(self.path['dictionary-index'], 'w') as f:
            f.write(rows)
    # 統計センターが作成するindexのダウンロード用関数

    def load_stat_center_index(self):
        self.cmd_line(self.build_cmd([
            'curl', '-o', self.path['dictionary-stat-center'], '"' +
            self.path['url-dictionary-stat-center'] + '"'
        ]))

    def build_detailed_index(self):
        jd = self.load_json(
            self.path['statid-json'])['GET_STATS_LIST']['DATALIST_INF']['TABLE_INF']
        for i, j in enumerate(jd):

            filename = '-'.join([
                j['@id'], j['STAT_NAME']['$'], str(j['SURVEY_DATE']), j['GOV_ORG']['$'], j[
                    'MAIN_CATEGORY']['$'], j['SUB_CATEGORY']['$']
            ]) + '.dic'
            try:
                STATISTICS_NAME = self.create_n_gram_str(
                    j['STATISTICS_NAME'], self.gram)
            except:
                STATISTICS_NAME = ''
            try:
                TITLE = self.create_n_gram_str(j['TITLE']['$'], self.gram)
            except:
                TITLE = ''
            with open(self.path['dictionary-detail'] + filename, 'w') as f:
                f.write(
                    '\n'.join([STATISTICS_NAME.encode('utf-8'), TITLE.encode('utf-8')]))

    def create_n_gram_str(self, str, gram):
        str = unicodedata.normalize('NFKC', str)
        str = re.sub('[\s\(\)-,\[\]]', '', str).replace(u'・', '')
        return ','.join([v for v in [str[str.index(s):str.index(s) + gram] for s in str] if v is not ''])

    def search_detailed_index(self, q):
        detail_files = os.listdir(self.path['dictionary-detail'])
        detail_index = []
        for dic in detail_files:
            with open(self.path['dictionary-detail'] + dic, 'r') as f:
                for row in f.readlines():
                    if q in row:
                        detail_index.append(','.join([dic.split('-')[0], q]))
        return detail_index

    def create_user_index_from_detailed_index(self, q):
        with open(self.path['dictionary-user'], 'a') as f:
            f.write('\n'.join(self.search_detailed_index(q)) + '\n')

    def build_uri(self, param):
        return '?'.join([
            '/'.join([self.url['host'], self.url['path']]
                     ), '&'.join([k + '=' + str(v) for k, v in param.items()])
        ])

    def build_cmd(self, cmd_list):
        return ' '.join(cmd_list)

    def cmd_line(self, cmd):
        try:
            return subprocess.check_output(cmd, shell=True)
        except:
            return None

    def load_json(self, path):
        with open(path) as json_data:
            return json.load(json_data)

    def search_id(self, q, _index, _header='index'):
        if q == 'index':
            rows = [[c for c in f.split('-') if '.dic' not in c]
                    for f in self.cmd_line(self.build_cmd(['cat', _index])).split('\n')]
        else:
            output = self.cmd_line(
                'cat ' + _index + ' | ' + 'grep -n \"' + q + '\"').split('\n')
            rows = [[c if i > 0 else c.split(
                ':')[-1] for i, c in enumerate(f.split('-')) if '.dic' not in c] for f in output]
        for i, r in enumerate(rows):
            if len(r) == 6:
                rows[i][2] = rows[i][2] + '-' + rows[i][3]
                del rows[i][3]
            rows[i] = ','.join(rows[i])
        rows = '\n'.join([','.join(self.csv_header[_header]), '\n'.join(rows)])
        return rows

    def get_all_data(self, statsDataId, next_key):
        self.cache['tmp'] = self.path['tmp'] + \
            '.'.join([self._['appId'], statsDataId, next_key, 'json'])
        try:
            if os.path.exists(self.cache['tmp']) == False:
                apiURI = self.build_uri({
                    'appId'		: self._['appId'], 'statsDataId'	: statsDataId, 'limit'		: self._['limit'], 'startPosition': next_key
                })
                self.cmd_line(self.build_cmd(
                    ['curl', '-o', self.cache['tmp'], '"' + apiURI + '"'])).replace('\n', '')
            RESULT_INF = self.load_json(self.cache['tmp'])['GET_STATS_DATA'][
                'STATISTICAL_DATA']['RESULT_INF']
            NEXT_KEY = '-1' if 'NEXT_KEY' not in RESULT_INF.keys() else RESULT_INF[
                'NEXT_KEY']
            return str(NEXT_KEY)
        except:
            # 下記のエラー処理は考える
            filepath = self.path[
                'tmp'] + '.'.join([self._['appId'], statsDataId, '*', 'json'])
            try:
                downloaded_files = self.cmd_line(
                    self.build_cmd(['ls', filepath]))
                if downloaded_files != '':
                    self.remove_file(filepath)
                return None
            except:
                return None

    def convert_raw_json_to_csv(self, statsDataId):
        try:
            self.cache['csv'] = self.path['csv'] + statsDataId + '.csv'
            dat = {'header': None, 'body': [], 'keys': None}
            ix = [
                {int(f.split('.')[1]):f}
                for f in self.cmd_line(
                    self.build_cmd(
                        ['ls', self.path['tmp'] + '.'.join([self._['appId'], statsDataId, '*', 'json'])])
                ).split('\n')
                if f != ''
            ]
            print ix
            ix.sort()
            ix = [hash.values()[0] for hash in ix]
            for i, json_file in enumerate(ix):
                print i, json_file
                jd = self.load_json(json_file)
                if i == 0:
                    dat['header'] = [
                        k.replace('@', '')
                        for k in jd['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE'][0].keys()
                    ]
                    dat['keys'] = jd['GET_STATS_DATA'][
                        'STATISTICAL_DATA']['CLASS_INF']
                dat['body'].extend(jd['GET_STATS_DATA'][
                                   'STATISTICAL_DATA']['DATA_INF']['VALUE'])
            _h = {}
            _b = {}
            for o in dat['keys']['CLASS_OBJ']:
                o['CLASS'] = [o['CLASS']] if (
                    type(o['CLASS']) is list) is False else o['CLASS']
                if o['@id'] not in _b.keys():
                    _b[o['@id']] = {}
                for oc in o['CLASS']:
                    _b[o['@id']][oc['@code']] = oc['@name']
                _h[o['@id']] = o['@name']
            newCSV = [[r.encode('utf-8') for r in [_h[h]
                                                   if h in _h.keys() else h for h in dat['header']]]]
            newCSV.append(dat['header'])
            for body in dat['body']:
                newCSV.append(body.values())
            for i, x in enumerate(newCSV):
                if i > 0:
                    for j, d in enumerate(x):
                        if dat['header'][j] in _b.keys() and d in _b[dat['header'][j]].keys():
                            newCSV[i][j] = _b[dat['header'][j]][
                                d].encode('utf-8')
                        else:
                            newCSV[i][j] = d.encode('utf-8')
            with open(self.cache['csv'], 'w') as f:
                csv.writer(f, quoting=csv.QUOTE_NONNUMERIC).writerows(newCSV)
            filepath = self.path[
                'tmp'] + '.'.join([self._['appId'], statsDataId, '*', 'json'])
            self.cmd_line(self.build_cmd(['rm', filepath]))

        except:
            filepath = self.path[
                'tmp'] + '.'.join([self._['appId'], statsDataId, '*', 'json'])
            if os.path.exists(filepath):
                self.cmd_line(self.build_cmd(['rm', filepath]))

    def merge_data(self, statsDataId, group_by, aggregate):
        statsDataId = statsDataId.split(',')
        data = {}
        for id in statsDataId:
            csv_path = self.path['csv'] + id + '.csv'
            if os.path.exists(csv_path) == False:
                self.get_all_data(id, '1')
                self.convert_raw_json_to_csv(id)
            data[id] = pd.read_csv(csv_path, skiprows=[0])
            data[id]['stat-id'] = id
        for k, v in data.items():
            v.rename(columns=lambda x: x.replace('$', '$' + k), inplace=True)
        data = pd.concat([v for k, v in data.items()], ignore_index=True)
        if group_by != 'all':
            # summation
            if aggregate == 'sum':
                data = data.groupby(group_by.split(',')).sum()
            # min
            elif aggregate == 'min':
                data = data.groupby(group_by.split(',')).min()
            # max
            elif aggregate == 'max':
                data = data.groupby(group_by.split(',')).max()
            # median
            elif aggregate == 'median':
                data = data.groupby(group_by.split(',')).median()
            # count
            elif aggregate == 'count':
                data = data.groupby(group_by.split(',')).count()
            # variance
            elif aggregate == 'var':
                data = data.groupby(group_by.split(',')).var()
            # standard deviation
            elif aggregate == 'std':
                data = data.groupby(group_by.split(',')).std()
            # mean
            elif aggregate == 'mean':
                data = data.groupby(group_by.split(',')).mean()
            else:
                data = data
        if group_by != 'all':
            data = data.loc[:, [c for c in data.columns if '$' in c or group_by in c]
                            ] if aggregate == '' else data.loc[:, [c for c in data.columns if '$' in c]]
        return data.reset_index()

    def remove_file(self, filepath):
        self.cmd_line(self.build_cmd([
            'rm', filepath
        ]))

    def get_csv(self, cmd, statsDataId):
        cmd = 'cat' if cmd == 'get' else cmd
        self.cache['csv'] = self.path['csv'] + statsDataId + '.csv'

        if os.path.exists(self.cache['csv']) == False:
            next_key = '1'
            if self._['next_key'] == True:
                while next_key != '-1':
                    next_key = self.get_all_data(statsDataId, next_key)
                    print next_key
            else:
                self.get_all_data(statsDataId, next_key)
            self.convert_raw_json_to_csv(statsDataId)
        txt = self.cmd_line(self.build_cmd([
            cmd, self.cache['csv'], " | awk 'NR != 2 { print $0; }'"
        ])) if cmd == 'cat' or cmd == 'head' else self.cmd_line(self.build_cmd([
            cmd, self.cache['csv']
        ]))
        return txt

    def error(self, txt):
        return txt

    def get_output(self, data, output_type):
        def get_tmp_data(tmp_data_0_j, tmp_data_i_j):
            if re.match('^\$[0-9]+$', tmp_data_0_j) or tmp_data_0_j == '$':
                return float(tmp_data_i_j) if tmp_data_i_j != '' else None
            else:
                return tmp_data_i_j
        if output_type == 'csv':
            return data
        elif output_type == 'rjson':
            tmp_data = [d for d in csv.reader(StringIO.StringIO(data.strip()))]
            data = []
            for i in range(1, len(tmp_data)):
                row_data = {}
                for j in range(0, len(tmp_data[i])):
                    row_data[tmp_data[0][j]] = get_tmp_data(
                        tmp_data[0][j], tmp_data[i][j])
                data.append(row_data)
            return json.dumps(data)
        elif output_type == 'cjson':
            tmp_data = [d for d in csv.reader(StringIO.StringIO(data.strip()))]
            print tmp_data[0]
            data = {}
            for i in range(0, len(tmp_data[0])):
                print tmp_data[0][i]
                data[tmp_data[0][i]] = [get_tmp_data(tmp_data[0][i], tmp_data[j][
                                                     i]) for j in range(1, len(tmp_data))]
            return json.dumps(data)
        else:
            return self.error(self.msg['check-extension'])

    def mimetype(self, ext):
        mt = 'text/plain' if ext == 'csv' else 'application/json'
        mt = 'application/octet-stream' if request.args.get(
            'dl') == 'true' else mt
        return mt

    def response(self, res, ext):
        return Response(res, mimetype=self.mimetype(ext), headers=self.header)
