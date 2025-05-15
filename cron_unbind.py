import os
import sys
import requests
import logging
import warnings
from datetime import datetime, timedelta
from urllib3.exceptions import InsecureRequestWarning


# ---------- generl loging  ----------
def init_logger():
    logger = logging.getLogger("rancher_cli")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logfile = os.getenv("RANCHER_CLI_LOG", "rancher_cli.log")
    fileh = logging.FileHandler(logfile)
    fileh.setFormatter(fmt)
    logger.addHandler(console)
    logger.addHandler(fileh)
    return logger


# ---------- configure init ----------
def init_config():
    rancher_url = os.getenv("RANCHER_URL", "").rstrip("/")
    access_key = os.getenv("ACCESS_KEY", "")
    secret_key = os.getenv(
        "SECRET_KEY", ""
    )
    if not access_key or not secret_key:
        print("please export envs ACCESS_KEY and SECRET_KEY")
        sys.exit(1)
    warnings.filterwarnings("ignore", category=InsecureRequestWarning, module="urllib3")
    return rancher_url, access_key, secret_key


def init_headers(key, secret):
    token = f"{key}:{secret}"
    return {"Authorization": f"Bearer {token}"}

# ---------------- check the anntionation and cal the expir time -----------------
def is_expired(binding, logger):
    ann = binding.get("annotations", {})

    if ann.get("rancher.io/tempbind") != "true":
        return False

    created_str = ann.get("rancher.io/tempbind-created")
    duration_str = ann.get("rancher.io/tempbind-duration")
    if not created_str or not duration_str:
        return False

    try:
        created_time = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%S")
        duration = int(duration_str)
        expire_time = created_time + timedelta(minutes=duration)
        current_time = datetime.now()
        print(current_time.strftime("%Y-%m-%d %H:%M:%S"), expire_time)
        return current_time > expire_time
    except Exception as e:
        logger.warning(f"[failed] {e}")
        return False


def delete_binding(url, headers, ep, binding_id, logger):
    resp = requests.delete(f"{url}/v3/{ep}/{binding_id}", headers=headers, verify=False)
    if resp.status_code in (200, 204):
        logger.info(f"[unbind] unbind successfully {binding_id}")
    else:
        logger.warning(
            f"[unbind] unbind failed {binding_id}, status: {resp.status_code}"
        )


def check_and_unbind_expired(url, headers, logger):
    # define API endpoints
    endpoints = [
        ("globalrolebindings", "globalRoleId"),
        ("clusterroletemplatebindings", "roleTemplateId"),
        ("projectroletemplatebindings", "roleTemplateId"),
    ]

    for ep, _ in endpoints:
        try:
            resp = requests.get(f"{url}/v3/{ep}", headers=headers, verify=False)
            bindings = resp.json().get("data", [])
            for b in bindings:
                if is_expired(b, logger):
                    logger.info(f"[unbind check] {ep} {b['id']} expired")
                    delete_binding(url, headers, ep, b["id"], logger)

        except Exception as e:
            logger.error(f"[unbind check] {ep} error: {e}")


def main():
    logger = init_logger()
    url, key, secret = init_config()
    headers = init_headers(key, secret)
    warnings.filterwarnings("ignore", category=InsecureRequestWarning, module="urllib3")
    check_and_unbind_expired(url, headers, logger)


if __name__ == "__main__":
    main()
