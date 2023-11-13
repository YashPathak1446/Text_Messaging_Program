# ds_protocol.py

# Ryan Zhang, Yash Pathak
# ryanyz@uci.edu, pathaky@uci.edu
# 20907746, 51317074

import json
from collections import namedtuple
import time



# Namedtuple to hold the values retrieved from json messages.
DataTuple = namedtuple('DataTuple', ['command', 'username', 'password', 'token', 'entry', 'timestamp', 'response_type', 'response_message'])


def extract_json(json_msg: str) -> DataTuple:
    '''
    Call the json.loads function on a json string and convert it to a DataTuple object
    :param json_msg: json to be loaded into a DataTuple namedtuple

    :return: DataTuple namedtuple
    '''
    try:
        json_obj = json.loads(json_msg)

        # Convert json object into a Data tuple depending on the type of command being issued
        if "join" in json_obj:
            data = DataTuple("join", json_obj["join"]["username"], json_obj["join"]["password"], json_obj["join"]["token"], None, None, None, None)

        elif "post" in json_obj:
            data = DataTuple("post", None, None, json_obj["token"], json_obj["post"]["entry"], json_obj["post"]["timestamp"], None, None)

        elif "bio" in json_obj:
            data = DataTuple("bio", None, None, json_obj["token"], json_obj["bio"]["entry"], json_obj["bio"]["timestamp"], None, None)

        elif "response" in json_obj:
            data = DataTuple("response", None, None, json_obj["response"]["token"] if "token" in json_obj["response"] else None, None, None, json_obj["response"]["type"], json_obj["response"]["message"] if "message" in json_obj["response"] else json_obj["response"]["messages"])
        
        return data

    except json.JSONDecodeError:
        print("Json cannot be decoded.")
        return False


def encode_json(command: str, username: str = None, password: str = None, token: str = None, entry: str = None, directmessage: dict = None) -> json:
    '''
    Call the json.dumps function on a dict to convert it to a json object
    :param command: the command to be sent to the server (join, post, bio, directmessage)
    :param username: the username (not needed if token provided)
    :param password: the password (not needed if token provided)
    :param token: unique user token server uses to identify you
    :param entry: message to be sent with either post or bio
    :param directmessage: a dictionary containing the entry, recipient, and timestamp

    :return: json with information wrapped to be sent to DS server
    '''
    # Encode information given in parameters into a json depending on the type of command
    if command == "join":
        data = {"join": {"username": username,"password": password, "token": token}}
        return json.dumps(data)

    elif command in ["post", "bio"]:
        data = {"token": token, command: {"entry": entry, "timestamp": time.time()}}
        return json.dumps(data)

    elif command == "directmessage":
        data = {"token": token, "directmessage": directmessage}
        return json.dumps(data)
