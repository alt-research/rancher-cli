#!/usr/bin/env python3
"""
Rancher RoleTemplate CLI tool
features:
 1. list all users
 2. list all clusters
 3. list one cluster MemberShip
 4. list all projects within cluster
 5. list all role templates
 6. view one roleTamples detail
 7. list all role bindings for user
 8. bind role to user
 9. unbind role from user
"""
import os
import sys
import json
import requests
import argparse
from datetime import datetime, timedelta

from urllib3.exceptions import InsecureRequestWarning
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rancher_cli.config import init_logger, init_config, init_headers



# ------------------- support function -------------------
def get_user_id(username, url, headers, logger):
    logger.info(f"query the userName: {username}")
    resp = requests.get(
        f"{url}/v3/users?username={username}", headers=headers, verify=False
    )
    resp.raise_for_status()
    for u in resp.json().get("data", []):
        if u.get("username") == username:
            uid = u.get("id")
            return uid
    logger.warning(f"Not found user: {username}")
    return None


def get_cluster_id(cluster_name, url, headers, logger):
    logger.info(f"query the clusterName: {cluster_name}")
    resp = requests.get(
        f"{url}/v3/clusters?name={cluster_name}", headers=headers, verify=False
    )
    resp.raise_for_status()
    clusters = resp.json()["data"]
    cluster_id = clusters[0]["id"]
    if not clusters:
        print(f"[ERROR] Cluster '{cluster_name}' not found.")
        sys.exit(1)

    print(f"Cluster '{cluster_name}' found with ID: {cluster_id}")
    return clusters[0]["id"]


def get_cluster_members(cluster_id, url, headers, logger):
    logger.info(f"query the clusterMembers: {cluster_id}")
    resp = requests.get(
        f"{url}/v3/clusterRoleTemplateBindings?clusterId={cluster_id}",
        headers=headers,
        verify=False,
    )
    resp.raise_for_status()
    return resp.json()["data"]

def list_cluster_members(cluster_name, url, headers, logger):
    cluster_id = get_cluster_id(cluster_name, url, headers, logger)
    if not cluster_id:
        print("(none)")
        return

    members = get_cluster_members(cluster_id, url, headers, logger)
    if not members:
        print("(none)")
        return

    for m in members:
        principal_id = m.get("userPrincipalId") or m.get("groupPrincipalId")
        name = get_username_by_user_id(principal_id, url, headers, logger)
        role_id = m.get("roleTemplateId")
        role_name = get_role_display_name(role_id, url, headers, logger) or role_id
        print(f"- {name:<25} => {role_name} [{role_id}]")


def get_all_users(url, headers, logger):
    logger.info("get all users")
    resp = requests.get(f"{url}/v3/users", headers=headers, verify=False)
    resp.raise_for_status()
    return [(u["id"], u.get("name", "")) for u in resp.json().get("data", [])]

def list_users(url, headers, logger):
    users = get_all_users(url, headers, logger)
    if not users:
        print("(none)")
        return

    for uid, name in users:
        print(f"{uid}\t{name}")


def get_clusters(url, headers, logger):
    logger.info("get all clusters")
    resp = requests.get(f"{url}/v3/clusters", headers=headers, verify=False)
    resp.raise_for_status()
    for c in resp.json().get("data", []):
        return [(c["id"], c.get("name", ""))]

def list_clusters(url, headers, logger):
    clusters = get_clusters(url, headers, logger)
    if not clusters:
        print("(none)")
        return

    for cid, name in clusters:
        print(f"{cid}\t{name}")


def get_username_by_user_id(user_id, url, headers, logger):
    logger.info(f"get username by user_id: {user_id}")
    resp = requests.get(f"{url}/v3/users/{user_id}", headers=headers, verify=False)


def get_projects(url, headers, logger, cluster_id):
    """
    get the projects in the cluster
    """
    logger.info(f"get cluster [{cluster_id}] projects as following:\n")
    resp = requests.get(
        f"{url}/v3/projects",
        headers=headers,
        params={"clusterId": cluster_id},
        verify=False,
    )
    resp.raise_for_status()
    return [(p["id"], p.get("name", "")) for p in resp.json().get("data", [])]

def list_projects(url, headers, logger, cluster_id):
    projects = get_projects(url, headers, logger, cluster_id)
    if not projects:
        print("(none)")
    else:
        for pid, name in projects:
            print(f"{pid}\t{name}")


