# aliyun_api_demo
学习阿里云 API调用方法:

1. cdn_py2.py/ecs_py2.py/slb_py2.py 三个脚本分别针对每个服务API调用API;
2. ali_api_py2.py/ali_api_py3.py 两个脚本是对1中服务API的组合写法;
3. pipeline-sdk-v1.py/pipeline-sdk-v2.py 使用阿里云API SDK完成获取一个ELB服务后端ECS IP;


## 注意:
 * 1/2 脚本使用前需将AK信息写入aliyun.ini文件, 或通过执行脚本config 命令写入;
 * 3脚本执行前需安装Aliyun SDK, 参考requirements.txt;
 ref: https://github.com/aliyun/aliyun-openapi-python-sdk
 * 更多的API调用Action及参数需要参考阿里云API文档;

用法示例:
# cdn
<pre><code>
# python cdn_py2.py Action=DescribeCdnDomainLogs DomainName=appcdn.example.com LogDay=2018-05-20 PageSize=1000
# python cdn_py2.py Action=DescribeCdnDomainLogs DomainName=appcdn.example.com StartTime='2018-04-01T00:00:00Z'  EndTime='2018-05-01T00:00:00Z' PageSize=1000
# python cdn_py2.py Action=DescribeCdnDomainLogs DomainName=appcdn.example.com StartTime='2018-04-01T00:00:00Z'  EndTime='2018-05-01T00:00:00Z' PageSize=500 PageNumber=2
</code></pre>

# slb
<pre><code>
# python slb_py2.py  Action=DescribeRegions
# python slb_py2.py  Action=DescribeLoadBalancers RegionId=cn-qingdao
# python slb_py2.py  Action=DescribeLoadBalancerAttribute RegionId=cn-qingdao LoadBalancerId=15af5f10b61-cn-qingdao-cm5-a01
</code></pre>

# ecs
<pre><code>
# python ecs_py2.py  Action=DescribeInstances RegionId=cn-qingdao
</code></pre>

# ali_api:
<pre><code>
# python ali_api_py2.py Service=slb Action=DescribeRegions
# python3 ali_api_py3.py Service=slb Action=DescribeRegions
# python ali_api_py2.py Service=ecs Action=DescribeInstances RegionId=cn-qingdao
# python ali_api_py2.py Service=cdn Action=DescribeCdnDomainLogs DomainName=appcdn.example.com LogDay=2018-05-20 PageSize=1000
</code></pre>

