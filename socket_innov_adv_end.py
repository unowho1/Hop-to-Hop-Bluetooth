import socket
import threading
import time
import bluetooth
import queue

device_address="3C:91:80:31:9C:DE"

def receive_messages(recv_socket, message_buffer):
    while True:
        data = recv_socket.recv(1024)
        message_buffer.put(data)
        print("Incoming message : ",data.decode('utf-8'))
        if (data.decode('utf-8')=='-1'):
            break

    recv_socket.close()

def send_messages(send_socket, message_buffer):
    while True:
        try:
            message = message_buffer.get(block=True, timeout=1)
            print("Outgoing message : ",message.decode('utf-8'))
            if (message.decode('utf-8')=='-1'):
                break
            send_socket.send(message)
        except queue.Empty:
            pass 

    send_socket.close()

def handle_client(client_socket, client_info):
    try:
        check=client_socket.recv(1024).decode('utf-8')
        if check.split(' ')[0]!=device_address:
            if(check.split(' ')[1]=='0'):
                client_socket.send('No'.encode('utf-8'))
                print("Limit Exceeded")
                client_socket.close()
                return
            else:
                check=check.split(' ')[0]+" "+str(int(check.split(' ')[1])-1)
                pass
            scan_int(check,client_socket)
            # send_socket,end_device=start_client(check,1)
            # if not end_device:
            #     status=send_socket.recv(1024).decode('utf-8')
            #     if(status!="Yes"):
            #         client_socket.send("No".encode('utf-8'))
            #         client_socket.close()
            #         send_socket.close()
            #     else:
            #         client_socket.send("Yes".encode('utf-8'))
            #         #sujal code
            #         print("Connection established")
            #         message_buffer = queue.Queue()
            #         recv_thread = threading.Thread(target=receive_messages,args=(client_socket,message_buffer))
            #         recv_thread.start()
            #         send_thread = threading.Thread(target=send_messages,args=(send_socket,message_buffer))
            #         send_thread.start()
            #         recv_thread.join()
            #         send_thread.join()
            #         print("Connection between both ended")
            # else:
            #     client_socket.send("Yes".encode('utf-8'))
            #     #sujal code
            #     print("Connection established")
            #     message_buffer = queue.Queue()
            #     recv_thread = threading.Thread(target=receive_messages,args=(client_socket,message_buffer))
            #     recv_thread.start()
            #     send_thread = threading.Thread(target=send_messages,args=(send_socket,message_buffer))
            #     send_thread.start()
            #     recv_thread.join()
            #     send_thread.join()
            #     print("Connection between both ended")
        else:
            client_socket.send("Yes".encode('utf-8'))
            while True:
                data = client_socket.recv(1024)
                if (data.decode('utf-8')=='-1'):
                    break
                print(f"Received from {client_info}: {data.decode('utf-8')}")
            print(f"Client {client_info} disconnected.")
            client_socket.close()
    except OSError:
        pass

    # print(f"Client {client_info} disconnected.")
    # client_socket.close()

def start_server():
    port=11
    temp_socket=socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    temp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    temp_socket.bind((device_address, port))
    temp_socket.listen(1)
    server_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((device_address, 10))
    # server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    # server_socket.bind(("3C:91:80:31:9C:DE", bluetooth.PORT_ANY))
    # bluetooth.advertise_service(
    #     server_socket,
    #     "MyBluetoothServer"
    # )
    server_socket.listen(1)
    
    print(f"Server: Waiting for connection on RFCOMM channel 10")

    while True:
        client_socket, client_info = server_socket.accept()
        print(f"Server: Accepted connection from {client_info}")
        client_socket.send(str(port).encode('utf-8'))
        client_socket, client_info = temp_socket.accept()
        print(f"Server: Assigning {client_info} to port",port)
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_info))
        client_handler.start()
        port+=1
        temp_socket=socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        temp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        temp_socket.bind((device_address, port))
        temp_socket.listen(1)

def scan():
    print("Scanning for bluetooth devices:")
    devices = bluetooth.discover_devices(lookup_names = True, lookup_class = True)
    number_of_devices = len(devices)
    print(number_of_devices,"devices found")
    i=1
    for addr, name, device_class in devices:
        print(str(i)+". Device Name and MAC address: %s %s" % (name,addr))
        print("\n")
        i+=1
    i=-1
    while(i<1 or i>len(devices)):
        i=int(input("Enter device : "))
        if(i==0):
            return "3C:91:80:31:9C:DE"
        if(i<1 or i>len(devices)):
            print("Invalid Input!! Enter again")
    return devices[i-1][0]

