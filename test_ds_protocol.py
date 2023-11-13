import ds_protocol
import json
from collections import namedtuple



server_response_1 = json.dumps({"response": {"type": "ok", "message": "Direct message sent"}})
server_response_2 = json.dumps({"response": {"type": "ok", "messages": [{"message": "Hello User 1!", "from": "markb", "timestamp": "1603167689.3928561"}, {"message": "Bzzzzz", "from": "thebeemoviescript", "timestamp": "1603167689.3928561"}]}})

print(ds_protocol.encode_json(command="directmessage", token="user_token", directmessage={"entry": "Hello World!","recipient":"ohhimark", "timestamp": "1603167689.3928561"}))
print(ds_protocol.encode_json(command="directmessage", token="user_token", directmessage="new"))
print(ds_protocol.encode_json(command="directmessage", token="user_token", directmessage="all"))
print(ds_protocol.extract_json(server_response_1))
print(ds_protocol.extract_json(server_response_2))