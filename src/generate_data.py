import osmnx as ox
import networkx as nx
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    # ラジアンに変換
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # ハーバーサイン公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球の半径(キロメートル)
    return c * r

def interpolate_points(p1, p2, num_points):
    """ p1とp2の間にnum_pointsの数だけポイントを補間する """
    return zip(np.linspace(p1[0], p2[0], num_points),
               np.linspace(p1[1], p2[1], num_points))

def generate_gps_data(start_point, end_point, start_time, speed_km_per_h, sampling_rate):
    # OSMnxで道路ネットワークを取得
    G = ox.graph_from_point(start_point, dist=3000, network_type='walk')

    # 最も近いノードを見つける
    orig_node = ox.distance.nearest_nodes(G, start_point[1], start_point[0])
    dest_node = ox.distance.nearest_nodes(G, end_point[1], end_point[0])

    # 最短ルートを見つける
    route = nx.shortest_path(G, orig_node, dest_node, weight='length')

    # ルート上の各ノードの座標と距離を取得
    nodes = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in route]
    distances = [haversine(lon1, lat1, lon2, lat2) for (lat1, lon1), (lat2, lon2) in zip(nodes[:-1], nodes[1:])]

    # 総距離と移動時間の計算
    total_distance = sum(distances)
    total_time = total_distance / (speed_km_per_h / 60)  # 分単位で計算

    # サンプル数と各セグメントに必要なサンプル数の計算
    total_samples = int(total_time * 60 / sampling_rate)
    segment_samples = [max(1, round(d / total_distance * total_samples)) for d in distances]

    # 各セグメント間でポイントを補間
    sampled_points = []
    for (p1, p2), num in zip(zip(nodes[:-1], nodes[1:]), segment_samples):
        # 各セグメントのポイントを補間
        segment_points = list(interpolate_points(p1, p2, num))
        sampled_points.extend(segment_points[:-1])  # 各セグメントの最後のポイントを除外

    # 最後のポイントを追加
    sampled_points.append(nodes[-1])

    # サンプリングされたポイントからデータフレームを作成
    sampled_gps_data = pd.DataFrame(sampled_points, columns=['longitude', 'latitude'])

    # 総サンプル数に合わせるために、不足分のポイントを調整
    total_samples = min(len(sampled_gps_data), total_samples)
    sampled_gps_data = sampled_gps_data.iloc[:total_samples]

    # タイムスタンプと速度をデータフレームに追加
    timestamps = [start_time + timedelta(seconds=sampling_rate * i) for i in range(total_samples)]
    sampled_gps_data['timestamp'] = timestamps
    sampled_gps_data['speed_km/h'] = speed_km_per_h

    return sampled_gps_data

# パラメータ設定
start_point = (33.5904, 130.4206)  # 博多駅の座標
end_point = (33.5919, 130.3982)  # 天神駅の座標
start_time = datetime.now()
speed_km_per_h = 4.5 # 歩行速度
sampling_rate = 5 # サンプリングレート（秒）

gps_data = generate_gps_data(start_point, end_point, start_time, speed_km_per_h, sampling_rate)
gps_data.to_csv('./outputs/gps_data.csv', index=False)