# ------------------- RoleTemplate query -------------------
def fetch_all_templates(rancher_url, headers, logger):
    result = {}

    # Global
    globals_ = (
        requests.get(f"{rancher_url}/v3/globalroles", headers=headers, verify=False)
        .json()
        .get("data", [])
    )
    result["global"] = [
        (r["id"], r.get("displayName") or r.get("name")) for r in globals_
    ]

    # Cluster
    cluster_resp = requests.get(
        f"{rancher_url}/v3/roletemplates?context=cluster&limit=1000",
        headers=headers,
        verify=False,
    )
    cluster_resp.raise_for_status()
    clusters = cluster_resp.json().get("data", [])
    result["cluster"] = [
        (r["id"], r.get("displayName") or r.get("name")) for r in clusters
    ]
    if not clusters:
        logger.warning("No cluster templates returned; check context param or permissions.")

    # Project
    projects = (
        requests.get(
            f"{rancher_url}/v3/roletemplates?context=project&limit=1000",
            headers=headers,
            verify=False,
        )
        .json()
        .get("data", [])
    )
    result["project"] = [
        (r["id"], r.get("displayName") or r.get("name")) for r in projects
    ]

    return result

def print_templates(categorized_templates):
    emoji = {"global": "🌐", "cluster": "☁️", "project": "📦"}
    for level in ["global", "cluster", "project"]:
        templates = categorized_templates.get(level, [])
        print("\n" + "=" * 50)
        print(f"{emoji.get(level, '')}  {level.capitalize()} RoleTemplates")
        print("=" * 50)
        if not templates:
            print("  (none)")
        else:
            for tpl_id, name in templates:
                print(f"  - {tpl_id:<12}  {name}")



# ------------------- RoleTemplate display name query  -------------------
def get_role_display_name(role_id, url, headers, logger, builtin_roles_cache=None):
    if builtin_roles_cache and role_id in builtin_roles_cache:
        return builtin_roles_cache[role_id]
    if role_id.startswith("rt-"):
        endpoint = "roleTemplates"
    elif role_id.startswith("gr-"):
        endpoint = "globalroles"
    else:
        # logger.info(f'build-in role_id: {role_id}')
        return role_id
    resp = requests.get(f"{url}/v3/{endpoint}/{role_id}", headers=headers, verify=False)
    if resp.status_code != 200:
        logger.error(f"fail to get role name for{role_id}: HTTP {resp.status_code}")
        return None
    data = resp.json()
    return data.get("displayName") or data.get("name")


def get_username_by_user_id(principal_id, url, headers, logger=None):
    user_id = principal_id.strip("local://")
    resp = requests.get(f"{url}/v3/users/{user_id}", headers=headers, verify=False)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("username") or data.get("name") or user_id
    return user_id


# ------------------- list the given user rolebindings   -------------------
def list_bindings(user_id, url, headers, logger):
    logger.info(f"get the rolebindings of the user: {user_id}")
    bindings = []

    builtin_roles_cache = {}
    try:
        resp = requests.get(
            f"{url}/v3/roletemplates?builtin=true", headers=headers, verify=False
        )
        if resp.status_code == 200:
            for role in resp.json().get("data", []):
                role_id = role.get("id")
                role_name = role.get("displayName") or role.get("name")
                if role_id and role_name:
                    builtin_roles_cache[role_id] = role_name
            logger.info(f"load {len(builtin_roles_cache)} builtin roles")

        else:
            logger.error(f"load builtin roles failed: HTTP {resp.status_code}")
    except Exception as e:
        logger.error(f"load builtin roles failed: {str(e)}")

    endpoints = [
        ("globalrolebindings", "global", "globalRoleId"),
        ("clusterroletemplatebindings", "cluster", "roleTemplateId"),
        ("projectroletemplatebindings", "project", "roleTemplateId"),
    ]
    for ep, level, key in endpoints:
        resp = requests.get(
            f"{url}/v3/{ep}?userId={user_id}", headers=headers, verify=False
        )
        resp.raise_for_status()
        for b in resp.json().get("data", []):
            rid = b.get(key)

            if not rid:
                continue
            name = builtin_roles_cache.get(rid)
            if not name:
                name = get_role_display_name(rid, url, headers, logger) if rid else None

            bindings.append(
                {
                    "level": level,
                    "bindingId": b.get("id"),
                    "roleId": rid,
                    "roleName": name,
                    "target": b.get("clusterId") or b.get("projectId") or "",
                }
            )
    logger.info(f"total found {len(bindings)} bindings as following:\n")
    return bindings


