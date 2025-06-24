from home.models import DashboardData
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import paho.mqtt.client as mqtt
import os, math, json

base_svg = None

class MqttClient:
    def __init__(self, host, port, topic:list[str]) -> None:
        self.host = host
        self.port = int(port)
        self.topic = topic
        self.subscribe_topic = []
        self.get_sub_topic()
        self.set_client()
        self.count = 0

        self.radar_data = None
        self.simulate_data = None

    def get_sub_topic(self):
        for topic in self.topic:
            self.subscribe_topic.append((topic, 0))

    def set_client(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        print(f'Set mqtt client on {self.host}:{self.port}')
        # 延遲連接，避免啟動時失敗
        try:
            self.client.connect(self.host, self.port)
            self.client.loop_start()
        except Exception as e:
            print(f'MQTT connection failed: {e}, will retry later')

    def __on_connect(self, client, userdata, flags, rc, properties):
        print(f"Connected with result code {rc}. topic={len(self.topic)}")
        client.subscribe(self.subscribe_topic)

    def __on_message(self, client, userdata, msg):
        if msg.topic in self.topic:
            json_data = msg.payload.decode('utf-8')
            json_data = json.loads(json_data)
            # DashboardData.objects.update_or_create(
            #     topic_name = msg.topic,
            #     defaults={"json_data": json_data}
            # )
            if msg.topic == 'radar':
                self.radar_data = json_data
            elif msg.topic == 'simulate':
                self.simulate_data = json_data

            # Merge both datasets (if they exist)
            merged_data = {"id": [], "azm": [], "elv": [],'color':[]}
            
            # If we already have radar data, include it
            if self.radar_data:
                merged_data["id"].extend(self.radar_data["id"])
                merged_data["azm"].extend(self.radar_data["azm"])
                merged_data["elv"].extend(self.radar_data["elv"])
                merged_data["color"].extend(self.radar_data.get('color', ['#ff0000' for _ in range(len(self.radar_data["id"]))]))
            
            # If we already have simulate data, include it
            if self.simulate_data:
                merged_data["id"].extend(self.simulate_data["id"])
                merged_data["azm"].extend(self.simulate_data["azm"])
                merged_data["elv"].extend(self.simulate_data["elv"])
                merged_data["color"].extend(self.simulate_data.get('color', ['#0000ff' for _ in range(len(self.simulate_data["id"]))]))

            svg = draw_polygon(merged_data)
            json_data['svg'] = svg

            self.count += 1
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "broadcast_group",
                {
                    "type": "broadcast_data",
                    "message": {
                        "topic": msg.topic,
                        "data": json_data,
                        'count': self.count
                        }
                }
            )
            # print(f'mqtt get {self.count} {msg.topic}')


def draw_polygon(radar:dict):
    global base_svg
    width, height = 800, 500
    radius = 230
    center_x, center_y = width // 2, height // 2

    def angle2xy(angle: float, text: str, line: float = radius, font_size: int = 24):
        angle = float(angle)
        angle = (angle - 90) * math.pi / 180
        x = center_x + line * math.cos(angle)
        y = center_y + line * math.sin(angle)
        text_width = len(text) * font_size * 0.6
        text_height = font_size
        x_centered = x - text_width / 2
        y_centered = y + text_height / 4
        return int(x_centered), int(y_centered)
    
    if base_svg is None:
        # 繪製底圖
        svg = f"""
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <circle cx="{center_x}" cy="{center_y}" r="{radius-10}" fill="none" stroke="silver" stroke-width="2"/>
            <circle cx="{center_x}" cy="{center_y}" r="{radius+10}" fill="none" stroke="silver" stroke-width="2"/>
            <path d="M{0+center_x} {-8+center_y} L{10+center_x} {8+center_y} L{-10+center_x} {8+center_y} Z" fill="lightgrey" stroke="lightgrey" stroke-width="1" />
        """
        # 繪製方位
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            fs = 20
            x_, y_ = angle2xy(angle, text=f'{angle}', line=int(radius*0.9), font_size=fs)
            svg += f'<text x="{x_}" y="{y_}" font-size="{fs}" fill="darkgreen" stroke="darkgreen" stroke-width="1">{angle}</text>'
        # 繪製天線
        for ant, angle in enumerate([0, 45, 90, 135, 180, 225, 270, 315, 22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]):
            fs = 16
            x_, y_ = angle2xy(angle, text=f'{ant}', line=int(radius), font_size=fs)
            svg += f'<text x="{x_}" y="{y_}" font-size="{fs}" fill="dodgerblue" stroke="dodgerblue" stroke-width="1">{ant}</text>'
        base_svg = svg
    else:
        svg = base_svg
    if radar is None: return svg+'</svg>'
    
    # 繪製無人機位置
    for id_, azm_, elv_, color_ in zip(radar['id'], radar['azm'], radar['elv'], radar['color']):
        azm_ = float(azm_)
        target_x, target_y = angle2xy(azm_, text=f'.', line=int(radius), font_size=4)
        # Simulated data starting with '-' will be drawn as a red dot
        if id_.startswith('-'): 
            # Draw a red dot instead of a line
            svg += f'<circle cx="{target_x}" cy="{target_y}" r="5" fill="{color_}" stroke="{color_}" stroke-width="2"/>'
            id_ = id_[1:]
            text_x = (center_x + target_x*3) / 4
            text_y = (center_y + target_y*3) / 4
        else:
            # Draw a line for the drone radar
            svg += f'<line x1="{center_x}" y1="{center_y}" x2="{target_x}" y2="{target_y}" stroke="{color_}" stroke-width="2" />'
            text_x = (center_x + target_x) / 2
            text_y = (center_y + target_y) / 2
        svg += f'<text x="{text_x}" y="{text_y}" font-size="15" text-anchor="middle" fill="darkslategrey" stroke="darkslategrey" stroke-width="1" )")>{id_} ({azm_}, {elv_})</text>'

    svg += '</svg>'
    return svg

def init_mqtt():
    mqtt_ip = os.getenv('MQTT_IP')
    mqtt_port = os.getenv('MQTT_PORT')
    radar = os.getenv('MQTT_TOPIC_RADAR')
    message = os.getenv('MQTT_TOPIC_MESSAGE')
    spec = os.getenv('MQTT_TOPIC_SPEC')
    ant = os.getenv('MQTT_TOPIC_ANT')
    pf = os.getenv('MQTT_TOPIC_PF')
    target = os.getenv('MQTT_TOPIC_TARGET')
    simulate = os.getenv('MQTT_TOPIC_SIMULATE')

    mqtt_client = MqttClient(
        mqtt_ip, mqtt_port,
        topic=[
            radar, message, spec, ant, pf, target, simulate
        ]
    )
    return mqtt_client