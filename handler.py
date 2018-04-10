import json

import boto3

from models.game import Game
from models.variant import Variant

import pynamodb.exceptions


def get_all():
    games_table_response = [x.to_dict() for x in Game.scan()]
    return {'games': games_table_response}


def check_name_queries(search_name, queries):
    for query in queries:
        if not query in search_name:
            return False
    return True


def get_name(query_name):
    query_name = query_name.lower()
    print('Searching for: {}'.format(query_name))

    first_query, *other_queries = query_name.split(' ')

    results = [x.to_dict() for x in Game.scan(
        Game.search_name.contains(first_query))]

    filtered_results = list(results)
    if other_queries:
        for result in results:
            if not check_name_queries(result['search_name'], other_queries):
                filtered_results.remove(result)

    if not filtered_results:
        return {}

    return {
        'games': filtered_results
    }


def get_variant_sha1(variant_sha1):
    variant_sha1 = variant_sha1.lower()
    print('Searching for {}'.format(variant_sha1))

    try:
        variant = Variant.get(variant_sha1)
    except pynamodb.exceptions.GetError:
        return {}

    return {
        'variant_details': variant.to_detailed_dict()
    }


def get(event, context):
    query_string_params = event.get('queryStringParameters')
    if not query_string_params:
        return {
            "statusCode": 200,
            "body": json.dumps(get_all())
        }

    body = {}
    query_name = query_string_params.get('name')
    query_variant_sha1 = query_string_params.get('sha1')

    if query_name:
        body = {**body, **get_name(query_name)}

    if query_variant_sha1:
        body = {**body, **get_variant_sha1(query_variant_sha1)}

    if not body:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'error - not found'})
        }

    body['message'] = 'success'
    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }


def post(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps(event)
    }
