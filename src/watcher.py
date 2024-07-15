import websockets
import json


class RosbridgeWatcher:
    def __init__(self, config):
        ip = config.get('ip')
        port = config.get('port')
        self.rosbridge_url = f"ws://{ip}:{port}"
        self.config = config

    def is_msg_different_without_stamp(self, msg1, msg2):
        if msg1 is None or msg2 is None:
            return True
        
        msg1_dict = json.loads(msg1)
        msg2_dict = json.loads(msg2)
        
        msg1_dict['msg']['header'].pop('stamp', None)
        msg2_dict['msg']['header'].pop('stamp', None)

        msg1_modified = json.dumps(msg1_dict, sort_keys=True)
        msg2_modified = json.dumps(msg2_dict, sort_keys=True)

        return msg1_modified != msg2_modified


    async def watch_topic(self, topic_name, message_type, callback):
        async with websockets.connect(self.rosbridge_url) as websocket:
            # Subscribe to the topic
            subscribe_msg = {
                "op": "subscribe",
                "topic": topic_name,
                "type": message_type
            }
            await websocket.send(json.dumps(subscribe_msg))
            print(f"Subscribed to {topic_name}")

            try:
                prev_message = None
                while True:
                    # Receive message from the topic
                    message = await websocket.recv()
                    data = json.loads(message)
                    if not self.config.get('log_only_changes') or self.is_msg_different_without_stamp(prev_message, message):
                        print(f"Received message: {data}")
                        callback(data)

                    prev_message = message

            except websockets.ConnectionClosed:
                print("Connection to ROSBridge closed")

