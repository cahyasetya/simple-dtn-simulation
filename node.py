import socket
import threading
from datetime import datetime, timedelta
import json
from uuid import getnode

buffer=[]
pesanditerima=[]

def send_message_thread(sock):
    while True:
        print
        tujuan=raw_input("Masukkan ip tujuan:")
        pesan=raw_input("Masukkan pesan:")
        maxHop=raw_input("Masukkan maksimal hop:")
        ttl=raw_input("Masukkan Ttl:")

        msg=createMessage(tujuan,pesan,maxHop,ttl)
        sock.sendto(msg,("255.255.255.255",9000))
        buffer.append(msg)

def recv_message_thread(sock):
    while True:
        data,address=sock.recvfrom(1048)
        print data
        msg=json.loads(data)

        if msg['id']==getnode():
            print "pesan yang sama"
            print "mengabaikan pesan"
        elif msg['dst_address']==socket.gethostbyname(socket.gethostname()):
            if msg['id'] in pesanditerima:
                print "pesan pernah diterima, mengabaikan"
            else:
                print msg['pesan']
                pesanditerima.append(msg['id'])
        else:
            ada=False
            for d in buffer:
                if d['id']==msg['id']:
                    ada=True
                    print "duplikat pesan"
            if ada==False:
                if msg['hop']<msg['max_hop']:
                    print "menambahkan ke buffer"
                    buffer.append(msg)
                    sock.sendto(data, ('255.255.255.255',9000))
                else:
                    print "max hope reached"

def createMessage(dst_address,pesan,max_hop,ttl):
    mac=getnode()
    tanggal_buat=datetime.now()
    hop=1

    msg=json.dumps({'id':mac,'dst_address':dst_address,'tanggal_buat':str(tanggal_buat),'hop':hop,'pesan':pesan,'max_hop':max_hop,'ttl':ttl})
    return msg

def broadcast(sock):
    for msg in buffer:
        ori=msg;
        waktu_sekarang=datetime.now()
        msg=json.loads(msg)
        print msg["tanggal_buat"]
        waktu_dibuat=datetime.strptime(msg['tanggal_buat'], '%Y-%m-%d %H:%M:%S.%f')
        if waktu_sekarang-waktu_dibuat>timedelta(seconds=long(msg['ttl'])):
            print "paket dengan id: %s timeout, membuang paket"%(msg['id'])
            buffer.remove(ori)
            print "buffer menjadi ", buffer
        else:
            print "mengirim paket ke ", msg['dst_address']
            sock.sendto(json.dumps(msg),("255.255.255.255",9000))

    t=threading.Timer(5.0,broadcast,[sock])
    t.start()

if __name__=="__main__":

    server_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_address=("192.168.1.15",9000)
    server_socket.bind(server_address)

    t=threading.Timer(5.0,broadcast,[server_socket])

    threading.Thread(target=send_message_thread,args=(server_socket,)).start()
    threading.Thread(target=recv_message_thread,args=(server_socket,)).start()
    t.start()