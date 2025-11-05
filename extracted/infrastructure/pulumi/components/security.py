# infrastructure/pulumi/components/security.py
import pulumi_aws as aws

def create_security_group(name: str, allowed_ports: list) -> aws.ec2.SecurityGroup:
    """Create a security group with specified allowed ports"""
    ingress_rules = [
        {"protocol": "tcp", "from_port": port, "to_port": port, "cidr_blocks": ["0.0.0.0/0"]}
        for port in allowed_ports
    ]
    
    return aws.ec2.SecurityGroup(
        name,
        description=f"{name} security group",
        ingress=ingress_rules,
        egress=[
            {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]},
        ],
    )