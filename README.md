# silly-spying
A silly python client &amp; server script I wrote to troll my friend. **Please, do not use it for harmful purposes!**

# How it works?
The idea is quite simple, the target computer opens a socket server, and accepts connections to it.
The client then can send 4 different events:
  0 - Exit;
  1 - Key event (1 byte, `0bkkkkkkkp`, where k is for key index, and p is for boolean pressed variable);
  2 - Mouse event (4 bytes xy coordinates and 1 byte for mouse buttons: `0blr`, l - left, r - right);
  3 - Screenshot request (1 byte, `0bqqqqqqqp`, where q stands for quality level (0-90), and p for format (JPEG or PNG));
  
The server accepts these events and then processes them.
The client on the other hand, just constantly requests screen frame each 3 frames, and listents to the window events to send after.
And that's pretty much it.

As I've already said, please, **do not use it for harmful purposes**. Thanks.
