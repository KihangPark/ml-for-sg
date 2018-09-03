# Machine learning api for Shotgun

Main purpose of this package is providing machine learning based python API for shotgun.

# Main Features

Below list is a part of the main things that this package will do:

1. Gather shotgun information and generate cache data files in csv format.
2. Generate jupyter-notebook file which user can use for investigating 'irregular' or heavy cost consuming pattern based on statical method.
3. Predict cost value based on machine learning method.

# Basic workflow

Below template workflow can be useful for using this package.

1. Generate source data based on shotgun field information.
2. Generate analyze report based on #1.
3. Update configure setting based on analyze results based on #2.
4. Generate resource data based on updated configure setting #3.
5. Train machine learning model based on #4.
6. Get prediction based on trained model in #5.

Upper basic workflow is based on below three sub parts.

A. Generate source data based on shotgun information.
B. Analyze based on A and generate re-source data based on analyzed results.
C. Generate machine learning model based on re-source and get prediction.

# Detail workflow

## Source data generation

This process will gather shotgun field information
and generate csv cache for generating analyze report.

### Setup shotgun script

At first,script must be registered for gathering shotgun data from python api.

![Alt text](/docs/images/01.png)

Set script application key.

![Alt text](/docs/images/02.png)

### Setup configure

Proper configure setting must be done before gathering shotgun field information.

#### Create configure file from config_template.yaml

    # Generate configure file from config_template.yaml
    cp config/config_template.yaml config/config.yaml

#### Update configure setting based on shotgun information

Below is the actual sample setting.

    library_paths:
        shotgun: 'Z:\Dev\python-api' # This path is pointing shotgun api package directory.

    model:
    trainer:
    data_processor:
    analyze_report_export_directory: 'analyze_report' # Analyze report will be generated under <package root>/analyze_report
    resource_handler:
    source_generator:
        shotgun:
            connection:
                site: 'https://test.shotgunstudio.com' # Shotgun url.
                script_name: 'tool_test' # Script name which was generated.
                api_key: 'xxxxxxxxxxxxx' # Script application key which was generated.
            data:
                source_schema: 'Shot' # Target Granularity
                text:
                    feature_list: ['description', 'tags', 'notes', 'open_notes'] # Shotgun fields which will be used as list of string values.
                cost: 'duration' # Shotgun cost field name.
                skip_features: ['id', 'created_at', 'image', 'project', 'updated_at'] # Shotgun fields which will be skipped.
                source_includes: ['bunny_010_0010', 'bunny_010_0020', 'bunny_010_0030', 'bunny_010_0040', 'bunny_010_0050'] # Shot list which will be used.

### Generate data csv file

Below process can generate source data file based on shotgun field values.

#### Open analyze jupyter-notebook file

![Alt text](/docs/images/03.png)

#### Setup environment

    # Set root package root directory.
    import os
    import sys
    import pandas
    import seaborn as sns

    # Set for inline graph.
    import matplotlib.pyplot as plt
    %matplotlib inline

    # Setup environment values.
    os.environ['ML_FOR_SG_ROOT'] = 'Z:\Dev\Github\ml-for-sg'
    sys.path.append('Z:\Dev\Github\ml-for-sg')

#### Get shotgun information based on project id

This process will generate csv file automatically under <package root>/source_data.
(Directory path "source_data" could be changed based on configure setting.)

    from lib.source_generator.shotgun.source_generator import ShotgunSourceGenerator
    shotgun_source_generator = ShotgunSourceGenerator()
    shotgun_source_generator.generate_source_data(project_id=70)

## Investigation

This workflow can find out target data like below.

* Finding out cost consuming tasks. (For example, top %3 cost consuming task.)
* Finding out too long cut duration shots. (For example, over 300 frame long shots.)

These kind of filtered result will be good starting point for finding solution.
Actual process will be below.

1. Gather shotgun information and convert to pandas DataFrame.
2. Filter 'irregular' data pattern based on #1. (Not implemented yet.)
3. Check actual field values and find out issue point.

User can find below actual sample process in <root package>/ipynb/sample.ipynb.

#### Setup environment

Open jupyter file in <package root>/ipynb/sample.ipynb.

#### Generate analyze report

    # Analyze feature based on source data.
    from lib.resource.feature_analyzer import FeatureAnalyzer
    feature_analyzer = FeatureAnalyzer()
    feature_analyzer.analyze()
    
#### Open analyze jupyter-notebook file

![Alt text](/docs/images/04.png)

#### Find proper filter setup based on analyze report file

This workflow can find out target data like below.

* Finding out high correlation field with cost field. (For example, top 5 field list which have high correlation with cost.)

