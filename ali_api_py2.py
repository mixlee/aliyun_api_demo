#!/usr/bin/python2
# -*- coding:utf-8 -*-
# ########################################
# Function:    演示阿里云裸API使用方法 增加多服务支持 PY2
# Example Usage:
#   python ali_api_py2.py Service=cdn Action=DescribeCdnDomainLogs DomainName=appcdn.example.com LogDay=2018-05-20 PageSize=1000
#   python ali_api_py2.py Service=slb Action=DescribeLoadBalancers RegionId=cn-qingdao
#   python ali_api_py2.py Service=ecs Action=DescribeInstances RegionId=cn-qingdao
# ########################################

import sys, os
import urllib
import base64
import hmac
from hashlib import sha1
import time
import uuid
from optparse import OptionParser
import ConfigParser
import traceback
import requests

access_key_id = ''
access_key_secret = ''
service_address = 'https://{}.aliyuncs.com'
services_api_version = {'slb': '2014-05-15', 'ecs': '2014-05-26', 'cdn': '2014-11-11'} # 更多服务支持自行添加
CONFIGFILE = os.getcwd() + '/aliyun.ini'
CONFIGSECTION = 'Credentials'

def percent_encode(str):
    res = urllib.quote(str.decode(sys.stdin.encoding).encode('utf8'), '')
    res = res.replace('+', '%20')
    res = res.replace('*', '%2A')
    res = res.replace('%7E', '~')
    return res

def compute_signature(parameters, access_key_secret):
    sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])

    canonicalizedQueryString = ''
    for (k, v) in sortedParameters:
        canonicalizedQueryString += '&' + percent_encode(k) + '=' + percent_encode(v)

    stringToSign = 'GET&%2F&' + percent_encode(canonicalizedQueryString[1:])

    print('debug: stringToSign - {}'.format(stringToSign))
    h = hmac.new(access_key_secret + "&", stringToSign, sha1)
    signature = base64.encodestring(h.digest()).strip()
    return signature

def compose_params(service, user_params):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    parameters = {
        'Format': 'JSON',
        'AccessKeyId': access_key_id,
        'SignatureVersion': '1.0',
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureNonce': str(uuid.uuid1()),
        'TimeStamp': timestamp,
    }

    for key in user_params.keys():
        parameters[key] = user_params[key]

    parameters['Version'] = services_api_version[service]
    signature = compute_signature(parameters, access_key_secret)
    parameters['Signature'] = signature
    print(parameters)
    return parameters

def make_request(service, ser_params, quiet=False):
    params = compose_params(service, user_params)
    service_url = service_address.format(service)
    print(("URL: {}/?{}".format(service_url, urllib.urlencode(params))))
    req = requests.get(service_url, params)
    print("Request Done: {}".format(req.json()))

def configure_accesskeypair(args, options):
    if options.accesskeyid is None or options.accesskeysecret is None:
        print("config miss parameters, use --id=[accesskeyid] --secret=[accesskeysecret]")
        sys.exit(1)
    config = ConfigParser.RawConfigParser()
    config.add_section(CONFIGSECTION)
    config.set(CONFIGSECTION, 'accesskeyid', options.accesskeyid)
    config.set(CONFIGSECTION, 'accesskeysecret', options.accesskeysecret)
    cfgfile = open(CONFIGFILE, 'w+')
    config.write(cfgfile)
    cfgfile.close()

def setup_credentials():
    config = ConfigParser.ConfigParser()
    try:
        config.read(CONFIGFILE)
        global access_key_id
        global access_key_secret
        access_key_id = config.get(CONFIGSECTION, 'accesskeyid')
        access_key_secret = config.get(CONFIGSECTION, 'accesskeysecret')
    except Exception, e:
        print(traceback.format_exc())
        print("can't get access key pair, use config --id=[accesskeyid] --secret=[accesskeysecret] to setup")
        sys.exit(1)


if __name__ == '__main__':
    parser = OptionParser("%s Action=action Param1=Value1 Param2=Value2\n" % sys.argv[0])
    parser.add_option("-i", "--id", dest="accesskeyid", help="specify access key id")
    parser.add_option("-s", "--secret", dest="accesskeysecret", help="specify access key secret")

    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(0)

    if args[0] == 'help':
        print('Please refer ali service api documents: https://help.aliyun.com/')
        sys.exit(0)
    if args[0] != 'config':
        setup_credentials()
    else: # it's a configure id/secret command
        configure_accesskeypair(args, options)
        sys.exit(0)

    user_params = {}
    if len(sys.argv) < 3:
        print('No enought args... exit')
        sys.exit(1)
    if not (sys.argv[1].startswith('Service=') and sys.argv[2].startswith('Action=')):
        print('Service/Action Params Error... exit')
        sys.exit(1)

    #
    print(sys.argv)
    _, service = sys.argv[1].split('=')
    if service not in services_api_version:
        print('No support service: {}'.format(service))
        sys.exit(1)
    #
    for arg in sys.argv[2:]:
        try:
            key, value = arg.split('=')
            user_params[key.strip()] = value
        except ValueError, e:
            print(e.read().strip())
            raise SystemExit(e)
    make_request(service, user_params)

