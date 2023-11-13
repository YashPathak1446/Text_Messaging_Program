from Profile import Profile
from ds_messenger import DirectMessenger


PATH = "C:\\Users\\zyrat\\Documents\\Desktop\\college\\classes\\ics32\\programs\\final project\\testing\\test.dsu"
current_profile = Profile("dsu_test", "username_test", "pass_test")

def test_new_file():
    global current_profile

    new_messages = [{'message': 'Hello World!', 'from': 'bob5896', 'timestamp': '1647149883.77518'}, 
                    {'message': 'second', 'from': 'bob5896', 'timestamp': '1647149908.18672'}, 
                    {'message': 'hi there', 'from': 'tom', 'timestamp': '1647149908.22928'}, 
                    {'message': 'hi again :)', 'from': 'tom', 'timestamp': '1647149929.78163'}, 
                    {'message': 'spaghetti', 'from': 'joe', 'timestamp': '1647149996.79552'}]

    current_profile.add_message(new_messages)

    for user in current_profile.get_users():
        print(user.get_messages())

    current_profile.save_profile(PATH)

def test_send_message():
    global current_profile

    messenger = DirectMessenger(username="3245", password="mypass")
    messenger.send("bob5896", "this is a test message", current_profile)

    current_profile.save_profile(PATH)

def test_open_file():
    global current_profile

    current_profile = Profile()
    current_profile.load_profile(PATH)

    for user in current_profile.get_users():
        print(user.get_messages())

if __name__ == "__main__":
    test_new_file()
    test_send_message()
    print()
    test_open_file()
