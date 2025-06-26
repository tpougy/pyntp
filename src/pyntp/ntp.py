# nptサーバーによる正確な時刻 [ntp_time]

import os
import sys
import math
import time
import ntplib
import threading
import iter_backoff

# 共通変数
PARAMS = {
	"ADJUST_INTERVAL": 60,	# 時刻同期の周期
	"MERGE_TIME": 10,	# 何秒かけて同期時刻に合流するか
	"NTP_SERVER_URL": "pool.ntp.org",
}

# ntp時刻とのずれ情報の掲示板
OFFSET_POOL = {
	"prev_offset": 0,
	"new_offset": 0,
	"switch_time_local": -math.inf,	# offset情報を更新した時刻 (手元の時計)
}

# スレッド間共有メッセージとロック
lock = threading.Lock()

# offsetを取得 (iterバックオフあり)
def get_offset(client):
	# 指数バックオフ
	for _ in iter_backoff(s0 = 1, r = 3, n = 5):
		try:
			# 時刻同期の実施
			response = client.request(PARAMS["NTP_SERVER_URL"], version = 3)
			new_offset = response.offset
			return new_offset
		except:
			continue
	raise Exception("[ntp-time error] Exceeded exponential backoff attempts for NTP server communication")

# 受信を1回実施とoffset情報の切り替え
def recv_once(client):
	# offsetを取得 (iterバックオフあり)
	new_offset = get_offset(client)
	# offsetの書き換え
	with lock:
		OFFSET_POOL["prev_offset"] = OFFSET_POOL["new_offset"]
		OFFSET_POOL["switch_time_local"] = time.time()
		OFFSET_POOL["new_offset"] = new_offset

# 別スレッドで定期的に時刻合わせ
def adjust_loop():
	client = ntplib.NTPClient()
	while True:
		try:
			# 受信を1回実施とoffset情報の切り替え
			recv_once(client)
		except:
			# サーバー接続に失敗した場合はメインスレッドも含めて落とす
			print("[ntp-time error] Failed to obtain information for time synchronization.")
			os._exit(0)
		# 次の時刻合わせまで待つ
		time.sleep(PARAMS["ADJUST_INTERVAL"])

# 別スレッドで定期的に時刻合わせ
thread = threading.Thread(target = adjust_loop, daemon = True)	# メインスレッドが落ちたときはサブスレッドも落とす
thread.start()

# なめらかに変化するoffsetの取得
def get_smoothed_offset(local_time):
	with lock:
		# offsetの混合率を算出
		passed_time = local_time - OFFSET_POOL["switch_time_local"]	# 切り替わり時刻からの経過時間
		raw_alpha = passed_time / PARAMS["MERGE_TIME"]
		alpha = max(0, min(raw_alpha, 1))	# クリッピング
		# offsetの補正
		fixed_offset = OFFSET_POOL["prev_offset"] * (1 - alpha) + OFFSET_POOL["new_offset"] * alpha
	return fixed_offset

# 正確な現在時刻の取得 [ntp_time]
def now():
	# 補正前の時刻
	local_time = time.time()
	# 時刻の補正
	fixed_time = local_time + get_smoothed_offset(local_time)	# なめらかに変化するoffsetの取得
	return fixed_time
