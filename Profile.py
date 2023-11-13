# Profile.py

# Ryan Zhang, Yash Pathak
# ryanyz@uci.edu, pathaky@uci.edu
# 20907746, 51317074

import json, time, os
from pathlib import Path
from ds_messenger import User, DirectMessage


"""
DsuFileError is a custom exception handler that you should catch in your own code. It
is raised when attempting to load or save Profile objects to file the system.

"""
class DsuFileError(Exception):
    pass

"""
DsuProfileError is a custom exception handler that you should catch in your own code. It
is raised when attempting to deserialize a dsu file to a Profile object.

"""
class DsuProfileError(Exception):
    pass

class Profile:
    def __init__(self, dsuserver="168.235.86.101", username="3245", password="mypass"):
        self.dsuserver = dsuserver
        self.username = username
        self.password = password
        self._users = []

    def add_user(self, user_name: str) -> None:
        """
        Adds a user to the profile

        :param user_name: name of user
        """
        user = User(user_name)
        self._users.append(user)

    def add_message(self, new_messages: list = None, our_message: DirectMessage = None) -> None:
        """
        Adds a message to the profile

        :param new_messages: list of new messages to be added into profile
        """
        # Message is a dictionary in format: {"message": x, "from": y, "timestamp": z}
        # Runs through every message
        if new_messages:
            for message in new_messages:
                # Iterates through every user to see if the message is from a known user
                found = False
                for user in self._users:
                    if message["from"] == user.name:
                        user.add_message(message["message"], message["timestamp"])
                        found = True
                        break

                # If no user found, create a new user
                if not found:
                    user = User(message["from"])
                    user.add_message(message["message"], message["timestamp"])
                    self._users.append(user)

        # Adds our own message instead
        if our_message:
            # Iterates through every user to see if the message sent is to a known user
            found = False
            for user in self._users:
                if our_message.recipient == user.name:
                    user.add_message(our_message.message, our_message.timestamp, True)
                    found = True
                    break

            # If no user found, create a new user
            if not found:
                user = User(message.recipient)
                user.add_message(our_message.message, our_message.timestamp, True)
                self._users.append(user)

    def get_users(self) -> list:
        """
        Gets messages stored in profile

        :return: list of stored messages
        """
        return self._users

    def save_profile(self, path: str) -> None:
        """
        Saves current Profile instace to the file system
        """
        p = Path(path)

        # Creates path if it doesn't exist
        if not os.path.exists(p) and p.suffix == '.dsu':
            p.touch()

        if os.path.exists(p) and p.suffix == '.dsu':
            # Tries to open the dsu file and dump all the data into it
            try:
                f = open(p, 'w')
                json.dump(self.__dict__, f)
                f.close()
            except Exception as ex:
                raise DsuFileError("An error occurred while attempting to process the DSU file.", ex)
        else:
            raise DsuFileError("Invalid DSU file path or type")

    def load_profile(self, path: str) -> None:
        """
        Populates the current instance of Profile with data stored in a DSU file
        """
        p = Path(path)

        if os.path.exists(p) and p.suffix == '.dsu':
            try:
                f = open(p, 'r')
                obj = json.load(f)
                
                # Set instance attributes to ones loadede from dsu file
                self.username = obj['username']
                self.password = obj['password']
                self.dsuserver = obj['dsuserver']
                for user_obj in obj['_users']:
                    user = User(user_obj["name"])
                    for message in user_obj["messages"]:
                        user.add_message(message["message"], message["timestamp"], message["sent by user"])
                    self._users.append(user)
                f.close()
            except Exception as ex:
                raise DsuProfileError(ex)
        else:
            raise DsuFileError()
