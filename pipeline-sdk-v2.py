# -*- coding: utf-8 -*-
# ########################################
# Function:    演示阿里云API SDK使用方法, 类式写法, 通过一个slb信息查找到其后端的ECS IP信息
# Example Usage:
#   python3 pipeline_sdk_v2.py
# ########################################

import json
import logging
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest, DescribeInstanceAttributeRequest
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancersRequest, DescribeLoadBalancersRelatedEcsRequest, DescribeLoadBalancerAttributeRequest


logging.basicConfig(level=logging.DEBUG)


class ALIAPI:
    def __init__(self, ALI_ACCESS_KEY='', ALI_SECRET_KEY='', SLB_NAME='', SLB_REGION_ID=''):
        self._accessKey = ALI_ACCESS_KEY
        self._secretKey = ALI_SECRET_KEY
        self.slbName = SLB_NAME
        self.regionID = SLB_REGION_ID
        self.client = AcsClient(self._accessKey, self._secretKey, self.regionID)
        self.logger = logging.getLogger()

    def get_slb_backends(self, slb_id):
        """
        :param slb_id: str
        return: ecs instance-id list, ecs is slb instance's backend
        """
        slb_req = DescribeLoadBalancerAttributeRequest.DescribeLoadBalancerAttributeRequest()
        slb_req.add_query_param('LoadBalancerId', slb_id)

        # Print response, show remix slb related ecs:
        slb_res = self.client.do_action_with_exception(slb_req)
        slb = json.loads(slb_res.decode('utf-8'))
        # print(json.dumps(slb, indent=2))

        # list all ecs-id which is elb backend:
        slb_backends = slb['BackendServers']['BackendServer']
        slb_backend_ids = []
        for backend in slb_backends:
            slb_backend_ids.append(backend['ServerId'])
        return slb_backend_ids

    def get_slb_from_name(self, slb_name):
        """
        :param slb_name: str, specify slb instance name
        :return: specify slb instance id
        """
        slb_req = DescribeLoadBalancersRequest.DescribeLoadBalancersRequest()
        slb_res = self.client.do_action_with_exception(slb_req)
        slbs = json.loads(slb_res.decode('utf-8'))
        logging.debug('all slbs: {}'.format(json.dumps(slbs)))
        # print(json.dumps(slbs, indent=2))
        slb_list = slbs['LoadBalancers']['LoadBalancer']
        for lb in slb_list:
            if lb['LoadBalancerName'] == slb_name:
                logging.debug('process slb: {}'.format(lb['LoadBalancerName']))
                slb_id = lb['LoadBalancerId']
                return slb_id
        return None

    def ecs_id2ip(self, ecs_id):
        """
        :param ecs_id: str, ecs instance-id
        return: str, ecs instance internal ip
        """
        # DescribeInstanceAttributeRequest
        ecs_req = DescribeInstanceAttributeRequest.DescribeInstanceAttributeRequest()
        ecs_req.add_query_param('InstanceId', ecs_id)
        ecs_res = self.client.do_action_with_exception(ecs_req)
        ecs = json.loads(ecs_res.decode('utf-8'))
        priv_ip = ecs['VpcAttributes']['PrivateIpAddress']['IpAddress']
        pub_ip = ecs['PublicIpAddress']['IpAddress']
        return (priv_ip, pub_ip)

    def gen_ip_list(self):
        slb_id = self.get_slb_from_name(self.slbName)
        if not slb_id:
            self.logger.error('No SLB Instance Fount: {}'.format(self.slbName))
            exit(1)
        ecs_ids = self.get_slb_backends(slb_id)
        ecs_ips = []
        for ecs_id in ecs_ids:
            ip = self.ecs_id2ip(ecs_id)
            ecs_ips.append(ip)
        return ecs_ips


if __name__ == '__main__':
    access_key = "XXXX"
    secret_key = "XXXX"
    slb_name = 'remix.example.com_qd_slb'
    slb_region_id = "cn-qingdao"
    api = ALIAPI(ALI_ACCESS_KEY=access_key, ALI_SECRET_KEY=secret_key, SLB_NAME=slb_name, SLB_REGION_ID=slb_region_id)
    ips = api.gen_ip_list()
    logging.info(ips)