These kind of filtered result will be good starting point for finding solution.
Actual process will be below.

1. Gather shotgun information and convert to pandas DataFrame.
2. Filter high 'correlation' data pattern based on #1. (Not implemented yet.)
3. Check actual field values and find out issue point.

#### Update configure file

Based on investigation results, user can update configure setting.

    # For updating configure,
    # please update df_x_remove_columns, df_x_remove_columns2 and df_x_text_remove_columns
    # and execute below.
    from lib.resource.resource_handler import ResourceHandler
    resource_handler = ResourceHandler()
    data = {
        'skip_feature_for_df_x_full': df_x_remove_columns + df_x_remove_columns2,
        'skip_feature_for_df_x_text_full': df_x_text_remove_columns
    }
    resource_handler.save_source_convert_config(data)
    
#### Generate re-source data based on updated configure

    from lib.resource.resource_handler import ResourceHandler
    resource_handler = ResourceHandler()
    resource_handler.convert_source_to_resource()

## Get prediction

This workflow can get prediction like below.

* Finding out cost value based on shotgun field value. (For example, task cost prediction which contains specific tag - 'fire', 'water', etc.)

These kind of prediction is kind of imitation which is done by production.

* This fx task will take much cost, because this fx task have 'fire' effect.
* This shot will task much cost, because this shot have 3 different furry character.

Actual process will be below.

1. Select regression model or get recommendation model. (Just only Ordinary Least Squares method implemented. More model will be implemented later.)
2. Fit #2 data to #3 model.
3. Get prediction based on #1.

User can find below actual sample process in <root package>/ipynb/sample.ipynb.

#### Open sample jupyter-notebook file

![Alt text](/docs/images/04.png)

#### Load re-source data

    resource_handler = ResourceHandler()
    data = resource_handler.load_resource_data()

#### Train model based on re-source data

    from lib.trainer.trainer import Trainer
    trainer = Trainer()
    merged_feature = trainer.merge_features(data)
    
    from lib.model.linear_regression.lasso_model import LassoModel
    lasso_model = LassoModel()
    trained_lasso_model = trainer.train_model(lasso_model, merged_feature)
    trainer.save_trained_model('lasso', trained_lasso_model)
    
#### Load trained model

    trained_model = resource_handler.load_trained_model('lasso')
    
#### Prepare new data for getting prediction

    from collections import OrderedDict

    new_data = OrderedDict([ 
        ('assets__backdrop', 1),
        ('assets__cliff', 0),
        ('sg_sequence__bunny_010', 1)]
    )

    c = ['assets__backdrop', 'assets__cliff', 'sg_sequence__bunny_010']
    v = [1, 0, 1]

    for column in merged_feature.columns:
        if column not in c:
            c.append(column)
            v.append(0)

    # .values.reshape(1, -1) because it must be 2-dim, because we passed only one new observation
    new_data = pandas.DataFrame([v], columns=c, index=['xxx']) 
    # Use the model to make predictions
    print new_data

#### Get prediction

    trained_model[0].predict(new_data)

# Minimum Requirements

* Shotgun API v3+.
* Python v2.7.
* Pandas v0.22+.
* Sklearn v0.19.1+

# Documentation

Will be delivered later which can replace below temporary description.

## Data preparation for test

Current sample config is focusing 'cost' investigation.
So 'cost' input value will be needed for testing.
Below simple api can be used to push dummy cost data to sample shotgun site.
After getting 30 trial shotgun site, below process can be used for pushing dummy tag, description.

### Open dummy data generation jupyter-notebook

![Alt text](/docs/images/05.png)

#### Setup environment

    # Set root package root directory.
    import os
    import sys

    os.environ['ML_FOR_SG_ROOT'] = 'Z:\Dev\Github\ml-for-sg'
    sys.path.append('Z:\Dev\Github\ml-for-sg')

    # Create shotgun data manager.
    from lib.source_generator.shotgun.source_generator import ShotgunSourceGenerator
    shotgun_source_generator = ShotgunSourceGenerator()
    handler = shotgun_source_generator.handler

#### Register dummy data

    from lib.utils.dummy_data_generation import *
    for shot in ['bunny_010_0010', 'bunny_010_0020', 'bunny_010_0030', 'bunny_010_0040', 'bunny_010_0050']:
        task_sources = get_raw_task_source(handler, shot)
        register_sample_sg_data(handler, task_sources)
        register_heavy_feature_tag(handler, task_sources)

#### Check the dummy result

After this operation, shotgun site will have dummy tag / description values.

![Alt text](/docs/images/dummy_sg_data.png)

# Changelog

# Tests

