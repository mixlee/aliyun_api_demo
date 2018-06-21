# -*- coding: utf-8 -*-
# ########################################
# Function:    演示阿里云API SDK使用方法, 脚本式写法, 通过一个slb信息查找到其后端的ECS IP信息
# Example Usage:
#   python3 pipeline_sdk_v1.py
# ########################################

import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest, DescribeInstanceAttributeRequest
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancersRequest, DescribeLoadBalancersRelatedEcsRequest, DescribeLoadBalancerAttributeRequest

# Global Info:
ALI_ACCESS_KEY = "XXXX"
ALI_SECRET_KEY = "XXXX"
SLB_NAME = "remix.example.com_qd_slb"
SLB_REGION = "cn-qingdao"

# Initialize AcsClient instance
client = AcsClient(
    ALI_ACCESS_KEY,
    ALI_SECRET_KEY,
    SLB_REGION
)

# Initialize a ecs request and set parameters
ecs_req = DescribeInstancesRequest.DescribeInstancesRequest()
ecs_req.set_PageSize(10)

# Print response, list all ecs instance:
ecs_res = client.do_action_with_exception(ecs_req)
instances = json.loads(ecs_res.decode('utf-8'))
# print(json.dumps(instances, indent=2))

# Initialize a slb request and set parameters
slb_req = DescribeLoadBalancersRequest.DescribeLoadBalancersRequest()
slb_req.set_PageSize(10)

# Print response, list all slb instances:
slb_res = client.do_action_with_exception(slb_req)
slbs = json.loads(slb_res.decode('utf-8'))
# print(json.dumps(slbs, indent=2))

# init request:
# Get slb instance named: "remix.example.com_qd_slb"
slb_list = slbs['LoadBalancers']['LoadBalancer']
for lb in slb_list:
    if lb['LoadBalancerName'] == SLB_NAME:
        remix_slb_id = lb['LoadBalancerId']
        print(remix_slb_id)
        break

#remix_req = DescribeLoadBalancersRelatedEcsRequest.DescribeLoadBalancersRelatedEcsRequest()
remix_req = DescribeLoadBalancerAttributeRequest.DescribeLoadBalancerAttributeRequest()
remix_req.add_query_param('LoadBalancerId', remix_slb_id)

# Print response, show remix slb related ecs:
remix_res = client.do_action_with_exception(remix_req)
remix_slb = json.loads(remix_res.decode('utf-8'))
print(json.dumps(remix_slb, indent=2))

# list all ecs-id as remix elb backend:
remix_slb_backends = remix_slb['BackendServers']['BackendServer']
remix_slb_backend_ids = []
for backend in remix_slb_backends:
    print(backend['ServerId'])
    remix_slb_backend_ids.append(backend['ServerId'])

# remix ecs-id to ecs-ip:
print("########### SLB Backend ECS Info ###########")
remix_ecs_ip = []
for id in remix_slb_backend_ids:
    # use fun DescribeInstanceAttributeRequest
    ecs_req = DescribeInstanceAttributeRequest.DescribeInstanceAttributeRequest()
    ecs_req.add_query_param('InstanceId', id)
    ecs_res = client.do_action_with_exception(ecs_req)
    ecs = json.loads(ecs_res.decode('utf-8'))
    print(json.dumps(ecs, indent=2))

