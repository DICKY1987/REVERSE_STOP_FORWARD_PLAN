# infrastructure/pulumi/__main__.py
"""
R_PIPELINE Infrastructure Definition
"""
import pulumi
import pulumi_aws as aws
import pulumi_command as command

# Configuration
config = pulumi.Config()
environment = config.require("environment")  # dev, staging, prod

# User data script for instance initialization
user_data_script = """#!/bin/bash
set -e

# Create r_pipeline user
useradd -r -s /bin/bash r_pipeline

# Create directory structure
mkdir -p /opt/r_pipeline/{plugins,logs,quarantine,data}
chown -R r_pipeline:r_pipeline /opt/r_pipeline
chmod 755 /opt/r_pipeline/*

# Install Python 3.10
yum install -y python310 python310-pip

# Install OpenTelemetry Collector
curl -L -o /tmp/otelcol.tar.gz https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.90.0/otelcol_0.90.0_linux_amd64.tar.gz
tar -xzf /tmp/otelcol.tar.gz -C /usr/local/bin/
chmod +x /usr/local/bin/otelcol

# Create systemd service for OpenTelemetry
cat > /etc/systemd/system/otel-collector.service <<'EOF'
[Unit]
Description=OpenTelemetry Collector
After=network.target

[Service]
Type=simple
User=r_pipeline
ExecStart=/usr/local/bin/otelcol --config=/opt/r_pipeline/otel-config.yaml
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable otel-collector
systemctl start otel-collector

echo "R_PIPELINE infrastructure initialized"
"""

# Security Group
security_group = aws.ec2.SecurityGroup(
    f"r-pipeline-sg-{environment}",
    description=f"R_PIPELINE security group for {environment}",
    ingress=[
        # SSH access (restricted to specific IPs in production)
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["10.0.0.0/8"] if environment == "prod" else ["0.0.0.0/0"]
        ),
        # HTTPS for API (if needed)
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=443,
            to_port=443,
            cidr_blocks=["0.0.0.0/0"]
        ),
    ],
    egress=[
        # Allow all outbound (for package installation, etc.)
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"]
        )
    ],
    tags={"Environment": environment, "ManagedBy": "Pulumi"}
)

# EC2 Instance
instance = aws.ec2.Instance(
    f"r-pipeline-instance-{environment}",
    instance_type="t3.medium" if environment == "prod" else "t3.small",
    ami="ami-0abcdef1234567890",  # Amazon Linux 2 AMI (update for your region)
    vpc_security_group_ids=[security_group.id],
    user_data=user_data_script,
    tags={"Name": f"R_PIPELINE-{environment}", "Environment": environment}
)

# Outputs
pulumi.export("instance_id", instance.id)
pulumi.export("instance_public_ip", instance.public_ip)
pulumi.export("security_group_id", security_group.id)