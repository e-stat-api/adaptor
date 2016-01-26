#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('./')
import e_Stat_API_Adaptor
eStatAPI = e_Stat_API_Adaptor.e_Stat_API_Adaptor({
	# 取得したappId
	 'appId'	: '#appID#'
	# データをダウンロード時に一度に取得するデータ件数
	,'limit'	: '10000'
	# next_keyに対応するか否か(非対応の場合は上記のlimitで設定した件数のみしかダウンロードされない)
	# 対応時はTrue/非対応時はFalse
	,'next_key'	: True
	# 中間アプリの設置ディレクトリ
	,'directory':'#Directory#'
	# APIのバージョン
	,'ver'		:'2.0'
})
# 0000030001をcsvの形式でダウンロード
print 'id:'+sys.argv[1]
print  eStatAPI.get_csv('get' , sys.argv[1])