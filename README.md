# ipbucket
ipbucket is an IP address management (IPAM) tool, written in Python using the Flask framework.

Currently in an alpha development stage.

It can be started using: python ipbucket.wsgi

The default settings will render the application at: http://localhost:8080


###Working features at the moment:

Web interface:
 - Add / View IP Domains 
 - Add / View IPv4 networks
 -View / update IPv4 address records

REST interface:
 - IP Domain GET, POST
 - IPv4 network GET, POST
 - IPv4 address GET, PUT, POST
