import os
import yaml


def load_config():

    ml_vfx_root = os.environ['ML_VFX_ROOT']
    config_file_path = os.path.abspath(os.path.join(ml_vfx_root, 'config', 'config.yaml'))
    f = open(config_file_path, "r")
    config = yaml.load(f)

    return config