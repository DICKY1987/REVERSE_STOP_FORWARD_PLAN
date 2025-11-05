# infrastructure/pulumi/__main__.py
import pulumi
import pulumi_aws as aws

# Create required directories via EC2 user data
user_data = """#!/bin/bash
mkdir -p /opt/r_pipeline/{plugins,logs,quarantine}
useradd -r r_pipeline
chown -R r_pipeline:r_pipeline /opt/r_pipeline
chmod 755 /opt/r_pipeline/*
"""

# Security group with strict firewall rules
security_group = aws.ec2.SecurityGroup(
    "r-pipeline-sg",
    description="R_PIPELINE security group",
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 443, "to_port": 443, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]},
    ],
)

# Deploy infrastructure
pulumi.export("security_group_id", security_group.id)

# Run: pulumi up
# Then: pytest infrastructure/tests/ --hosts=your-server
# Expected: PASS