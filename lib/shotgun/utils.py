from lib.utils.utils import load_config


def get_shotgun_handler():

    config = load_config()

    shotgun_library_path = config['library_paths']['shotgun']

    import sys
    sys.path.append(shotgun_library_path)

    from shotgun_api3.shotgun import Shotgun

    shotgun_handler = Shotgun(
        config['shotgun']['connection']['site'],
        script_name=config['shotgun']['connection']['script_name'],
        api_key=config['shotgun']['connection']['api_key']
    )

    return shotgun_handler