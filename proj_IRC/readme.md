This is the basic implementation of IRC Server/Client over TCP.
Currently only supports one server with many clients, capable of one-one and one-to-many communication  

To run:  
    - IRC_Server: Python IRC_Server.py [ip] [port] [server name]  
    - Client: Python Client.py [server ip] [server port] [Name]  
      
COMMAND_LIST = ['/join', '/msg', '/part', '/quit', '/list', 'help', '/create', '/names']    
Command Details:  
    **/msg:**  
        - syntax: /msg [target] : [message]  
        - desc: send a message to target, target is either a channel or a user  
    **/join:**  
        - syntax: /join [channel name]  
        - desc: joins the specified channel  
    **/part:**     
        - syntax: /part [channel name]  
        - desc: leaves the specified channel  
    **/quit:**   
        - syntax: /quit   
        - desc: exit the server    
    **/list:**  
        - syntax: /list
        - desc: display a list of existing channels  
    **/create:**  
        - syntax: /create [channel name]    
        - desc: create the channel with the specified name  
    **/names:**    
        - syntax: /names  
        - desc: display the list of online users  
  
Implementation Structure:  
    - IRC_Server: The main server class, handles all packet transfer  
    - irc_db: The database to keep track of all connections and channels, and delete records for user logging out  
    - Channel: The class that handles packets for in channel communication as well as user leaving  
    
Organization for irc_db:  
    - Users: store as bidirectional dictionary, allows to be able to access by name and socket  
    - ChannelList: organized using dictionary as name:Channel_Obj
    
Limitations:  
    - Lacks support for server network 
    - Lack authentication 
    - Require unique NICK for registration, which can be problematic when use for large user base  
  
Reference:  
[IRC RFC](https://tools.ietf.org/html/rfc2812#section-3.1.7)  
[Example of IRC Communication](http://chi.cs.uchicago.edu/chirc/irc_examples.html)
  