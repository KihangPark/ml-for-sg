# Machine learning api for Shotgun

Main purpose of this package is providing machine learning based python API for shotgun.

# Main Features

Below are part of the things that this package will do:

1. Gather shotgun information and convert to pandas DataFrame.
2. Investigate 'irregular' or 'issue' cost consuming pattern based on statical method.
3. Predict cost value based on machine learning method.

# Basic workflow

Below workflow will be useful for using this package.

## Investigation

### Find out irregular data pattern.

This workflow can find out target data like below.

* Finding out cost consuming tasks. (For example, top %3 cost consuming task.)
* Finding out too long cut duration shots. (For example, over 300 frame long shots.)

These kind of filtered result will be good starting point for finding solution.
Actual process will be below.

1. Gather shotgun information and convert to pandas DataFrame.
2. Filter 'irregular' data pattern based on #1. (Not implemented yet.)
3. Check actual field values and find out issue point.

### Investigate correlation between fields.

This workflow can find out target data like below.

* Finding out high correlation field with cost field. (For example, top 5 field list which have high correlation with cost.)

These kind of filtered result will be good starting point for finding solution.
Actual process will be below.

1. Gather shotgun information and convert to pandas DataFrame.
2. Filter high 'correlation' data pattern based on #1. (Not implemented yet.)
3. Check actual field values and find out issue point.

## Prediction

### Predict future based on previous data.

This workflow can get prediction like below.

* Finding out cost value based on shotgun field value. (For example, task cost prediction which contains specific tag - 'fire', 'water', etc.)

These kind of prediction is kind of imitation which is done by production.

* This fx task will take much cost, because this fx task have 'fire' effect.
* This shot will task much cost, because this shot have 3 different furry character.

Actual process will be below.

1. Gather shotgun information and convert to pandas DataFrame.
2. Filter out 'irregular' data pattern from #1. (Not implemented yet.)
3. Select regression model or get recommendation model. (Just only Ordinary Least Squares method implemented. More model will be implemented later.)
4. Fit #2 data to #3 model.
5. Get prediction based on #1.

# Minimum Requirements

* Shotgun API v3+.
* Python v2.7.
* Pandas v0.22+.
* Sklearn v0.19.1+

# Documentation

Will be delivered later which can replace below temporary description.

## Data preparation

Current sample config is focusing 'cost' investigation.
So 'cost' input value will be needed for testing.
Below simple api can be used to push dummy cost data to sample shotgun site.
After getting 30 trial shotgun site, below process can be used for pushing dummy tag, description.

    import os
    os.environ['ML_FOR_SG_ROOT'] = <path to package> (For example, 'C:\Dev\ml-for-sg')
    from lib.shotgun.base import SGDataManager
    sg_data_manager = SGDataManager()
    target_list = sg_data_manager.get_target_list()
    from lib.shotgun.utils_for_dummy_data_generation import register_sample_sg_data, register_heavy_feature_tag
    register_sample_sg_data(target_list)
    register_heavy_feature_tag(target_list)

After this operation, shotgun site will have dummy tag / description values.

![Alt text](/docs/images/dummy_sg_data.png)

## Sample Prediction



Some useful direct links:

# Changelog

# Tests

