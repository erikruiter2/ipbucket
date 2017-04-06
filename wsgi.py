"""
Overview of Templates:
base.html: 
 - Global html structure containing <html> and <body> tag
index.html
 - block maincontent: initial static welcome page
base_elements.html
 - block head: HTML <head> tag, Loads stylesheets and js libraries
 - block head->scripts: Placeholder to add additional scripts / js library references
 - block navigation: Builds left side menu structure, including menuitems
 - macro datatable(id, columns): Creates an empty jquery table with specified columns
"""

import sys
import settings
import json
import ipaddr_func
from database import init_db, db_session, db_query_by_id, db_add_entry, db_query_all
from models import IPv4Network, IPDomain, DomainIPv4, IPv4Address
from sqlalchemy import create_engine, MetaData, update
from flask import Flask, request, render_template, Response, Blueprint, jsonify
app = Flask(__name__)
from ipaddr_func import ip2long, long2ip, is_valid_ipv4_address, is_valid_ipv6_address
import logging
from logging.handlers import RotatingFileHandler

init_db()

wsgi_app = Blueprint('wsgi_app', __name__)

handler = RotatingFileHandler('ipbucket.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
def response(result = "", notification = "", request_info = None):
  return jsonify( { 'result' : result , 'notification' : notification, 'request_info': dict(request.view_args) })




""" WEB SERVICE routing """

@wsgi_app.route('/')
def index():
  return render_template('index.html')

@wsgi_app.route('/ip_domain', methods=['GET'])
def ip_domain():
  return render_template('ip_domain_overview.html')

@wsgi_app.route('/ip_domain/add/', methods=['GET'])
def ip_domain_add():
  return render_template('ip_domain_add_form.html')

@wsgi_app.route('/ip_network/<int:domain_id>', methods=['GET'])
def ip_network_overview(domain_id):
  return render_template('ip_network_overview.html')

@wsgi_app.route('/ip_network/<int:ip_domain_id>/<int:network_id>', methods=['GET'])
def ip_network(ip_domain_id,network_id):
  return render_template('ip_network.html', data = db_query_IPv4Network(ip_domain_id=ip_domain_id, network_id=network_id))

@wsgi_app.route('/ip_network/add/', methods=['GET'])
def ip_network_add():
  return render_template('ip_network_add_form.html')



""" REST API routing """


""" GET requests """
@wsgi_app.route('/api/ip_domain/all', methods=['GET'])
def api_ip_domains_get():
  return response(result = db_query_all(IPDomain))

@wsgi_app.route('/api/ip_domain/overview', methods=['GET'])
def api_ip_domains_overview_get():
  return response(result = db_query_IPDomainOverview())

@wsgi_app.route('/api/ip_domain/<int:id>', methods=['GET'])
def api_ip_domain_get(id):
  return response(result = db_query_by_id(IPDomain, id))

@wsgi_app.route('/api/ip_network/<int:ip_domain_id>', methods=['GET'])
def api_ip_networks_get(ip_domain_id):
  return response(result = db_query_all_IPv4Network(ip_domain_id))

@wsgi_app.route('/api/ip_network/<int:ip_domain_id>/<int:network_id>', methods=['GET'])
def api_ip_network_get(ip_domain_id, network_id):
  return response(result = db_query_IPv4Network(ip_domain_id=ip_domain_id, network_id=network_id))

@wsgi_app.route('/api/ip_address/<int:ip_domain_id>/<int:ip>/<int:count>', methods=['GET'])
def api_ip_address_get(ip_domain_id, ip, count):
  print request.view_args
  return response(result = db_query_IPv4Address(ip_domain_id=ip_domain_id, ip=ip, count=count))


""" POST requests """
@wsgi_app.route('/api/ip_domain/', methods=['POST'])
def api_ip_domain_post():
  data = json.loads(request.data)
  result =  db_add_entry(IPDomain,name=data['name'], comment=data['comment'])
  if type(result) is str:
    return response('error',result)
  else:
    return response('success', 'IP Domain ' + data['name'] + ' succesfully created.')

@wsgi_app.route('/api/ip_network/', methods=['POST'])
def api_ip_network_post():
  data = json.loads(request.data)
  result = db_add_IPv4Network(ip_domain_id=data['ip_domain'], name=data['name'], address=data['address'], comment=data['comment'])
  if type(result) is str:
    return response('error',result)
  else:
    return response('success', 'Network ' + data['name'] + ' with address ' + data['address'] + ' succesfully created.')


@wsgi_app.route('/api/ip_address/', methods=['POST'])
def api_ip_address_post():
  data = json.loads(request.data)
  result = db_add_entry(IPv4Address,ip=data['ip'], ip_domain_id=data['ip_domain_id'], fqdn=data['fqdn'], description=data['description'], reserved=data['reserved'])
  if type(result) is str:
    return response('error',result)
  else:
    return response('success', 'IP Address entry ' + data['fqdn'] + ' succesfully created.')


""" PUT requests """
@wsgi_app.route('/api/ip_address/<int:ip_domain_id>/<int:ip>', methods=['PUT'])
def api_ip_address_put(ip_domain_id,ip):
  data = json.loads(request.data)
  result = db_change_IPv4Address(ip=ip, ip_domain_id=ip_domain_id, data=data)
  if type(result) is str:
    return response('error',result)
  else:
    return response('success', 'IP Address entry ' + long2ip(ip) + ' succesfully updated.')


""" Helper functions """


def db_add_IPv4Network(ip_domain_id, name, address, comment):
  result=0
  ip , mask = address.split("/")
  print ip, mask
  if (is_valid_ipv4_address(ip) == False):
    return str(ip + " is not a valid IPv4 address.")
  
  result = db_add_entry(IPv4Network,ip_domain_id=ip_domain_id, name=name, ip=ip2long(ip), mask=int(mask), comment=comment)
  
  if type(result) is int:
    result = db_add_entry(DomainIPv4,ip_domain_id=ip_domain_id, ip4_network_id=result)
  
  return result

def db_query_IPDomainOverview():
  ip_domains = db_query_all(IPDomain)
  for ip_domain in ip_domains:
    ipv4network_count =  db_session.query(DomainIPv4.id).filter(DomainIPv4.ip_domain_id==ip_domain['id']).count() 
    ip_domain['ipv4network_count'] = ipv4network_count
    ip_domain['ipv6network_count'] = 0
  return ip_domains

def db_query_all_IPv4Network(ip_domain_id):
  entries = list()
  entrylist = dict()
  result = IPv4Network.query.order_by(IPv4Network.ip.asc(), IPv4Network.mask.asc() )
  index = 0
  for entry in result:
    entrylist['index'] = index
    index += 1
    for value in vars(entry):
      if value != '_sa_instance_state':
        entrylist[value] = vars(entry)[value]
        entrylist['parent'] = 0

    entries.append(entrylist)
    entrylist = dict()
  entries = add_parents(entries)
  entries = add_utilisation(entries)
  for i in range (0, len(entries)):
    entries[i]['ip'] = long2ip(entries[i]['ip'])  + "/" + str(entries[i]['mask'])
  
  return entries

def add_parents(entries):
  for p in entries:
    for c in entries:
      if c['index'] is not p['index']:
        if (IPv4Network_Contains(p,c) and p['index'] < c['index']):
          if p['ip'] == c['ip']: 
            if c['mask'] > p['mask']: c['parent'] = p['id']
          else: c['parent'] = p['id']
  return entries

def add_utilisation(entries):
  for i in entries:
    count = pow(2, (32 - i['mask']))
    result = IPv4Address.query.filter(((IPv4Address.ip >= i['ip']) & (IPv4Address.ip <= i['ip']+count)) & IPv4Address.ip_domain_id == i['ip_domain_id']).all()
    
    app.logger.error(len(result))
    
    
    
    i['utilisation_string'] = str(len(result)) + " / " +  str(count)

    i['utilisation_pct'] = (float(len(result)) / float(count)) * 100
    app.logger.error(i)
  return entries
    
def IPv4Network_Contains(parent_entry, child_entry):
  start = parent_entry['ip']
  end = parent_entry['ip'] - 1 + pow(2,  (32 - parent_entry['mask']))
  if (child_entry['ip'] >= start and child_entry['ip'] <= end):
    return True
  else:
    return False

def db_query_IPv4Network(ip_domain_id , network_id):
  entrylist = dict()
  entry = IPv4Network.query.filter_by(ip_domain_id = ip_domain_id, id=network_id).first()
  for value in vars(entry):
    if value != '_sa_instance_state':
      entrylist[value] = vars(entry)[value]
  entrylist['ip_string'] = long2ip(entrylist['ip'])  + "/" + str(entrylist['mask'])
  return entrylist


def db_query_IPv4Address(ip_domain_id, ip, count):
  """ Queries a list of ip addresses in a specified ip_domain, starting with ip (int value), up to the specified mask"""
  entries = list()
  for i in range (0, count):
    entries.append({ "id": -1 ,"ip" : ip + i , "ip_string" : long2ip(ip + i) , "ip_domain_id": ip_domain_id, "fqdn":"", "description":"", "reserved": False })
  
  result = IPv4Address.query.filter(((IPv4Address.ip >= ip) & (IPv4Address.ip <= ip+count)) & IPv4Address.ip_domain_id == ip_domain_id).all()
  
  for i in range (0,len(entries)):
    for entry in result:
      if entries[i]['ip'] == entry.ip:
        entries[i]['id'] = entry.id
        entries[i]['fqdn'] = entry.fqdn
        entries[i]['description'] = entry.description
        entries[i]['reserved'] = entry.reserved         
  return entries

def db_change_IPv4Address(ip_domain_id, ip, data):
  print ip_domain_id, ip, data
  stmt = ""
  for (entry) in data:

    if entry == 'ip_domain_id':
      stmt = update(IPv4Address).where((IPv4Address.ip==ip) & (IPv4Address.ip_domain_id == ip_domain_id) ).values(ip_domain_id=data[entry])
    if entry == 'fqdn':
      stmt = update(IPv4Address).where((IPv4Address.ip==ip) & (IPv4Address.ip_domain_id == ip_domain_id) ).values(fqdn=data[entry])
    if entry == 'description':
      stmt = update(IPv4Address).where((IPv4Address.ip==ip) & (IPv4Address.ip_domain_id == ip_domain_id) ).values(description=data[entry])
    if entry == 'reserved':
      stmt = update(IPv4Address).where((IPv4Address.ip==ip) & (IPv4Address.ip_domain_id == ip_domain_id) ).values(reserved=data[entry])
    print stmt
    result = db_session.execute(stmt)
    print vars(result)
  return stmt


 







