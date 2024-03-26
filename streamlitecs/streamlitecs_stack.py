from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2, 
    aws_ecs as ecs,
    aws_cloudfront as cloudfront,
    aws_ecs_patterns as ecs_patterns
)
from constructs import Construct

class StreamlitecsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "MyVpc", max_azs=3)     # default is all AZs in region

        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)
        
        security_group = ec2.SecurityGroup(self, "MySecurityGroup",
            vpc=vpc,
            description="Allow CloudFront traffic to ALB",
            allow_all_outbound=True  # Allow all outbound traffic
        )

        security_group.add_ingress_rule(
            ec2.Peer.prefix_list('pl-3b927c52'),  # Replace 'pl-xxxxxx' with your prefix list ID
            ec2.Port.all_traffic(),
            "Allow CloudFront traffic"
        )

        app = ecs_patterns.ApplicationLoadBalancedFargateService(self, "MyFargateService",
            cluster=cluster,            # Required
            cpu=512,                    # Default is 256
            desired_count=2,            # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("public.ecr.aws/m2l6b1f0/streamlitecs:latest")), # replace with your own image repe
            memory_limit_mib=2048,      # Default is 512
            public_load_balancer=False)  
        
        app.load_balancer.add_security_group(security_group)

        distribution = cloudfront.CloudFrontWebDistribution(
            self, "MyCloudFrontDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    custom_origin_source=cloudfront.CustomOriginConfig(
                        domain_name=app.load_balancer.load_balancer_dns_name,
                        origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY
                    ),
                    behaviors=[
                        cloudfront.Behavior(
                            is_default_behavior=True,
                            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                            allowed_methods=cloudfront.CloudFrontAllowedMethods.ALL,
                            cached_methods=cloudfront.CloudFrontAllowedCachedMethods.GET_HEAD,
                            path_pattern="/_stcore/*",
                            forwarded_values=cloudfront.CfnDistribution.ForwardedValuesProperty(query_string=True,headers=['*'] ),
                        )
                    ],
                    
                    
                )
            ]
        )
        
        url = "https://"+distribution.distribution_domain_name
        
        CfnOutput(self, id="CFurl", value=url, export_name="CFdistribution")
        
     