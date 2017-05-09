# Gatekeeper
Openstack Registration Site

## Workflow

```
[Dashboard] -> [Shibboleth] -> [SAFIRE] -> [IDP] -> [SAFIRE] -> [Shibboleth] -> [Gatekeeper] -> [Keystone] -> [Dashboard]
```

```
+----------------+          +-----------------+              +------------------+
|     User       |  YES     |   User Signed   |     YES      |    Redirect To   |
|     Exists     +--------->+   Terms         +------------->+    Openstack     |
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
             |NO                |Disagree                 |                |
             |                  |                         v                |
             v                  v                     +---+-----------+    |
+------------+------------------+--------+            | Display Join  |    |
|         Display Sorry Page             |            | Project       +----+
+----------------------------------------+            +---------------+


```

### Roles
* PrincipleInvestigator (Project)
* TermsSigned (Domain)
* AllocationApprover (Domain)

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

### Agreeing to Terms
When agreeing to terms, the system will email the user & a mailbox where we'll store all "signed" copies of terms.
We'll include some metadata from the shibboleth environment as well as a copy of the terms agreed to.
