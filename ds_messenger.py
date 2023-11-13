import time
import socket
import ds_protocol
import json



class DirectMessage(dict):
    """
    Class to hold direct message information. Inherits from dict to support saving to local device.
    """
    def __init__(self, recipient: str = None, message: str = None, timestamp: str = time.time()):
        self.recipient = recipient
        self.message = message
        self.timestamp = timestamp
        
        # Subclass dict to enable serialization
        dict.__init__(self, recipient=self.recipient, message=self.message, timestamp=self.timestamp)

class User(dict):
    """
    Class to hold information on messages sent to and from a specific user. Inherits from dict to support saving to local device.
    """
    def __init__(self, name):
        self.name = name
        self._messages = []

        # Subclass dict to enable serialization
        dict.__init__(self, name=self.name, messages=self._messages)

    def add_message(self, message: str, timestamp: str = time.time(), sent_by_user: bool = False) -> None:
        """
        Adds a message into the user message list as a dict

        :param message: message to be stored
        :param timestamp: timestamp of the message
        """
        self._messages.append({"message": message, "timestamp": timestamp, "sent by user": sent_by_user})

        # Subclass dict to enable serialization
        dict.__setitem__(self, 'messages', self._messages)

    def get_messages(self) -> list[dict]:
        """
        Returns a list of message dicts from user

        :return: list of message dicts
        """
        return self._messages


class DirectMessenger:
    """
    Class to support sending messages to and from a remote server.
    """
    def __init__(self, dsuserver: str = "168.235.86.101", port: int = 3021, username: str = None, password: str = None):
        self.dsuserver = dsuserver
        self.port = port
        self.username = username
        self.password = password

        if not self.get_token():
            print("Token was unable to be retrieved.")

    def get_token(self) -> bool:
        """
        Retrieves the unique user token from the server.

        :return: True if token was successfully retrieved, False otherwise
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            # Try to connect to the provided server IP and port
            try:
                client.connect((self.dsuserver, self.port))
            except socket.error:
                print("Could not connect to server. Check your IP and Port.")
                return False

            # Create the abstraction files
            send = client.makefile('w')
            recv = client.makefile('r')

            # Join the server with username and password
            # Encode the data
            try:
                data = ds_protocol.encode_json("join", self.username, self.password, '')
            except:
                print("Join data could not be encoded to json.")
                return False

            # Send the data
            try:
                send.write(data)
                send.flush()
            except:
                print("An error occurred while trying to join the server.")
                return False

            # Receive server response and extract token
            srv_msg = recv.readline()
            srv_data = ds_protocol.extract_json(srv_msg)

            # Will evaluate true if extracting encountered a JSONDecodeError
            if not srv_data:
                return False

            # If server responds with an error then print error and return False
            if srv_data.response_type == "error":
                print("Invalid password or username already taken.")
                return False

            self.token = srv_data.token

        return True
		
    def send(self, recipient:str, message:str, profile = None) -> bool:
        """
        Sends a message to a recipient through the DSU server

        :param message: the message to be sent
        :param recipient: the recipient of the message

        :return: True if the message was successfully sent, False otherwise
        """
        message_obj = DirectMessage(recipient, message)
        message_dict = {"entry": message_obj.message, "recipient": message_obj.recipient, "timestamp": message_obj.timestamp}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            # Try to connect to the provided server IP and port
            try:
                client.connect((self.dsuserver, self.port))
            except socket.error:
                print("Could not connect to server. Check your IP and Port.")
                return False

            # Create the abstraction files
            send = client.makefile('w')
            recv = client.makefile('r')

            # Encode the message and recipient
            try:
                data = ds_protocol.encode_json("directmessage", token=self.token, directmessage=message_dict)
            except:
                print("Direct message could not be encoded to json.")
                return False

            # Send the data
            try:
                send.write(data)
                send.flush()
            except:
                print("An error occurred while sending the message to the server.")
                return False

            # Receive server response
            srv_msg = recv.readline()
            srv_data = ds_protocol.extract_json(srv_msg)

            # Will evaluate true if extracting encountered a JSONDecodeError
            if not srv_data:
                return False

            # If server responds with an error then print error and return False
            if srv_data.response_type == "error":
                print("Message could not be sent.")
                return False

        # Add our sent message into our profile object
        profile.add_message(our_message=message_obj)

        # Return True if no operation failed
        return True
		
    def retrieve_new(self, to_retrieve: str = "new") -> list:
        """
        Retrieves all new messages from the server.

        :param to_retrieve: prevents redundancy, retrieve_all will call this method with the "all" argument instead

        :return: list of new messages
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            # Try to connect to the provided server IP and port
            try:
                client.connect((self.dsuserver, self.port))
            except socket.error:
                print("Could not connect to server. Check your IP and Port.")
                return None

            # Create the abstraction files
            send = client.makefile('w')
            recv = client.makefile('r')

            # Encode the message and recipient
            try:
                data = ds_protocol.encode_json("directmessage", token=self.token, directmessage=to_retrieve)
            except:
                print("Direct message could not be encoded to json.")
                return None

            # Send the data
            try:
                send.write(data)
                send.flush()
            except:
                print("An error occurred while sending the message to the server.")
                return None

            # Receive server response
            srv_msg = recv.readline()
            srv_data = ds_protocol.extract_json(srv_msg)

            # Will evaluate true if extracting encountered a JSONDecodeError
            if not srv_data:
                return None

            # If server responds with an error then print error and return False
            if srv_data.response_type == "error":
                print("Message could not be sent.")
                return None

        # Return True if no operation failed
        return srv_data.response_message
 
    def retrieve_all(self) -> list:
        """
        Retrieves all messages from the server.

        :return: list of all messages
        """
        # Calls the retreive_new method with agument "all" instead of default "new"
        return self.retrieve_new(to_retrieve="all")