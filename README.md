# UDP-based-Multithreaded-client-server

On execution, there are two main options:

## *Sender mode*
In the Sender mode, users initiate communication with multiple clients. The process involves providing the IP address of the clients, selecting the number of clients, and inputting their respective ports. Upon establishing connections, the server offers three options:
* **End the Connection:**
  * Terminate the connection between the server and clients.
* **Send a Text Message:**
  * Allows the server to send messages individually to each connected client.
* **Send a File:**
  * Permits the server to send different files to each client individually.
  * Prompts the server to specify the file location before transmission.


## *Receiver mode*
* All clients share the same IP address but have different ports.
* Users manually input the client's port for communication.
* Clients can receive individual messages from the server but are unable to send messages back.
* Clients can receive files from the server and choose their own storage location.


## UDP Protocol
The User Datagram Protocol (UDP) is a connectionless, lightweight communication protocol that operates on the transport layer of the Internet Protocol (IP) suite. It is known for its simplicity and speed, making it suitable for applications where low latency and real-time data transmission are crucial.

## TFTP Protocol
The Trivial File Transfer Protocol (TFTP) is a simple, lockstep file transfer protocol that uses the UDP protocol for data transmission. TFTP is commonly employed for transferring files between devices on a network, especially in scenarios where a more robust protocol like FTP may be impractical.
