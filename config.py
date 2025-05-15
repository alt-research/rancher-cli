import os
import sys
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