# gui.py

# Ryan Zhang, Yash Pathak
# ryanyz@uci.edu, pathaky@uci.edu
# 20907746, 51317074


# a5.py
# 
# ICS 32 
#
# v0.4
# 
# The following module provides a graphical user interface shell for the DSP journaling program.

# Ryan Zhang, Yash Pathak
# ryanyz@uci.edu, pathaky@uci.edu
# 20907746, 51317074

USERNAME = "3245"
PASSWORD = "mypass"

from audioop import add
from ctypes import alignment
import tkinter as tk
from tkinter import END, ttk, filedialog
from turtle import bgcolor, fillcolor
from Profile import Profile
from ds_messenger import User, DirectMessage, DirectMessenger


is_dark_mode = False

class Body(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the body portion of the root frame.
    """
    def __init__(self, root, select_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._select_callback = select_callback

        # a list of the User objects available in the active DSU file
        self._users = [User]
        
        # After all initialization is complete, call the _draw method to pack the widgets
        # into the Body instance 
        self._draw()
    
    def node_select(self, event=None):
        """
        Update the entry_editor with the full user entry when the corresponding node in the users_tree
        is selected.
        """
        index = int(self.users_tree.selection()[0])
        self.selected_user = self._users[index].name
        entry = self._users[index].get_messages()
        self.set_text_entry(entry, self.message_display_frame)

    def get_selected_user(self):
        return self.selected_user
    
    def get_text_entry(self) -> str:
        """
        Returns the text that is currently displayed in the entry_editor widget.
        """
        return self.entry_editor.get('1.0', 'end').rstrip()

    def set_text_entry(self, messages:list, entry:tk.Text):
        """
        Sets the text to be displayed in the entry_editor widget.
        NOTE: This method is useful for clearing the widget, just pass an empty string.
        """
        # Sets the message to the entry if it is not a list
        if type(messages) != list:
            entry.delete(0.0, 'end')
            entry.insert(0.0, messages)

        # If list, only enter the actual messages and not timestamps, etc.
        elif type(messages) == list:
            entry.delete(0.0, 'end')

            for message in messages[::-1]:
                # Make the background black if the message was sent by the local user
                if message["sent by user"]:
                    entry.tag_config('user', background="black", foreground="white")
                    entry.insert(0.0, f"{message['message']}\n",'user')
                # Messages sent by remote users are in white background
                else:
                    entry.insert(0.0, f"{message['message']}\n")
    
    def set_users(self, users:list):
        """
        Populates the self._users attribute with users from the active DSU file.
        """
        self._users = users
        # Inserts each user in the user tree from the users list along with its user id
        for user_id in range(len(self._users)):
            self._insert_user_tree(user_id, self._users[user_id])

    def insert_user(self, user: User):
        """
        Inserts a single user to the user_tree widget.
        """
        self._users.append(user)
        id = len(self._users) - 1 #adjust id for 0-base of treeview widget
        self._insert_user_tree(id, user)

    def reset_ui(self):
        """
        Resets all UI widgets to their default state. Useful for when clearing the UI is neccessary such
        as when a new DSU file is loaded, for example.
        """
        self.set_text_entry("", self.message_display_frame)
        self.entry_editor.configure(state=tk.NORMAL)
        self._users = []
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

    def _insert_user_tree(self, id, user: User):
        """
        Inserts a user entry into the users_tree widget.
        """
        entry = user.name
        # Since we don't have a title, we will use the first 24 characters of a
        # user entry as the identifier in the user_tree widget.
        if len(entry) > 25:
            entry = entry[:24] + "..."
        
        self.users_tree.insert('', id, id, text=entry, tags=("a",))
    
    def _draw(self):
        """
        Call only once upon initialization to add widgets to the frame
        """
        global is_dark_mode
        bg_black = "black" if is_dark_mode else "white"
        bg_gray = "gray" if is_dark_mode else "white"

        ttk.Style(self.root).configure("Treeview", background=bg_gray, fieldbackground=bg_gray) 

        users_frame = tk.Frame(master=self, width=250)
        users_frame.pack(fill=tk.BOTH, side=tk.LEFT)

        self.users_tree = ttk.Treeview(users_frame, style="Treeview")
        # self.users_tree.tag_configure("a", background=bg_gray)
        self.users_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.users_tree.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(master=self, bg=bg_black)
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        
        editor_frame = tk.Frame(master=entry_frame, bg=bg_black)
        editor_frame.pack(fill=tk.X, side=tk.BOTTOM, expand=False, padx=5, pady=5)
        
        self.entry_editor = tk.Text(editor_frame, height=5, width=0, bg=bg_gray)
        self.entry_editor.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=5, pady=5)

        self.message_display_frame = tk.Text(master=entry_frame, bg=bg_gray)
        self.message_display_frame.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True, padx=5, pady=5)


class Footer(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the footer portion of the root frame.
    """
    def __init__(self, root, send_callback=None, add_user_callback=None, dark_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._send_callback = send_callback
        self._add_user_callback = add_user_callback
        self._dark_callback = dark_callback
        self.is_dark_mode = tk.IntVar()

        # After all initialization is complete, call the _draw method to pack the widgets
        # into the Footer instance 
        self._draw()

    def dark_click(self):
        self._dark_callback(self.is_dark_mode.get())
    
    def send_click(self):
        """
        Calls the callback function specified in the send_callback class attribute, if
        available, when the send_button has been clicked.
        """
        if self._send_callback is not None:
            self._send_callback()

    def add_user_click(self):
        """
        Calls the callback function specified in the add_callback class attribute, if
        available, when the ass_button has been clicked.
        """
        if self._add_user_callback is not None:
            self._add_user_callback()
    
    def _draw(self):
        """
        Call only once upon initialization to add widgets to the frame
        """
        global is_dark_mode
        bg_black = "black" if is_dark_mode else "white"
        bg_gray = "gray" if is_dark_mode else "white"

        send_button = tk.Button(master=self, text="Send", width=20, bg=bg_gray)
        send_button.configure(command=self.send_click)
        send_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx=5, pady=5)

        add_button = tk.Button(master=self, text="Add User", width=20, bg=bg_gray)
        add_button.configure(command=self.add_user_click)
        add_button.pack(fill=tk.BOTH, side=tk.LEFT, padx=5, pady=5)

        self.chk_button = tk.Checkbutton(master=self, text="Activate Dark Mode", variable=self.is_dark_mode)
        self.chk_button.configure(command=self.dark_click) 
        self.chk_button.pack(fill=tk.BOTH, side=tk.BOTTOM)

class MainApp(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the main portion of the root frame. Also manages all method calls for
    the NaClProfile class.
    """
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self._is_dark_mode = False
        # Initialize a new NaClProfile and assign it to a class attribute.
        self._current_profile = Profile()

        # After all initialization is complete, call the _draw method to pack the widgets
        # into the root frame
        self._draw()

    def new_profile(self):
        """
        Creates a new DSU file when the 'New' menu item is clicked.
        """
        filename = tk.filedialog.asksaveasfile(filetypes=[('Distributed Social Profile', '*.dsu')])
        self._profile_filename = filename.name

        self._current_profile = Profile()
        self.body.reset_ui()
    
    def open_profile(self):
        """
        Opens an existing DSU file when the 'Open' menu item is clicked and loads the profile
        data into the UI.
        """
        filename = tk.filedialog.askopenfile(filetypes=[('Distributed Social Profile', '*.dsu')])

        self._profile_filename = filename.name
        self._current_profile = Profile()

        # Load the profile and import the path
        self._current_profile.load_profile(self._profile_filename)

        self.body.reset_ui()

        # Populate the GUI with loaded users
        self.body.set_users(self._current_profile.get_users())
    
    def close(self):
        """
        Closes the program when the 'Close' menu item is clicked.
        """
        self.root.destroy()

    def dark_changed(self, value:bool):
        global is_dark_mode
        is_dark_mode = True if value == 1 else False
        self.body.destroy()
        self.footer.destroy()
        self._draw()

    def add_user(self):
        """
        Creates a new window that prompts for a new user's name. Saves the user into the current profile and treeview.
        """
        # Create the window
        add = tk.Toplevel()
        add.title('Add New User')
        add.geometry("250x70")

        # Add the text box
        username_editor = tk.Text(add, height=1)
        username_editor.pack(fill=tk.X, side=tk.TOP, expand=False, padx=5, pady=5)

        # Add the save button
        save_button = tk.Button(master=add, text="Save New User", width=12)
        save_button.configure(command=lambda:self.save_user(username_editor.get('1.0', 'end').rstrip(), add))
        save_button.pack(side=tk.TOP, padx=5, pady=5)

        add.update()
        add.minsize(add.winfo_width(), add.winfo_height())

    def save_user(self, user_name: str, to_destroy):
        """
        Saves the new username. Also destroys the add_user popup window.
        """
        self.body.insert_user(User(user_name))
        self._current_profile._users = self.body._users
        self._current_profile.save_profile(self._profile_filename)

        # Destroy window
        to_destroy.destroy()

    def send_message(self):
        """
        Sends a message when the Send button is clicked.
        """
        # Get the selected user, otherwise don't run the method
        try:
            selected_user = self.body.get_selected_user()
        except AttributeError:
            return
        else:
            # Get the message from the text box
            message_to_send = self.body.entry_editor.get('1.0', 'end').rstrip()
            
            # Only send the message if it is not empty or only whitespace
            if not message_to_send.isspace() and message_to_send != "":
                # Clear the text box
                self.body.set_text_entry("", self.body.entry_editor)

                # Create the messenger object to send the message
                messenger_obj = DirectMessenger(username=USERNAME, password=PASSWORD)
                messenger_obj.send(selected_user, message_to_send, self._current_profile)
                
                # Update the GUI's users with the profile's after sending
                self.body._users = self._current_profile.get_users()

                self._current_profile._users = self.body._users
                self._current_profile.save_profile(self._profile_filename)

                # Update the node containing messages
                self.body.node_select()

    def _draw(self):
        """
        Call only once, upon initialization to add widgets to root frame
        """
        # Build a menu and add it to the root frame.
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='New', command=self.new_profile)
        menu_file.add_command(label='Open...', command=self.open_profile)
        menu_file.add_command(label='Close', command=self.close)

        # The Body and Footer classes must be initialized and packed into the root window.
        self.body = Body(self.root, self._current_profile)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        
        self.footer = Footer(self.root, self.send_message, self.add_user, self.dark_changed)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)

    def check_new_messages(self):
        """
        Checks new messages from the remote server. Will run every 1 second in the main loop.
        """
        try:
            # Create messenger object
            messenger_obj = DirectMessenger(username=USERNAME, password=PASSWORD)
            new_messages = messenger_obj.retrieve_new()

            # If new messages isn't blank (there are messages)
            if new_messages:
                # Add the messages into the current profile
                self._current_profile.add_message(new_messages=new_messages)
                self._current_profile.save_profile(self._profile_filename)

                # Refresh the node with new messages
                self.body.node_select()
        except:
            print("Could not load new messages.")
        finally:
            self.root.after(1000, self.check_new_messages)


if __name__ == "__main__":
    # All Tkinter programs start with a root window. We will name ours 'main'.
    main = tk.Tk()
    style = ttk.Style(main)
    style.theme_use("default")

    # 'title' assigns a text value to the Title Bar area of a window.
    main.title("ICS 32 Distributed Social Demo")

    # This is just an arbitrary starting point. You can change the value around to see how
    # the starting size of the window changes. I just thought this looked good for our UI.
    main.geometry("720x540")
    
    # adding this option removes some legacy behavior with menus that modern OSes don't support. 
    # If you're curious, feel free to comment out and see how the menu changes.
    main.option_add('*tearOff', False)

    # Initialize the MainApp class, which is the starting point for the widgets used in the program.
    # All of the classes that we use, subclass Tk.Frame, since our root frame is main, we initialize 
    # the class with it.
    app = MainApp(main)

    # When update is called, we finalize the states of all widgets that have been configured within the root frame.
    # Here, Update ensures that we get an accurate width and height reading based on the types of widgets
    # we have used.
    # minsize prevents the root window from resizing too small. Feel free to comment it out and see how
    # the resizing behavior of the window changes.
    main.update()
    main.minsize(main.winfo_width(), main.winfo_height())

    # Timer event to get new messages automatically
    main.after(1000, app.check_new_messages)

    # And finally, start up the event loop for the program (more on this in lecture).
    main.mainloop()