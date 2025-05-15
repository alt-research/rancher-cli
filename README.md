# Rancher Roles Operation
## Roles Classification and Naming Rules
- Global-Admin (builtin)
- Global-Auditor
- `Cluster-Operator-<Cluster-Name>`
- `Project-AppDeveloper-<Project-Nmae>`
- Others

## Create Roles
1. Global-Auditor
```yaml
# Global-Auditor
apiVersion: management.cattle.io/v3
kind: GlobalRole
metadata:
  name: global-auditor
  annotations:
    lifecycle.cattle.io/create.mgmt-auth-gr-controller: 'true'
  labels:
    cattle.io/creator: norman
displayName: Global-Auditor
rules:
  - apiGroups:
      - '*'
    resources:
      - '*'
    verbs:
      - get
      - list
      - watch
```
2. Cluster-Operator-Pgbt
```yaml
# Cluster-Operator-Pgbt
administrative: false
apiVersion: management.cattle.io/v3
builtin: false
clusterCreatorDefault: false
context: cluster
displayName: Cluster-Operator-Pgbt
external: false
hidden: false
kind: RoleTemplate
locked: false
metadata:
  annotations:
    cleanup.cattle.io/rtUpgradeCluster: 'true'
    lifecycle.cattle.io/create.mgmt-auth-roletemplate-lifecycle: 'true'
  name: cluster-operator-pgbt
projectCreatorDefault: false
roleTemplateNames:
  - nodes-manage
  - persistentvolumeclaims-manage
  - storage-manage
  - backups-manage
rules:
  - apiGroups:
      - ''
    resources:
      - node
    verbs:
      - get
      - list
      - update
      - patch
      - watch
  - apiGroups:
      - ''
    resources:
      - persistentvolumes
    verbs:
      - create
      - delete
      - get
      - list
      - update
  - apiGroups:
      - storage.k8s.io
    resources:
      - storageclasses
    verbs:
      - watch
      - update
      - patch
      - list
      - get
      - delete
      - create
  - apiGroups:
      - events.k8s.io
    resources:
      - events
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - networkpolicies
    verbs:
      - get
      - list
      - create
      - delete
  - apiGroups:
      - ''
    resources:
      - resourcequotas
    verbs:
      - get
      - list
      - update
  - apiGroups:
      - ''
    resources:
      - limitranges
    verbs:
      - get
      - list
      - update
  - apiGroups:
      - certificates.k8s.io
    resources:
      - certificatesigningrequests
    verbs:
      - get
      - list
      - create
  - apiGroups:
      - ''
    resources:
      - namespaces
    verbs:
      - get
      - list
  - apiGroups:
      - apiextensions.k8s.io
    resources:
      - customresourcedefinitions
    verbs:
      - get
      - list
  - apiGroups:
      - storage.k8s.io
    resourceNames: []
    resources:
      - csinodes
    verbs:
      - get
      - list
      - watc
```
3. Project-AppDeveloper
```yaml
# Project-AppDeveloper
administrative: false
apiVersion: management.cattle.io/v3
builtin: false
clusterCreatorDefault: false
context: project
displayName: Project-AppDeveloper
external: false
hidden: false
kind: RoleTemplate
locked: false
metadata:
  annotations:
    cleanup.cattle.io/rtUpgradeCluster: 'true'
    lifecycle.cattle.io/create.mgmt-auth-roletemplate-lifecycle: 'true'
  name: project-appdeveloper
projectCreatorDefault: false
roleTemplateNames: []
rules:
  - apiGroups:
      - ''
    resources:
      - configmaps
    verbs:
      - create
      - delete
      - get
      - list
      - patch
      - update
      - watch
  - apiGroups:
      - ''
    resources:
      - persistentvolumeclaims
    verbs:
      - create
      - delete
      - get
      - list
      - patch
      - update
      - watch
  - apiGroups:
      - ''
    resources:
      - pods
    verbs:
      - watch
      - update
      - patch
      - list
      - get
      - delete
      - create
  - apiGroups:
      - ''
    resources:
      - secrets
    verbs:
      - list
      - create
      - delete
  - apiGroups:
      - apps
    resources:
      - deployments
    verbs:
      - create
      - delete
      - get
      - list
      - patch
      - update
      - watch
  - apiGroups:
      - apps
    resources:
      - replicasets
    verbs:
      - create
      - delete
      - list
      - get
      - patch
      - update
      - watch
  - apiGroups:
      - apps
    resources:
      - statefulsets
    verbs:
      - create
      - delete
      - get
      - list
      - patch
      - update
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses
    verbs:
      - create
      - delete
      - get
      - list
      - patch
      - update
      - watch
  - apiGroups:
      - io.k8s.api.discovery
    resources:
      - endpoints
    verbs:
      - create
      - delete
      - get
      - list
      - patch
      - update
      - watch
  - apiGroups:
      - project.cattle.io
    resources:
      - apps
    verbs:
      - create
      - delete
      - get
      - list
      - patch
      - update
      - watch
  - apiGroups:
      - permission.neuvector.com
    resources:
      - namespace
    verbs:
      - get
      - list
  - apiGroups:
      - ''
    resources:
      - namespaces
    verbs:
      - get
      - list
  - apiGroups:
      - ''
    resources:
      - services
    verbs:
      - create
      - delete
      - get
      - list
      - patch
      - update
  ```
