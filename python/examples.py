#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('./')
import e_Stat_API_Adaptor
eStatAPI = e_Stat_API_Adaptor.e_Stat_API_Adaptor({
    # 取得したappId
    'appId'	: '#appID#'    # データをダウンロード時に一度に取得するデータ件数
    # next_keyに対応するか否か(非対応の場合は上記のlimitで設定した件数のみしかダウンロードされない)
    , 'limit'	: '10000'    # 対応時はTrue/非対応時はFalse
    , 'next_key'	: True        # 中間アプリの設置ディレクトリ
    , 'directory': '#絶対パス#'        # APIのバージョン
    , 'ver'		: '2.0'
})
#
#
# # インストール直後に下記を実行
# #
# 全ての統計表IDをローカルにダウンロード
# print eStatAPI.load_all_ids()
# ダウンロードした統計表IDからインデックスを作成
# print eStatAPI.build_statid_index()
#
#
# # STATISTICS_NAMEとTITLEからインデックスを作成(N-gram)
# # print eStatAPI.build_detailed_index()
# # print eStatAPI.search_detailed_index('家計')
# #
# # 下記でユーザー用のインデックスにすることも可能
# # print eStatAPI.create_user_index_from_detailed_index('法人')
#
#
# # インデックスリストを検索
# # print  eStatAPI.search_id('法人', eStatAPI.path['dictionary-index'] )
# # ユーザー作成型インデックスを検索
# # print  eStatAPI.search_id('法人', eStatAPI.path['dictionary-user'], 'user')
#
# # print eStatAPI.search_id('index',	eStatAPI.path['dictionary-index'])
# # print eStatAPI.search_id('家計',  eStatAPI.path['dictionary-index'])
#
#
# # csvファイルのremove
# # eStatAPI.remove_file(eStatAPI.path['csv']+'*.csv')
#
# # データのダウンロード
# # eStatAPI.get_csv('get' , '0000030002')
# # 作成されたCSVファイルの例(1行目が列を表す、2行目はキー、データは文字列)
# #"$","全国都道府県030001","男女Ａ030001","年齢各歳階級Ｂ030003","全域・集中の別030002","時間軸(年次)","unit"
# #"$","area","cat02","cat03","cat01","time","unit"
# #"117060396","全国","男女総数","総数","全域","1980年","人"
#
# # データの結合
# # print eStatAPI.merge_data('0000030001,0000030001', 'all', 'std')
#
# # 一部のデータを見る
# # print eStatAPI.get_csv('head', '0000030001')
# # print eStatAPI.get_csv('tail', '0000030001')
#
# # データの出力
# # csv	:csv形式
# # rjson :json-row形式
# # cjson :json-col形式
# # print eStatAPI.get_output(eStatAPI.get_csv('get' , '0000030001'),'csv')
# # print eStatAPI.get_output(eStatAPI.get_csv('get' , '0000030001'),'rjson')
# # print eStatAPI.get_output(eStatAPI.get_csv('get' , '0000030001'),'cjson')
#
# # ファイル構成
