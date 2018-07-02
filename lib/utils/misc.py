import os
import yaml


def load_config():

    ml_for_sg_root = os.environ['ML_FOR_SG_ROOT']
    config_file_path = os.path.abspath(
        os.path.join(ml_for_sg_root, 'config', 'config.yaml')
    )
    f = open(config_file_path, "r")
    config = yaml.load(f)

    return config


def load_source_convert_config():

    ml_for_sg_root = os.environ['ML_FOR_SG_ROOT']
    config_file_path = os.path.abspath(
        os.path.join(ml_for_sg_root, 'config', 'source_convert_config.yaml')
    )
    f = open(config_file_path, "r")
    config = yaml.load(f)

    return config