4. Cluster-List-Namespaces
```yaml
# Cluster-List-Namespaces
apiVersion: management.cattle.io/v3
builtin: false
context: cluster
description: ''
displayName: Cluster-List-Namespaces
external: false
hidden: false
kind: RoleTemplate
metadata:
  annotations:
    cleanup.cattle.io/rtUpgradeCluster: 'true'
    lifecycle.cattle.io/create.mgmt-auth-roletemplate-lifecycle: 'true'
  name: cluster-list-namespaces
rules:
  - apiGroups:
      - ''
    resources:
      - namespaces
    verbs:
      - list
      - get
      - watch
```

## Command Usage
### Features
Rancher RoleTemplate CLI tool
features:
 - list all users
 - list all clusters
 - list one cluster MemberShip
 - list all projects within cluster
 - list all role templates
 - view one roleTamples detail
 - list all role bindings for user
 - bind role to user
 - unbind role from user

### help
```shell
python main.py -h
usage: main.py [-h] {list,list-clusters,list-cluster-members,list-roleTemplates,list-projects,list-users,bind,tempbind,unbind,view} ...

Rancher RoleTemplate CLI

positional arguments:
  {list,list-clusters,list-cluster-members,list-roleTemplates,list-projects,list-users,bind,tempbind,unbind,view}
    list                query the given user role-bindings
    list-clusters       list clusters
    list-cluster-members
                        list cluster-members
    list-roleTemplates  list roleTemplates
    list-projects       list projects under the cluster
    list-users          list all users
    bind                bind the role to the given user
    unbind              unbind the role from the given user
    view                query the RoleTemplate context from roleId

options:
  -h, --help            show this help message and exit
```
### features
1. list-users
```shell
python main.py list-users
2025-05-14 18:33:55 [INFO] get all users
u-jbwtc project-avs
u-lt47z demo
u-mwfs4 cluster-operator
u-vvj54 audit
user-mf2hs      Default Admin
```
2. list specify user detail
```shell
python main.py list demo 
2025-05-14 18:34:44 [INFO] query the userName: demo
2025-05-14 18:34:44 [INFO] get the rolebindings of the user: u-lt47z
2025-05-14 18:34:44 [INFO] load 40 builtin roles
2025-05-14 18:34:44 [INFO] total found 2 bindings as following:

global  | user         | user                      | target=
cluster | cluster-member | Cluster Member            | target=local

# the user not exists
ython main.py list demod
2025-05-14 18:35:15 [INFO] query the userName: demod
2025-05-14 18:35:15 [WARNING] Not found user: demod
(none)
```
3. list-clusters
```shell
python main.py list-clusters
2025-05-14 18:35:49 [INFO] get all clusters
local   local
```

