import folium
import pandas as pd

# GPSデータを読み込む
gps_data = pd.read_csv('./outputs/gps_data.csv')

# 地図の中心を最初のGPSポイントに設定
map_center = [gps_data.iloc[0]['latitude'], gps_data.iloc[0]['longitude']]
map = folium.Map(location=map_center, zoom_start=15)

# GPSデータの各ポイントにマーカーをプロット
for index, row in gps_data.iterrows():
    folium.Marker([row['latitude'], row['longitude']],
                  popup=f"Time: {row['timestamp']}, Speed: {row['speed_km/h']} km/h").add_to(map)

# 地図をHTMLファイルとして保存
map.save('./outputs/gps_data_map.html')
