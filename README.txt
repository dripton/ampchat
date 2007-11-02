This is a simple chat program using the AMP protocol, to demonstrate how to
coordinate multiple protocol instances. 

Requires Twisted 2.5+, PyGTK 2.2+

Run "python chatserver.py" in one terminal.

Run "python chatclient.py" in a couple of other terminals, on remote machines
if you want.

Go to File/Connect.  Put in the machine name of the server, and a valid 
username and password.  (They're in passwd.txt; feel free to add more.)

Type in the text entry to send public messages.  Click on a user's name first 
to send private messages to that user.  Control-click on the selected user's
name to unselect it.