# ------------------- check role exists   -------------------
def role_exists(role_id, level, url, headers, logger):
    if level == "global":
        ep = "globalroles"
        key = "id"
    else:
        ep = "roletemplates"
        key = "id"
    resp = requests.get(f"{url}/v3/{ep}", headers=headers, verify=False)
    resp.raise_for_status()
    roles = resp.json().get("data", [])
    if level == "global":
        return any(r.get(key) == role_id for r in roles)
    else:
        return any(r.get(key) == role_id and r.get("context") == level for r in roles)


# ------------------- check target exists   -------------------
def validate_target_exists(level, target, url, headers, logger):
    if level == "global":
        return True
    endpoint_map = {"cluster": "clusters", "project": "projects"}
    endpoint_key = endpoint_map[level]
    if not endpoint_key:
        logger.error(f"not support the level: {level}")
        return False
    
    target_url = f"{url}/v3/{endpoint_key}/{target}"
    try:
        resp = requests.get(target_url, headers=headers, verify=False)
        if resp.status_code == 200:
            return True
        elif resp.status_code == 404:
            logger.error(f"the target [{target}] not exist in the {level}")
    except requests.exceptions.RequestException as e:
        logger.error(f"request error: {str(e)} | URL: {target_url}")
    return False


# ------------------- bind and unbind   ----------------------
def bind_role(
    user_id, role_id, level, target, url, headers, logger, duration_minutes=None
):
    # check target if exists
    if level != "global" and not validate_target_exists(
        level, target, url, headers, logger
    ):
        return None

    # check role exists
    # 1. check if the role in the given level exists
    if not role_exists(role_id, level, url, headers, logger):
        logger.error(f"Not existing the [{role_id}] in {level} level")
        return None

    # 2. check the current bindings, and if the binding exists, skip
    current_bindings = list_bindings(user_id, url, headers, logger)
    for b in current_bindings:
        if b["roleId"] == role_id and b["level"] == level and b["target"] == target:
            logger.info(
                f"the rolebindings exists,skip: role={role_id}, level={level}, target={target}"
            )
            return b["bindingId"]

    # 3. bind the role
    logger.info(f"bind: user={user_id}, role={role_id}, level={level}, target={target}")
    payload = {"userId": user_id}
    annotations = {}

    if duration_minutes:
        current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        annotations = {
            "rancher.io/tempbind": "true",
            "rancher.io/tempbind-created": str(current_time),
            "rancher.io/tempbind-duration": str(duration_minutes),
        }

    if level == "global":
        payload["globalRoleId"] = role_id
        ep = "globalrolebindings"
    elif level == "cluster":
        payload["roleTemplateId"] = role_id
        payload["clusterId"] = target
        ep = "clusterroletemplatebindings"
    else:
        payload["roleTemplateId"] = role_id
        payload["projectId"] = target
        ep = "projectroletemplatebindings"

    if annotations:
        payload["annotations"] = annotations

    resp = requests.post(f"{url}/v3/{ep}", headers=headers, json=payload, verify=False)
    resp.raise_for_status()
    bid = resp.json().get("id")
    logger.info(f"bind successfully: bindingId={bid}")
    # list_bindings(user_id, url, headers, logger)
    return bid


def unbind_role(user_id, role_id, level, target, url, headers, logger):

    # check target if exists
    if level != "global" and not validate_target_exists(
        level, target, url, headers, logger
    ):
        return None

    # check role exists
    # 1. check if the role in the given level exists
    if not role_exists(role_id, level, url, headers, logger):
        logger.error(f"Not existing the [{role_id}] in {level} level")
        return None

    logger.info(
        f"try unbind: user={user_id}, role={role_id}, level={level}, target={target}"
    )
    bindings = list_bindings(user_id, url, headers, logger)
    matched = [
        b
        for b in bindings
        if b["roleId"] == role_id and b["level"] == level and b["target"] == target
    ]
    if not matched:
        logger.warning(
            f"No matching binding found: role={role_id}, level={level}, target={target}"
        )
        return

    for b in matched:
        binding_id = b["bindingId"]
        if level == "global":
            ep = f"globalrolebindings/{binding_id}"
        elif level == "cluster":
            ep = f"clusterroletemplatebindings/{binding_id}"
        else:
            ep = f"projectroletemplatebindings/{binding_id}"

        resp = requests.delete(f"{url}/v3/{ep}", headers=headers, verify=False)
        if resp.status_code in (200, 204):
            logger.info(f"unbind successfully: {binding_id}")
        else:
            logger.error(f"unbind failed: {binding_id} HTTP {resp.status_code}")


