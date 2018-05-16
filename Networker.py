# Connects to webservers requesting page data.
# Written by Louis Kennedy

import gzip
import re
import ssl
import socket
import threading
import Settings as settings

def finddata(source):
    lastfind = 0
    current = 0
    while current != -1:
        lastfind = current
        current = source.find(b"\r\n", lastfind + 1)
    else:
        return lastfind + 2


def getheader(data, header):
    start_index = data.find(header)
    end_index = data.find(b"\r\n", start_index)
    try:
        return (data[start_index + len(header):end_index]).strip()
    except Exception as exception:
        raise Exception("Header Doesn't Exist")


def decoderesponse(data):
    encoding_type = getheader(data, b"Content-Encoding:")
    temp_data = data[0:int(len(data) / 10)]
    data_end = finddata(temp_data)
    data = data[data_end:]
    data = data[:len(data) - 7]
    if encoding_type == b"gzip":
        decoded_response = gzip.decompress(data)
        decoded_response = str(decoded_response, settings.DEFAULT_ENCODING)
        return decoded_response
    else:
        data = str(data, settings.DEFAULT_ENCODING)
        return data


def requestpage(address, retryCounter = 0):
    resource = address[address.find("/"):]
    csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 80
    if settings.ENCRYPTED:
        csocket = ssl.wrap_socket(csocket)
        port = 443
    csocket.settimeout(settings.SOCKET_TIMEOUT)
    try:
        csocket.connect((socket.gethostbyname(settings.BASE_SERVER), port))
    except socket.timeout:
        if retryCounter < settings.MAX_RETRIES:
            print("Network Error: Attempt to connect failed. Retrying...\n")
            requestpage(address, retryCounter + 1)
        else:
            print("Network Error: Max retries reached. Aborting server request.\n")
    request = "GET " + resource + " HTTP/1.1\r\n" + "User-Agent: Blacklight/" + \
              settings.VERSION + "\r\nHost: " + settings.BASE_SERVER + \
              "\r\nAccept-Language: en-us\r\nAccept-Encoding: gzip\r\nAccept-Charset: utf-8\r\n\r\n"
    csocket.send(request.encode(settings.DEFAULT_ENCODING))
    encoded_response = b''
    while True:
        try:
            chunk = csocket.recv(settings.RESPONSE_BUFFER_SIZE)
            if not chunk:
                break
            encoded_response += chunk
        except socket.timeout:
            break
    csocket.close()
    if encoded_response != b'':
        code = re.search(b"([0-9]{3} .+?)\r\n", encoded_response)
        if code:
            code = (code.group()).rstrip(b"\n\r")
            if code == b"200 OK":
                try:
                    return decoderesponse(encoded_response)
                except:
                    return None
            elif code == b"404 Not Found":
                raise Exception("Page Not Found")
            elif code == b"301 Moved Permanently" or code == b"302 Moved Temporarily":
                try:
                    location = getheader(encoded_response, b"Location:")
                    if location.find(settings.MAIN_BRANCH) != -1:
                        check = (b"https://" if settings.ENCRYPTED else b"http://") + bytes(settings.BASE_SERVER, settings.DEFAULT_ENCODING) + bytes(resource, settings.DEFAULT_ENCODING)
                        if location != check:
                            if location.find(b"https") != -1:
                                settings.ENCRYPTED = True
                            elif location.find(b"http") != -1:
                                settings.ENCRYPTED = False
                            return requestpage(settings.BASE_SERVER + resource)
                        else:
                            raise Exception("Cyclical Redirection Detected")  # The relocation link is identical to the original link followed.
                    else:
                        raise Exception("Invalid Link")
                except:
                    raise Exception("Relocation URI Is Invalid")
            else:
                raise Exception("Unhandled Code: " + str(code))
        else:
            raise Exception("Corrupt HTTP Response")
    else:
        raise Exception("Couldn't Find HTTP Status Code Header")
