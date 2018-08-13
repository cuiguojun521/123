# import socket
# import json
# sk = socket.socket()
# sk.connect(('127.0.0.1', 9999))
#
# count = 0
# def login():
#     global count
#     while count < 3:
#         username = input('请输入账号：')
#         password = input('请输入密码：')
#         dic = {'username': username, 'password': password}
#         str_dic = json.dumps(dic)
#         sk.send(str_dic.encode('utf-8'))
#         msg_r = sk.recv(1024).decode('utf-8')
#         if msg_r == '登录成功':
#             print('登录成功')
#         else:
#             print('登录失败，请重新输入！')
#             count += 1
# login()



import socket
import os, json, sys


class Myclient(object):
    def __init__(self, ip_port):
        self.client = socket.socket()
        self.ip_port = ip_port

    def connect(self):
        self.client.connect(self.ip_port)

    def start(self):
        self.connect()
        while True:
            username = input('输入用户名:').strip()
            password = input('输入密码:').strip()
            login_info = '%s:%s' % (username, password)
            self.client.sendall(login_info.encode())
            status_code = self.client.recv(1024).decode()
            if status_code == '400':
                print('[%s] 用户密码错误！' % status_code)
            elif status_code == '200':
                print('[%s] 登录成功！' % status_code)
                self.interactive()

    def interactive(self):
        while True:
            command = input('-->').strip()
            if not command: continue
            command_str = command.split()[0]
            if hasattr(self, command_str):
                func = getattr(self, command_str)
                func(command)

    def get(self, command):
        self.client.sendall(command.encode())
        status_code = self.client.recv(1024).decode()
        if status_code == '201':
            filename = command.split()[1]
            print(filename)
            if os.path.isfile(filename):
                self.client.sendall('403'.encode())
                revice_size = os.stat(filename).st_size
                response = self.client.recv(1024)
                self.client.sendall(str(revice_size).encode())
                status_code = self.client.recv(1024).decode()
                print('-----------------')
                if status_code == '205':
                    print('[%s] 续传' % status_code)
                    self.client.sendall('000'.encode())
                elif status_code == '405':
                    print('[%s] 文件一致。' % status_code)
                    return
            else:
                self.client.sendall('402'.encode())
                revice_size = 0

            file_size = self.client.recv(1024).decode()
            file_size = int(file_size)
            response = self.client.sendall('000'.encode())
            with open(filename, 'ab') as file:
                while revice_size != file_size:
                    data = self.client.recv(1024)
                    revice_size += len(data)
                    file.write(data)
                    self.__progress(revice_size, file_size, '下载中')
        else:
            print('[%s] Error!' % status_code)

    def put(self, command):
        if len(command.split()) > 1:
            filename = command.split()[1]
            if os.path.isfile(filename):
                self.client.sendall(command.encode())
                response = self.client.recv(1024)
                file_size = os.stat(filename).st_size
                self.client.sendall(str(file_size).encode())
                status_code = self.client.recv(1024).decode()
                if status_code == '202':
                    with open(filename, 'rb') as file:
                        for line in file:
                            send_size = file.tell()
                            self.client.sendall(line)
                            self.__progress(send_size, file_size, '上传中')

                elif status_code == '404':
                    print('[%s] Error!' % status_code)

            else:
                print('[401] Error!')

    def dir(self, command):
        self.__universal_method_data(command)

    def pwd(self, command):
        self.__universal_method_data(command)

    def mkdir(self, command):
        self.__universal_method_none(command)

    def cd(self, command):
        self.__universal_method_none(command)

    def __universal_method_none(self, command):
        self.client.sendall(command.encode())
        status_code = self.client.recv(1024).decode()
        if status_code == '201':
            self.client.sendall('000'.encode())

        else:
            print('[%s] Error!' % status_code)

    def __universal_method_data(self, command):
        self.client.sendall(command.encode())
        status_code = self.client.recv(1024).decode()
        print(status_code)
        if status_code == '201':
            self.client.sendall('000'.encode())
            result = self.client.recv(1024).decode()
            print(result)
        else:
            print('[%s] Error!' % status_code)

    def __progress(self, trans_size, file_size, mode):
        bar_length = 100
        percent = float(trans_size) / float(file_size)
        hashes = '=' * int(percent * bar_length)
        spaces = ' ' * int(bar_length - len(hashes))
        sys.stdout.write('\r%s:%.2fM/%.2fM %d%% [%s]' \
                         % (mode, trans_size / 1048576, file_size / 1048576, percent * 100, hashes + spaces))


if __name__ == '__main__':
    client = Myclient(('localhost', 8000))
    client.start()




