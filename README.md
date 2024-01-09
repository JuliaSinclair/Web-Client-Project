# Web-Client-Project
Assignment for Computer Communications and Networks (Fall 2023) at University of Victoria

To run the code: 
    In UVic's Linux Environment in this directory, run code by executing python3 trafficanalysis.py <TCP Trace File>
    Any other input or failure to add a URL will result in an error.

Output: 
    1. Whether or not the web server supports http2
    2. Cookie name, the expire time (if any), and the domain name (in any) of cookies that web server will use
    3. Whether or not the requested web page is password-protected

Notes:
    - This directory contains files: SmartClient.py and Readme.txt
    - Must use Python 3.5 or above 
    - Program supports HTTP status codes 200, 404, 503, 505, 301 and 302
