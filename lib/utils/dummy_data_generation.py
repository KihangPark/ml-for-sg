import urllib2
import random


def get_raw_sources(handler):
    raw_sources = []
    for code in ['bunny_010_0010', 'bunny_010_0020', 'bunny_010_0030', 'bunny_010_0040', 'bunny_010_0050']:
        raw_sources.append(get_raw_shot_source(handler, code))
    return raw_sources


def get_raw_shot_source(handler, code, project_id=70, limit=100):
    # Generate filter for project.
    if project_id:
        filters = [
            [
                'project', 'is', {'type': 'Project', 'id': project_id}
            ], [
                'code', 'is', code
            ]
        ]
    else:
        return []

    # Get source data from shotgun.
    schema_field_list = handler.schema_field_read('Shot')
    sources = handler.find(
        'Shot',
        filters,
        schema_field_list.keys(),
        limit=limit
    )

    valid_sources = []
    for source in sources:
        # Filter out improper project source.
        if not source['project']:
            continue
        valid_sources.append(source)

    return valid_sources


def get_raw_task_source(handler, code, project_id=70, limit=100):
    # Generate filter for project.
    if project_id:
        filters = [
            [
                'project', 'is', {'type': 'Project', 'id': project_id}
            ], [
                'code', 'is', code
            ]
        ]
    else:
        return []

    # Get source data from shotgun.
    schema_field_list = handler.schema_field_read('Shot')
    sources = handler.find(
        'Shot',
        filters,
        schema_field_list.keys(),
        limit=limit
    )

    task_sources = []
    schema_field_list = handler.schema_field_read('Task')
    for task in sources[0]['tasks']:
        filters = [
            [
                'project', 'is', {'type': 'Project', 'id': project_id}
            ], [
                'id', 'is', task['id']
            ]
        ]
        sources = handler.find(
            'Task',
            filters,
            schema_field_list.keys(),
            limit=limit
        )
        task_sources.append(sources[0])

    return task_sources


def get_sample_word_list(site=None, sample_word_count=300):

    if not site:
        site = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"

    response = urllib2.urlopen(site)
    txt = response.read()
    word_list = txt.splitlines()[:sample_word_count]
    return word_list


def register_sample_sg_data(handler, source):

    word_list = get_sample_word_list()

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
            'duration': random.randint(500, 5000)

        }

        handler.create('TimeLog', data)
