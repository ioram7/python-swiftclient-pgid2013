#import BaseHTTPServer
import SimpleHTTPServer
import SocketServer
import os
import webbrowser
from swiftclient.contrib.federated import federated_exceptions
import ssl

## Sends the authentication request to the IdP along
# @param idpEndpoint The IdP address
# @param idpRequest The authentication request returned by Keystone
def getIdPResponse(idpEndpoint, idpRequest, realm=None):
    global responseIdp
    responseIdp = None
    config = open(os.path.join(os.path.dirname(__file__),"config/federated.cfg"), "Ur")
    line = config.readline().rstrip()
    key = ""
    cert = ""
    timeout = 300
    while line:
        if line.split('=')[0] == "KEY":
            key = line.split("=")[1].rstrip()

        if line.split("=")[0] == "CERT":
            cert = line.split("=")[1].rstrip()
        if line.split('=')[0] == "TIMEOUT":
            timeout = int(line.split("=")[1])
        line = config.readline().rstrip()
    config.close()
    if key == "default":
        key = os.path.join(os.path.dirname(__file__),"certs/server.key")
    if cert == "default":
        cert = os.path.join(os.path.dirname(__file__),"certs/server.crt")
    print "Initiating Authentication against: "+realm["name"]+"\n"
    webbrowser.open(idpEndpoint + idpRequest)

#    print (idpEndpoint + idpRequest)

#    class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

        def log_request(code=0, size=0):
            return
        def log_error(format="", msg=""):
            return
        def log_request(format="", msg=""):
            return

        def do_GET(self):
	    global responseIdp
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
#https://localhost:8080/
##state=lpjquz0KyrQ9
#&access_token=ya29.AHES6ZQRoGjNDhWIB6Z6i1BW8hUCBlIepRUG4Zvd_vAD3FTt
#&token_type=Bearer
#&expires_in=3600
#&id_token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjQ0M2M3NjdlMjY3NjgxMWZhOTMxZGQyYjI3NWMyNGZkYmYyYjQ1MWIifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXRfaGFzaCI6IlBlZXdNUUlwOUllaUxxUUx2ZTZ4cEEiLCJoZCI6ImNpbi51ZnBlLmJyIiwiZW1haWwiOiJpc3NAY2luLnVmcGUuYnIiLCJzdWIiOiIxMTQ2NTEwOTQzMjQ3MTYxMjU3MTUiLCJhdWQiOiI4MDA1NTAzMzIyMTktcmdpbXJuNTg2ajVjbnJkNXZ2azMxaW92Y29tMmdiYjYuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJlbWFpbF92ZXJpZmllZCI6InRydWUiLCJhenAiOiI4MDA1NTAzMzIyMTktcmdpbXJuNTg2ajVjbnJkNXZ2azMxaW92Y29tMmdiYjYuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJpYXQiOjEzNzM5Mjk5NTgsImV4cCI6MTM3MzkzMzg1OH0.PqvNJHu1weZGpnFY8TD93DNhQY2NQWbVkSqmOEQhYfYxegxieEOoNpVumSIun2jugfcU4-MkuihyGl_70eSET5u2PrZfHwGf7T5rKYJ9R1K8MEf-AcT5TL4W-TxCI94Fk0FZWsCGjgWBgcoXx1HaVRy-pE1w5ovI3otjPyk0lK8
#&authuser=0
#&hd=cin.ufpe.br
#&session_state=f02671873f90c5c86d372b7bfef6a63c2223c24d..5dad
#&prompt=none
	    print self.path
	    print self.rfile.read()

	    response = self.path.split('#')
	    if len(response) == 2 : 
		response = response[1].split('&')
	        for resp in response :
	            r = resp.split('=')
		    if r[0] == "access_token" :
			resp_token = r[1]
		    elif r[0] == "id_token" :
			resp_idtoken = r[1]
		    elif r[0] == "expires_in" :
			resp_exp = r[1]
		    elif r[0] == "hd" :
			resp_hd = r[1]
		    elif r[0] == "token_type" :
			resp_tt = r[1]
		    elif r[0] == "state" :
			resp_state = r[1]
      	        responseIdp = dict(access_token=resp_token, id_token=resp_idtoken, expires_in=resp_exp, hd=resp_hd, token_type=resp_tt, state=resp_state)
	        #print(responseIdp)

            if responseIdp is None:
                self.wfile.write("An error occured.")
                raise federated_exceptions.CommunicationsError()
            self.wfile.write("You have successfully logged in. "
                             "You can close this window now.")

#    httpd = BaseHTTPServer.HTTPServer(('localhost', 8080), RequestHandler)
    httpd = SocketServer.TCPServer(('localhost', 8080), RequestHandler)
    try:
        httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=key, certfile=cert, server_side=True)
        httpd.socket.settimeout(1)
    except BaseException as e:
        print e.value
    count = 0
    while responseIdp is None and count < timeout:
        try:
            httpd.handle_request()
            count = count + 1
	#    print(count, responseIdp)
        except Exception as e:
            print e.value
    if responseIdp is None:
        print ("There was no response from the Identity Provider or the request timed out")
        exit("An error occurred, please try again")
    print "Authentication Complete\n"
    return responseIdp
