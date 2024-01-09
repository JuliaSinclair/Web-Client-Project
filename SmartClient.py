"""
University of Victoria
CSC 361 Fall 2023
Julia Sinclair
V00890683
"""

import sys
import socket
import ssl
import re

def send_request(host, port, path):
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Check host name exists
        try:
            IP_address = socket.gethostbyname(host)
        except socket.gaierror:
            print("Error: Invalid URL")
            sys.exit(1)

        # Connect to the host
        context = ssl.create_default_context()
        client_socket = context.wrap_socket(client_socket, server_hostname=host)
        client_socket.connect((host, port))

        # Prepare the HTTP request
        http_request = f"GET /{path} HTTP/1.1\r\nHost: {host}\r\n\r\n"

        # Send the HTTP request
        client_socket.sendall(http_request.encode())

        # Receive HTTP response     
        response = client_socket.recv(1024)

        return response.decode("utf-8")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 

    finally:
        # Close the client socket
        client_socket.close()

def request_redirects(host, port, path):
    # Use a set to keep track of visited hosts to prevent infinite loops
    visited = set()

    while True:
        # Send an HTTP request to the current URL
        redirect_response = send_request(host, port, path)

        # Check if it's a redirect (HTTP status code 3xx)
        if re.match("^(HTTP/1.[0|1])\s(3)", redirect_response):
            lines = redirect_response.split("\r\n")
            for line in lines:
                if line.lower().startswith("location:"):
                    new_location = line.split(":", 1)[1].strip()
                    print(f"Redirecting to: {new_location}")
                    # Check for redirection loops to avoid infinite recursion
                    if new_location in visited:
                        return 0
                    visited.add(new_location)
                    if new_location.startswith('http://'):
                        port = 80
                    if "://" in new_location:
                        new_location = new_location.split("://")[1]
                    new_location_split = new_location.split("/")
                    host = new_location_split[0]
                    path = "/" + "/".join(new_location_split[1:])
                    break
        else:
            # If it's not a redirect
            return redirect_response

def main() -> None:
    # Check if a URI argument is provided
    if len(sys.argv) != 2:
        print("Error: Please run program as followed python3 SmartClient.py <URI>")
        sys.exit(1)
    
    # Set socket timeout to 10 seconds
    socket.setdefaulttimeout(10)

    # Parse inputted URL
    URL = sys.argv[1]
    if "://" in URL:
        URL = URL.split("://")[1]
    url_split = URL.split("/")
    host = url_split[0]
    path = "/" + "/".join(url_split[1:])

    # Rountine Prints outlined in assignment
    print("---Request begin---")
    print(f"GET {host}{path} HTTP/1.1")
    print("Host:", host)
    print("Connection: Keep-Alive")
    print("\n", end = '')
    print("---Request end---")
    print("HTTP request sent, awaiting response...")
    print("\n", end = '')

    #Send and recieve HTTP request
    response = request_redirects(host, 443, path)
    if response == 0:
        print("Error: Redirection loop detected")
        sys.exit(1) 

    #Decode the response and split headers and body
    response_lines = response.split("\r\n")
    headers, _, body = response.partition("\r\n\r\n")

    # Print HTTP response
    print("\n--- Response Header ---")
    print(headers)
    print("\n--- Response Body ---")
    #print(body)

    # Print website inputted
    print("\nwebsite:", sys.argv[1])

    # Check if h2 is supported
    # Create SSL Wrapped Socket from Tutorial 2
    h2client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    h2context = ssl.create_default_context()
    h2context.set_alpn_protocols(['http/1.1', 'h2'])
    h2conn = h2context.wrap_socket(h2client_socket, server_hostname=host)
    h2conn.connect((host, 443))
    if h2conn.selected_alpn_protocol() == "h2":
        print("1. Supports http2: yes")
    else: 
        print("1. Supports http2: no")
    h2conn.close()

    # Finding and storing cookies
    #Initialize dictionary for cookies
    cookies_info = {}
    # Parse HTTP response for cookies
    for line in response_lines:
        if line.startswith("Set-Cookie:"):
            cookie_line = line[len("Set-Cookie:"):].strip()
            cookie_split = cookie_line.split(";")
            cookie_name = cookie_split[0].split("=")[0].strip()
            cookie_attributes = {}
            # Store cookies information in dictionary 
            for data in cookie_split:
                if data.strip().startswith("expires="):
                    expire_date = data.strip().split("=")[1].strip()
                    cookie_attributes['expire'] = expire_date
                if data.strip().startswith("domain="):
                    domain_name = data.strip().split("=")[1].strip()
                    cookie_attributes['domain'] = domain_name
            cookies_info[cookie_name] = cookie_attributes

    # Listing cookies
    print("2. List of Cookies:")
    for cookie, attributes in cookies_info.items():
        print(f"cookie name: {cookie}", end = '')
        if attributes.get('expire') is not None or attributes.get('domain') is not None:
            print(",", end = '')
        if attributes.get('expire') is not None:
            print(f" expires time: {attributes.get('expire')};", end = '')
        if attributes.get('domain') is not None:
            print(f" domain name: {attributes.get('domain')}", end = '')
        print("\n", end = '')

    # Check if password protected 
    if "HTTP/1.1 401 Unauthorized" in headers:
        print("3. Password Protected: yes")
    else: 
        print("3. Password Protected: no")

if __name__ == "__main__":
    main()