# --------------------- view RoleTemplate  ---------------------
def view_role_template(role_id, url, headers, logger):
    logger.info(f"read out context RoleTemplate: {role_id}")
    resp = requests.get(
        f"{url}/v3/roleTemplates/{role_id}", headers=headers, verify=False
    )
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


def main():
    logger = init_logger()
    url, key, secret = init_config()
    headers = init_headers(key, secret)

    parser = argparse.ArgumentParser(description="Rancher RoleTemplate CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="query the given user role-bindings")
    p_list.add_argument("username")

    sub.add_parser("list-clusters", help="list clusters")

    p_list_c_member = sub.add_parser(
        "list-cluster-members", help="list cluster-members"
    )
    p_list_c_member.add_argument("--cluster", "-c", required=True)

    sub.add_parser("list-roleTemplates", help="list roleTemplates")

    pcl = sub.add_parser("list-projects", help="list projects under the cluster")
    pcl.add_argument("--cluster", "-c", required=True)

    sub.add_parser("list-users", help="list all users")

    p_bind = sub.add_parser("bind", help="bind the role to the given user")
    p_bind.add_argument("username")
    p_bind.add_argument("roleId")
    p_bind.add_argument("level", choices=["global", "cluster", "project"])
    # if choices in ['cluster', 'project'], need target
    p_bind.add_argument("--target", default="")

    # p_temp = sub.add_parser(
    #     "tempbind", help="bind the role to the given user with a temporary duration"
    # )
    # p_temp.add_argument("username")
    # p_temp.add_argument("roleId")
    # p_temp.add_argument("level", choices=["global", "cluster", "project"])
    # p_temp.add_argument("--target", default="")
    # p_temp.add_argument("--duration", type=int, default=10)

    p_unbind = sub.add_parser("unbind", help="unbind the role from the given user")
    p_unbind.add_argument("username")
    p_unbind.add_argument("roleId")
    p_unbind.add_argument("level", choices=["global", "cluster", "project"])
      # if choices in ['cluster', 'project'], need target
    p_unbind.add_argument("--target", default="")

    p_view = sub.add_parser("view", help="query the RoleTemplate context from roleId")
    p_view.add_argument("roleId")

    args = parser.parse_args()

    try:
        # # check the args validity before request
        #if args.cmd in ["bind", "tempbind", "unbind"]:
        if args.cmd in ["bind", "unbind"]:
            if args.level in ["cluster", "project"] and not args.target:
                parser.error(
                    f"--target the param on level={args.level} is must。pleaase add  --target=<obj ID>"
                )
            elif args.level == "global" and args.target:
                parser.error(
                    f"--target the param on level={args.level} is not allowed。pleaase remove --target=<obj ID>"
                )

        if args.cmd == "list":
            uid = get_user_id(args.username, url, headers, logger)
            if not uid:
                print("(none)")
                sys.exit(1)
            items = list_bindings(uid, url, headers, logger)
            if not items:
                print("(none)")
            else:
                for b in items:
                    print(
                        f"{b['level']:<7} | {b['roleId']:<12} | {b['roleName'] or '' :<25} | target={b['target']}"
                    )

        elif args.cmd == "bind":
            uid = get_user_id(args.username, url, headers, logger)
            bind_role(uid, args.roleId, args.level, args.target, url, headers, logger)

        elif args.cmd == "unbind":
            uid = get_user_id(args.username, url, headers, logger)
            unbind_role(uid, args.roleId, args.level, args.target, url, headers, logger)

        # for tempbind，only set the annotation for the mapping
        # elif args.cmd == "tempbind":
        #     uid = get_user_id(args.username, url, headers, logger)
        #     binding_id=bind_role(
        #         uid,
        #         args.roleId,
        #         args.level,
        #         args.target,
        #         url,
        #         headers,
        #         logger,
        #         duration_minutes=args.duration,
        #     )
        #     if binding_id:
        #         print(f"Will automatically unbind after {args.duration} minutes")
            # time.sleep(args.duration * 60)
            # unbind_role(uid, args.roleId, args.level, args.target, url, headers, logger)

        elif args.cmd == "view":
            view_role_template(args.roleId, url, headers, logger)
        elif args.cmd == "list-roleTemplates":
            templates = fetch_all_templates(url, headers, logger)
            print_templates(templates)
        elif args.cmd == "list-clusters":
            list_clusters(url, headers, logger)
        elif args.cmd == "list-projects":
            list_projects(url, headers, logger, args.cluster)
        elif args.cmd == "list-users":
            list_users(url, headers, logger)
        elif args.cmd == "list-cluster-members":
            list_cluster_members(args.cluster, url, headers, logger)
    

    except Exception as e:
        logger.exception(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
