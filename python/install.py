#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('./')
import e_Stat_API_Adaptor
eStatAPI = e_Stat_API_Adaptor.e_Stat_API_Adaptor({
    # 取得したappId
    'appId'	: '#appId#'   
    # データをダウンロード時に一度に取得するデータ件数
    , 'limit'	: '10000'    
    # next_keyに対応するか否か(非対応の場合は上記のlimitで設定した件数のみしかダウンロードされない)
    # 対応時はTrue/非対応時はFalse
    , 'next_key'	: True        
   # 中間アプリの設置ディレクトリ
    , 'directory': '#絶対パス# /foo/bar/'
    # APIのバージョン        
    , 'ver'		: '2.0'
})
# 全ての統計表IDをローカルにダウンロード
print eStatAPI.load_all_ids()
# ダウンロードした統計表IDからインデックスを作成
print eStatAPI.build_statid_index()
