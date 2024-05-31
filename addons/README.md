# Deployment scripts for addons.thunderbird.net

1. `source ~/thundernest-ansible/files/secrets.sh ; cd ~/thundernest-ansible/addons/playbooks`
2. `ansible-playbook --extra-vars "@../env/test-web.yml" deploy-instance.yml`

```mermaid
%% { init : { "theme" : "dark", "flowchart" : { "curve" : "linear" }}}%%

flowchart TB

    AURL[addons.thunderbird.net, services.addons.thunderbird.net]
    AELB([ELB amo-prod]):::elb
    AWEB(EC2 atn-webN):::ec2
    CEL(EC2 atn-celeryN):::ec2
    RAB(EC2 rabbitmq):::ec2

    RDS[(RDS amo-prod)]:::managed
    ES(OpenSearch amo-tb):::managed
    RED(redis amr1):::managed
    Z(memcached amo-ca):::managed

    VURL[versioncheck.addons.thunderbird.net]
    VELB([ELB amo-prod-versioncheck]):::elb
    VWEB[EC2 versioncheck]:::ec2

    AURL -->AELB
    AELB <--> AWEB
    AWEB <--> Z
    AWEB <--> RDS
    AWEB <--> ES

    CEL <--> RDS
    CEL --> ES
    CEL <--> RED

    AWEB --> RAB
    RAB <--> CEL

    VURL --> VELB <--> VWEB
    VWEB <--> RDS
    VWEB <--> Z

 classDef managed fill:green
 classDef elb fill:blue
 classDef ec2 fill:#ff8000
```