def scan_int(dest,client_socket):
    print("Scanning for bluetooth devices:")
    devices = bluetooth.discover_devices(lookup_names = True, lookup_class = True)
    number_of_devices = len(devices)
    print(number_of_devices,"devices found")
    i=1
    for addr, name, device_class in devices:
        print(str(i)+". Device Name and MAC address: %s %s" % (name,addr))
        print("\n")
        i+=1
    connections=eval(input("Enter device : "))
    if(type(connections)==int):
        connections=[connections]
    print(connections)
        # if(i==0):
        #     return "3C:91:80:31:9C:DE"
        # if(i<1 or i>len(devices)):
        #     print("Invalid Input!! Enter again")
    shared_bool=threading.Event()
    threads=[]
    for k in connections:
        client_thread = threading.Thread(target=start_client_int,args=(dest,devices[int(k)-1][0],client_socket,shared_bool))
        threads.append(client_thread)
        client_thread.start()
    for thread in threads:
        thread.join()
    if(not shared_bool.is_set()):
        client_socket.send('No'.encode('utf-8'))
        print("No connection formed at this server")
    print(f"Client disconnected.")
    client_socket.close()

def start_client_int(dest,hop,client_socket,shared_bool):
    server_address =  hop
    print(hop)

    send_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    if(server_address=="18:54:CF:2A:C6:22" and dest.split(' ')[0]==hop):
        while True:
            try:
                send_socket.settimeout(2)
                send_socket.connect((server_address,1))
                break
            except socket.timeout:
                if(shared_bool.is_set()):
                    print("Terminating Connection with",hop)
                    return
        if(shared_bool.is_set()):
            print("Terminating Connection with",hop)
            send_socket.close()
            return
        shared_bool.set()
        client_socket.send("Yes".encode('utf-8'))
    else:
        while True:
            try:
                send_socket.settimeout(2)
                send_socket.connect((server_address,10))
                break
            except socket.timeout:
                if(shared_bool.is_set()):
                    print("Terminating Connection with",hop)
                    return
        send_socket.settimeout(60)
        data = send_socket.recv(1024)
        send_socket.close()
        data=data.decode('utf-8')
        time.sleep(2)
        send_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        send_socket.connect((server_address,int(data)))
        # print("Client: Assigned to port",data,"by",server_address)
        send_socket.send(dest.encode('utf-8'))
        data='No'
        while True:
            try:
                send_socket.settimeout(2)
                data=send_socket.recv(1024).decode('utf-8')
                break
            except socket.timeout:
                if(shared_bool.is_set()):
                    print("Terminating Connection with",hop)
                    return
        if(shared_bool.is_set()):
            print("Terminating Connection with",hop)
            send_socket.close()
            return
        shared_bool.set()
        if(data=='Yes'):
            client_socket.send("Yes".encode('utf-8'))
        else:
            print("Connection not formed by thread")
            return
    #sujal code
    print("Connection established")
    message_buffer = queue.Queue()
    recv_thread = threading.Thread(target=receive_messages,args=(client_socket,message_buffer))
    recv_thread.start()
    send_thread = threading.Thread(target=send_messages,args=(send_socket,message_buffer))
    send_thread.start()
    recv_thread.join()
    send_thread.join()
    print("Connection between both ended")

def start_client(dest,type,ct=-1):
    server_address = "3C:91:80:31:9C:DE"  

    client_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    if(server_address.split(' ')[0]=="18:54:CF:2A:C6:22" and type==1):
        client_socket.connect((server_address,1))
        return client_socket,1
    else:
        client_socket.connect((server_address,10))
    # client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    # client_socket.connect((server_address, 4))
    # if(type==1):
    #     return client_socket
    if(ct==1):
        try:
            while True:
                message = input("Client: Enter message to send (or '-1' to quit): ")
                client_socket.send(message.encode('utf-8'))
                if message.lower() == '-1':
                    break

        except OSError:
            client_socket.close()
            return
    data = client_socket.recv(1024)
    client_socket.close()
    data=data.decode('utf-8')
    time.sleep(2)
    client_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    client_socket.connect((server_address,int(data)))
    print("Client: Assigned to port",data,"by",server_address)
    client_socket.send(dest.encode('utf-8'))
    if(type==1):
        return client_socket,0
    
    signal='-1'
    signal=client_socket.recv(1024).decode('utf-8')
    if(signal!='Yes'):
        print("Connection not formed")
        return

    try:
        while True:
            message = input("Client: Enter message to send (or '-1' to quit): ")
            client_socket.send(message.encode('utf-8'))
            if message.lower() == '-1':
                break

    except OSError:
        pass

    client_socket.close()

if __name__ == "__main__":
    s=int(input("Want to initialize server:"))
    if(s==1):
        server_thread = threading.Thread(target=start_server)
        server_thread.start()
        time.sleep(1)
    c=int(input("Want to initialize client:"))
    if(c==1):    
        destination_addresses=["18:54:CF:2A:C6:22"]
        # destination_addresses=["64:6e:69:dd:dd:ba 3"]
        threads=[]
        for addr in destination_addresses:
            client_thread = threading.Thread(target=start_client,args=(addr,0))
            threads.append(client_thread)
        for thread in threads:
            thread.start()

    if(c==1):
        client_thread.join()
    if(s==1):
        server_thread.join()
