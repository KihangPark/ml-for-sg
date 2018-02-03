import urllib2
import random

from lib.utils.utils import load_config
from lib.shotgun.utils import get_shotgun_handler


def get_sample_word_list():

    config = load_config()
    word_site = config['shotgun']['sample_generation']['word_site']
    word_count = config['shotgun']['sample_generation']['sample_word_count']

    response = urllib2.urlopen(word_site)
    txt = response.read()
    word_list = txt.splitlines()[:word_count]
    return word_list


def register_sample_sg_data(task_list):

    shotgun_handler = get_shotgun_handler()

    word_list = get_sample_word_list()

    for task in task_list:

        temp_rand_word = []
        temp_rand_tag = []

        # prepare random word list for sg_description
        for _ in range(0, 3):
            temp_rand_word.append(random.choice(word_list))

        # prepare random tags
        for _ in range(0, 3):
            random_tag_name = random.choice(word_list)
            filters = [['name', 'is', random_tag_name]]
            result = shotgun_handler.find_one('Tag', filters)
            if result:
                temp_rand_tag.append(result)
            else:
                tag_data = {
                    'name': random_tag_name
                }
                temp_rand_tag.append(shotgun_handler.create('Tag', tag_data))

        data = {
            'sg_description': ' '.join(temp_rand_word),
            'tags': temp_rand_tag
        }

        shotgun_handler.update('Task', task['id'], data)


def register_heavy_feature_tag(task_list):

    shotgun_handler = get_shotgun_handler()

    heavy_feature_tag = shotgun_handler.find_one('Tag', filters=[['name', 'is', 'heavy_feature']])
    if not heavy_feature_tag:
        tag_data = {
            'name': 'heavy_feature'
        }
        heavy_feature_tag = shotgun_handler.create('Tag', tag_data)

    heavy_feature2_tag = shotgun_handler.find_one('Tag', filters=[['name', 'is', 'heavy_feature2']])
    if not heavy_feature2_tag:
        tag_data = {
            'name': 'heavy_feature2'
        }
        heavy_feature2_tag = shotgun_handler.create('Tag', tag_data)

    for task in task_list[:100]:

        tags = task['tags']
        tags.append(heavy_feature_tag)
        tags.append(heavy_feature2_tag)
        data = {

            'entity': task['entity'],
            'project': task['project'],
            'tags': tags
        }

        shotgun_handler.update('Task', task['id'], data)

        data = {
            'entity': task,
            'project': task['project'],
            'duration': 4800

        }

        shotgun_handler.create('TimeLog', data)
