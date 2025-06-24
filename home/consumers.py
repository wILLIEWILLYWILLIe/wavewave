from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from home.mqtt_client import draw_polygon
import json, time

CONN_LIST = [] 

class DashboardConsumer(AsyncWebsocketConsumer):

    async def websocket_connect(self, message):
        CONN_LIST.append(self)
        self.group_name = "broadcast_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f'Websocket connected ({self}). connect = {len(CONN_LIST)}')
        await self.broadcast_data({
            'message':{
                'topic': 'message',
                'data': 
                    {'level': 'Websocket','text': 'Start websocket.'},
                'count': 0, 'time':time.time()*1000
                },
            })
        await self.broadcast_data({
            'message':{
                'topic': 'radar',
                'data': 
                    {'svg': draw_polygon(None)},
                'count': 0, 'time':time.time()*1000
                },
            })

    async def websocket_receive(self, message):
        return

    async def websocket_disconnect(self, message):
        CONN_LIST.remove(self)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f'Websocket disconnected ({self}). connect = {len(CONN_LIST)}')
        raise StopConsumer() #後端不允許連結
    
    async def broadcast_data(self, event):
        data = event['message']['data']
        topic = event['message']['topic']
        count = event['message']['count']
        await self.send(text_data=json.dumps({
            "topic": topic, "data":data, 'count':count, 'time':time.time()*1000
        }))
        # print(f'broadcast_data to topic {topic} {count}')