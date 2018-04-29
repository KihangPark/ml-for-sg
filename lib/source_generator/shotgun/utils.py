import sys


def get_shotgun_handler(root_config):
    """Get shotgun handler instance.

    Returns:
        shotgun_api3.shotgun.Shotgun: shotgun instance.
    """
    shotgun_library_path = root_config['library_paths']['shotgun']
    sys.path.append(shotgun_library_path)

    try:
        from shotgun_api3.shotgun import Shotgun

        shotgun_connection_config = root_config['source_generator']['shotgun']['connection']
        shotgun_handler = Shotgun(
            shotgun_connection_config['site'],
            script_name=shotgun_connection_config['script_name'],
            api_key=shotgun_connection_config['api_key']
        )

        return shotgun_handler

    except:
        return None
