import folium
from folium.plugins import MarkerCluster
import base64
import io

# 地図を初期化（博多駅を中心に設定）
map_center = [start_latitude, start_longitude]
map = folium.Map(location=map_center, zoom_start=14)

# マーカークラスターを作成
marker_cluster = MarkerCluster().add_to(map)

# 各GPSデータポイントにマーカーを設置
for index, row in gps_data.iterrows():
    # マーカーに表示する情報を作成
    popup_info = folium.Popup(
        f"Timestamp: {row['Timestamp']}<br>Speed: {row['Speed(km/h)']} km/h",
        parse_html=True
    )
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_info,
    ).add_to(marker_cluster)

# 地図を一時ファイルとして保存
map_file_path = '/mnt/data/gps_data_map.html'
map.save(map_file_path)

map_file_path
