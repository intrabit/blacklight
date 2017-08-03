import socket
import threading
import recipebot.Settings as settings
import gzip
import re
import ssl


class Worker(threading.Thread):
    def __init__(self, links):
        threading.Thread.__init__(self)
        self.worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.worker_socket.settimeout(settings.CONNECTION_TIMEOUT)
        self.links = links
        self.encrypted = False

    def run(self):
        while True:
            self.processlink()

    # Connects to a server with either https or http and returns the html code for the page provided.
    def request(self, target, resource, encrypted):
        if encrypted and not self.encrypted:
            self.worker_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            self.encrypted = True
        elif not encrypted and self.encrypted:
            self.worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.encrypted = False
        self.worker_socket.settimeout(settings.CONNECTION_TIMEOUT)
        port = 443 if encrypted else 80
        self.worker_socket.connect((socket.gethostbyname(target), port))
        request = "GET " + resource + " HTTP/1.1\r\n" + "User-Agent: Blacklight/" + \
                  settings.VERSION + "\r\nHost: " + target +\
                  "\r\nAccept-Language: en-us\r\nAccept-Encoding: gzip\r\n\r\n"
        self.worker_socket.send(request.encode(settings.DEFAULT_ENCODING))
        encoded_response = b''
        while True:
            try:
                chunk = self.worker_socket.recv(settings.RESPONSE_BUFFER_SIZE)
                if not chunk:
                    break
                encoded_response += chunk
            except socket.timeout:
                print("Finished receiving data")
                break
        code = re.search(b"([0-9]{3} .+?)\r\n", encoded_response)
        if code:
            code = (code.group()).rstrip(b"\n\r")
            if code == b"200 OK":
                return self.decoderesponse(encoded_response)
            elif code == b"404 Not Found":
                raise Exception("Page Not Found")
            elif code == b"301 Moved Permanently":
                try:
                    location = self.getheader(encoded_response, b"Location:")
                    encrypt = False
                    check = (b"https://" if encrypted else b"http://") + bytes(target, settings.DEFAULT_ENCODING) + bytes(resource, settings.DEFAULT_ENCODING)
                    if location != check:
                        if location.find(b"https") != -1:
                            encrypt = True
                        return self.request(target, resource, encrypt)
                    else:
                        raise Exception()  # The relocation link is identical to the original link followed.
                except Exception as ex:
                    print(ex)
                    raise Exception("Relocation URI Is Invalid")
            else:
                raise Exception("Unhandled Code: " + code)
        else:
            raise Exception("Corrupt HTTP Response")

    # Takes a http response and decodes and returns the body.
    def decoderesponse(self, data):
        encoding_type = self.getheader(data, b"Content-Encoding:")
        if encoding_type == b"gzip":
            data_end = data.find(b"\r\n\r\n")
            data = data[data_end + 4:]
            decoded_response = gzip.decompress(data)
            decoded_response = str(decoded_response, settings.DEFAULT_ENCODING)
            return decoded_response
        else:
            data_end = data.find(b"\r\n\r\n")
            data = data[data_end + 4:]
            data = str(data, settings.DEFAULT_ENCODING)
            return data

    # Finds all of the internal links to other recipes and pushes them onto the synchronized stack.
    def getlinks(self, data, server):
        html_links = re.findall("<a href=\".+?\"", data)
        for link in html_links:
            end_quote = data.find("\"", 10)
            link = link[9:end_quote]
            if link.find("recipe") != -1:
                print(link)
                #link = server + link
                #self.links.put(data=link, block=True) # Uncomment when finished with recipe scanning method.

    # Finds the value for a given header.
    def getheader(self, data, header):
        start_index = data.find(header)
        end_index = data.find(b"\r\n", start_index)
        try:
            return (data[start_index + len(header):end_index]).strip()
        except Exception as exception:
            raise Exception("Header Doesn't Exist")

    # Finds the recipe information if it exists and saves it.
    def scanrecipe(self, data):
        pass

    # Processes the link taken from the queue.
    def processlink(self):
        link = self.links.get(block=True, timeout=None)
        split_index = link.find("/")
        server = link[:split_index]
        resource = link[split_index:]
        page_source = self.request(server, resource, False)
        self.scanrecipe(page_source)
        self.getlinks(page_source, server)
        self.links.task_done()