# Gatekeeper
Openstack Registration Site

## Workflow

```
[Dashboard] -> [Shibboleth] -> [SAFIRE] -> [IDP] -> [SAFIRE] -> [Shibboleth] -> [Gatekeeper] -> [Keystone] -> [Dashboard]
```

```
+----------------+          +-----------------+              +------------------+
|     User       |  YES     |   User Signed   |     YES      |Redirect To       |
|     Exists     +--------->+   Terms         +------------->+Openstack         |
+------------+---+          +----+------------+              +-------------+----+
             |                   |                                         ^
             |NO                 |                                         |
             |                   |                                         |
             v                   v                                         |
+------------+---+          +----+-------+            +---------------+    |
| User Account   |   YES    |   Present  |  Agree     | Display Create|    |
| Create Allowed +--------->+   Terms    +----------->+ Temp Project  |    |
+------------+---+          +---+--------+            +---+-----------+    |
             |                  |                         |                |
             |                  |                         |                |
             |NO                |Disaggree                |                |
             |                  |                         v                |
             v                  v                     +---+-----------+    |
+------------+------------------+--------+            | Display Join  |    |
|         Display Sorry Page             |            | Project       +----+
+----------------------------------------+            +---------------+


```

### Roles
* PrincilpleInvestigator (Project)
* TermsSigned (Domain)

### Project Metadata
Project metadata will be stored as JSON in the project description field, so besides the project name which is already stored in keystone the following fields will be added:
* ResearchField
* PrimaryInstitution
* Description
* CreatationTime
* ExpirationTime (-1 for a permanent project)

### Project Create Steps
* Create Project & Metadata
* Set Quotas
* Create Private Network
* Create Subnet
* Create Router
* Attach Router to Net & Subnet