4. list-roleTemplates
```shell
python main.py list-roleTemplates           

==================================================
🌐  Global Roles
==================================================
  - admin         Admin
  - authn-manage  Manage Authentication
  - clusters-create  Create Clusters
  - clustertemplaterevisions-create  Create RKE Template Revisions
  - clustertemplates-create  Create RKE Templates
  - features-manage  Manage Features
  - gr-d46c2      Global-audit
  - gr-q9b54      global-role
  - gr-ztgjq      serviceadmin
  - kontainerdrivers-manage  Manage Cluster Drivers
  - nodedrivers-manage  Manage Node Drivers
  - roles-manage  Manage Roles
  - settings-manage  Manage Settings
  - user          User
  - user-base     User Base
  - users-manage  Manage Users
  - view-rancher-metrics  View Rancher Metrics

==================================================
☁️  Cluster RoleTemplates
==================================================
  - backups-manage  Manage Cluster Backups
  - cluster-admin  Kubernetes cluster-admin
  - cluster-member  Cluster Member
  - cluster-owner  Cluster Owner
  - clustercatalogs-manage  Manage Cluster Catalogs
  - clustercatalogs-view  View Cluster Catalogs
  - clusterroletemplatebindings-manage  Manage Cluster Members
  - clusterroletemplatebindings-view  View Cluster Members
  - navlinks-manage  Manage Navlinks
  - nodes-manage  Manage Nodes
  - nodes-view    View Nodes
  - projects-create  Create Projects
  - projects-view  View All Projects
  - rt-5xs49      Cluster-Operator-pgbt
  - rt-vxzx6      cluster-list-namespace
  - storage-manage  Manage Storage

==================================================
📦  Project RoleTemplates
==================================================
  - admin         Kubernetes admin
  - configmaps-manage  Manage Config Maps
  - configmaps-view  View Config Maps
  - create-ns     Create Namespaces
  - edit          Kubernetes edit
  - ingress-manage  Manage Ingress
  - ingress-view  View Ingress
  - monitoring-ui-view  View Monitoring
  - navlinks-view  View Navlinks
  - persistentvolumeclaims-manage  Manage Volumes
  - persistentvolumeclaims-view  View Volumes
  - project-member  Project Member
  - project-monitoring-readonly  Project Monitoring View Role
  - project-owner  Project Owner
  - projectroletemplatebindings-manage  Manage Project Members
  - projectroletemplatebindings-view  View Project Members
  - read-only     Read-only
  - rt-6pjjr      project-custom-roles
  - rt-l2772      Project-AppDeveloper
  - secrets-manage  Manage Secrets
  - secrets-view  View Secrets
  - serviceaccounts-manage  Manage Service Accounts
  - serviceaccounts-view  View Service Accounts
  - services-manage  Manage Services
  - services-view  View Services
  - view          Kubernetes view
  - workloads-manage  Manage Workloads
  - workloads-view  View Workloads
```
5. view roleTemplate detail
```shell
python main.py view workloads-view
2025-05-14 18:38:12 [INFO] read out context RoleTemplate: workloads-view
{
  "administrative": false,
  "annotations": {
    "cleanup.cattle.io/rtUpgradeCluster": "true",
    "lifecycle.cattle.io/create.mgmt-auth-roletemplate-lifecycle": "true"
  },
  "baseType": "roleTemplate",
  
  ...
```
6. list-cluster-members
```shell
python main.py list-cluster-members -c local
2025-05-14 18:41:16 [INFO] query the clusterName: local
Cluster 'local' found with ID: local
2025-05-14 18:41:16 [INFO] query the clusterMembers: local
- demo                      => cluster-member [cluster-member]
- cluster-operator          => Cluster-Operator-pgbt [rt-5xs49]
- audit                     => Cluster-Operator-pgbt [rt-5xs49]
- u-jbwt                    => Cluster-Operator-pgbt [rt-5xs49]
```
7. bind user to roleTemplate
```shell
python main.py bind audit  rt-5xs49  cluster --target=local 
2025-05-14 18:44:25 [INFO] query the userName: audit
2025-05-14 18:44:25 [INFO] get the rolebindings of the user: u-vvj54
2025-05-14 18:44:25 [INFO] load 40 builtin roles
2025-05-14 18:44:25 [INFO] total found 4 bindings as following:

2025-05-14 18:44:25 [INFO] bind: user=u-vvj54, role=rt-5xs49, level=cluster, target=local
2025-05-14 18:44:25 [INFO] bind successfully: bindingId=local:crtb-jgfg7
```
8. unbind user from the cluster
```shell
python main.py unbind demo cluster-member cluster --target=local
2025-05-14 18:43:06 [INFO] query the userName: demo
2025-05-14 18:43:06 [INFO] try unbind: user=u-lt47z, role=cluster-member, level=cluster, target=local
2025-05-14 18:43:06 [INFO] get the rolebindings of the user: u-lt47z
2025-05-14 18:43:06 [INFO] load 40 builtin roles
2025-05-14 18:43:06 [INFO] total found 2 bindings as following:

2025-05-14 18:43:06 [INFO] unbind successfully: local:crtb-kh655
```
9. list-projects
```shell
python main.py list-projects -c local
2025-05-14 18:46:58 [INFO] get cluster [local] projects
local:p-2jlpz   project-admin
local:p-828ld   System
local:p-twxd5   project-avs
local:p-v5c5b   Default
```