from ds_messenger import DirectMessenger

messenger = DirectMessenger(username="3245", password="mypass")

messenger.send("3245", "this is a test message")
print(messenger.retrieve_new())
print(messenger.retrieve_all())