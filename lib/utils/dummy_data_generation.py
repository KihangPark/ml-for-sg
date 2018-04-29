import urllib2
import random


def get_sample_word_list(generator_config):

    word_site = generator_config['shotgun']['sample_generation']['word_site']
    word_count = generator_config['shotgun']['sample_generation']['sample_word_count']

    response = urllib2.urlopen(word_site)
    txt = response.read()
    word_list = txt.splitlines()[:word_count]
    return word_list


def register_sample_sg_data(handler, source, generator_config):

    word_list = get_sample_word_list(generator_config)

    for single_source in source:

        temp_rand_word = []
        temp_rand_tag = []

        # prepare random word list for sg_description
        for _ in range(0, 3):
            temp_rand_word.append(random.choice(word_list))

        # prepare random tags
        for _ in range(0, 3):
            random_tag_name = random.choice(word_list)
            filters = [['name', 'is', random_tag_name]]
            result = handler.find_one('Tag', filters)
            if result:
                temp_rand_tag.append(result)
            else:
                tag_data = {
                    'name': random_tag_name
                }
                temp_rand_tag.append(handler.create('Tag', tag_data))

        data = {
            'sg_description': ' '.join(temp_rand_word),
            'tags': temp_rand_tag
        }

        handler.update('Task', single_source['id'], data)


def register_heavy_feature_tag(handler, source):

    heavy_feature_tag = handler.find_one('Tag', filters=[['name', 'is', 'heavy_feature']])
    if not heavy_feature_tag:
        tag_data = {
            'name': 'heavy_feature'
        }
        heavy_feature_tag = handler.create('Tag', tag_data)

    heavy_feature2_tag = handler.find_one('Tag', filters=[['name', 'is', 'heavy_feature2']])
    if not heavy_feature2_tag:
        tag_data = {
            'name': 'heavy_feature2'
        }
        heavy_feature2_tag = handler.create('Tag', tag_data)

    for single_source in source:

        tags = single_source['tags']
        tags.append(heavy_feature_tag)
        tags.append(heavy_feature2_tag)
        data = {

            'entity': single_source['entity'],
            'project': single_source['project'],
            'tags': tags
        }

        handler.update('Task', single_source['id'], data)

        data = {
            'entity': single_source,
            'project': single_source['project'],
            'duration': 4800

        }

        handler.create('TimeLog', data)
