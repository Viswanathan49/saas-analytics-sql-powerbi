from sqlalchemy import create_engine
import yaml

def load_config(path="D:\Project\Data_Pipeline\project_root\config\config_dev.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def get_engine():
    cfg = load_config()
    db = cfg["db"]
    url = (
        f'{db["dialect"]}://'
        f'{db["user"]}:{db["password"]}@'
        f'{db["host"]}:{db["port"]}/'
        f'{db["database"]}'
    )
    engine = create_engine(url)
    return engine
