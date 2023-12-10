import osmnx as ox
import networkx as nx
import pandas as pd
from datetime import datetime, timedelta

def generate_gps_data(start_point, end_point, start_time, speed_km_per_h, sampling_rate):
    # OSMnxで道路ネットワークを取得
    G = ox.graph_from_point(start_point, dist=3000, network_type='walk')

    # 最も近いノードを見つける
    orig_node = ox.get_nearest_node(G, start_point)
    dest_node = ox.get_nearest_node(G, end_point)

    # 最短ルートを見つける
    route = nx.shortest_path(G, orig_node, dest_node, weight='length')

    # ルート上の各ノードの座標を取得
    longitudes, latitudes = zip(*[G.nodes[node]['x'], G.nodes[node]['y']] for node in route)

    # データフレームにデータを格納
    gps_data = pd.DataFrame({
        'latitude': latitudes,
        'longitude': longitudes
    })

    # タイムスタンプと速度の計算
    distance = sum(ox.utils.euclidean_dist_vec(lat1, lon1, lat2, lon2)
                   for (lat1, lon1), (lat2, lon2) in zip(gps_data[['latitude', 'longitude']].values[:-1],
                                                         gps_data[['latitude', 'longitude']].values[1:]))
    total_time = distance / (speed_km_per_h * 1000/3600)  # 秒単位で計算
    timestamps = [start_time + timedelta(seconds=sampling_rate*i)
                  for i in range(int(total_time/sampling_rate))]

    # タイムスタンプと速度をデータフレームに追加
    gps_data = gps_data.iloc[::int(len(gps_data)/len(timestamps))]
    gps_data['timestamp'] = timestamps
    gps_data['speed_km/h'] = speed_km_per_h

    return gps_data

# パラメータ設定
start_point = (33.5904, 130.4206)  # 博多駅の座標
end_point = (33.5919, 130.3982)  # 天神駅の座標
start_time = datetime.now()
speed_km_per_h = 4.5  # 歩行速度
sampling_rate = 5  # サンプリングレート（秒）

# GPSデータ生成
gps_data = generate_gps_data(start_point, end_point, start_time, speed_km_per_h, sampling_rate)

# CSVに出力
gps_data.to_csv('gps_data.csv', index=False)
