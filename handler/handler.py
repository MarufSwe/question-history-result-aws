import boto3
import uuid
import json
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime

uuid = str(uuid.uuid4())

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('practiceApiTable')
sub = '58781ddd-985a-485f-8c31-c8da77fd4278'


def lambda_handler(event, context):
    print('EVENT---: ', event)
    try:
        # get stage list
        stage = dynamodb_get_item('stage', event['arguments']['input']['stageSortKey'])
        empty_record_check(stage)
        resultStageKey = 'stage_' + str(stage['Item']['title'])
        # event['identity']['sub'] as sub

        englishQusetionSetting = dynamodb_get_item('englishqusetionsetting', 'englishqusetionsetting')

        userEnglishQuestionHistory = dynamodb_get_item('englishquestionhistory', 'englishquestionhistory#user#' + sub)

        if userEnglishQuestionHistory.get('Item'):
            print('Update Item====')
            if userEnglishQuestionHistory['Item']['results'].get(resultStageKey):
                print('Update by Stage Key====')

                table.update_item(
                    Key={
                        'PK': userEnglishQuestionHistory['Item']['PK'],
                        'SK': userEnglishQuestionHistory['Item']['SK']
                    },
                    UpdateExpression='SET results.' + resultStageKey + '.lastDate = :val1, results.' + resultStageKey + '.numberOfCompletion = :val2',
                    ExpressionAttributeValues={
                        # ':val1': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                        ':val1': datetime.today().isoformat(),
                        ':val2': userEnglishQuestionHistory['Item']['results'][resultStageKey]['numberOfCompletion'] + 1
                    }
                ),

            else:
                print('Add by Stage Key====')

                updateItems = {
                    ':val1': {
                        resultStageKey: {
                            'lastDate': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                            'numberOfCompletion': 1
                        }
                    }
                }

                updateItems[':val1'].update(userEnglishQuestionHistory['Item']['results'])
                table.update_item(
                    Key={
                        'PK': userEnglishQuestionHistory['Item']['PK'],
                        'SK': userEnglishQuestionHistory['Item']['SK']
                    },
                    UpdateExpression='SET results = :val1',
                    ExpressionAttributeValues = updateItems
                )

        else:
            print('Create Item====')
            table.put_item(
                Item={
                    'PK': 'englishquestionhistory',
                    'SK': 'englishquestionhistory#user#' + sub,
                    'results': {
                        resultStageKey: {
                            'lastDate': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                            'numberOfCompletion': 1
                        }
                    },
                    'type': 'userenglishquestionhistory',
                }
            )

        # userCoinUpdate = table.update_item(
        #     Key={
        #         'PK': 'user#' + sub,
        #         'SK': 'user#' + sub + '#coin',
        #     },
        #     UpdateExpression='SET totalCoin = totalCoin + :val1',
        #     ExpressionAttributeValues={
        #         ':val1': userEnglishQuestionHistory['Item']['results'].get(resultStageKey)
        #         if englishQusetionSetting['Item']['firstTimeAddCoin'] else englishQusetionSetting['Item']['firstTimeAddCoin'],
        #     },
        #     ReturnValues="UPDATED_NEW"
        #
        # ),
        # print('userCoinUpdate====: ', userCoinUpdate)

        return {'message': 'query execute successfully!!!'}
    except Exception as e:
        raise e


# stage SK check
def empty_record_check(arg1):
    if arg1.get('Item'):
        print('SK')
        return True
    else:
        raise Exception('ITEM False')


def dynamodb_get_item(PK, SK):
    return table.get_item(
        Key={
            'PK': PK,
            'SK': SK
        }
    )

    # for item in items:
    #     # check stage SK is exist or not in stage list
    #     if stage_SK in item['SK']:
    #         print("Stage SK is exist!!")
    #
    #         # get englishquestionhistory data
    #         engQue = table.scan(
    #             FilterExpression=Attr('PK').eq('englishquestionhistory') & Attr('SK').eq(
    #                 'englishquestionhistory#user#ab622594-413d-4491-8b65-891f07fe8cf2')
    #         )
    #         engQueResults = engQue['Items']
    #         # print('engQueResults=======: ', engQueResults)
    #         # for item in engQueResults:
    #         #     result = item['results']['stage_3']
    #         #     # myResult += (result)
    #         #     print('Result=========: ', result)
    #
    #         # check englishquestionhistory results is none or not
    #         if engQueResults:
    #             print('englishquestionhistory data exist!!!')
    #
    #             # get englishquestionhistory SK
    #             response = table.scan(
    #                 FilterExpression=Attr('PK').eq('englishquestionhistory') & Attr('type').eq(
    #                     'userenglishquestionhistory')
    #             )
    #             item = response['Items']
    #             for it in item:
    #                 history_PK = it['PK']
    #                 history_SK = it['SK']
    #                 # history_result = it['results']
    #                 # print('history_result===: ', history_result)
    #
    #                 # update englishquestionhistory results attribute
    #                 table.update_item(
    #                     Key={
    #                         'PK': history_PK,
    #                         'SK': history_SK,
    #                     },
    #                     UpdateExpression='SET results.stage_1.lastDate = :val1, results.stage_1.numberOfCompletion = :val2',
    #                     ExpressionAttributeValues={
    #                         ':val1': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
    #                         ':val2': 1,
    #                     }
    #                 ),
    #
    #                 # get existing regularCoin
    #                 getCoin = table.get_item(
    #                     Key={
    #                         'PK': 'englishqusetionsetting',
    #                         'SK': 'englishqusetionsetting'
    #                     }
    #                 )
    #                 regularCoin = getCoin['Item']['regularAddCoin']
    #                 # print('regularCoin=========: ', regularCoin)
    #
    #                 # update englishqusetionsetting coin
    #                 table.update_item(
    #                     Key={
    #                         'PK': 'englishqusetionsetting',
    #                         'SK': 'englishqusetionsetting'
    #                     },
    #                     UpdateExpression='SET regularAddCoin = :val1',
    #                     ExpressionAttributeValues={
    #                         ':val1': regularCoin + 1,
    #                     }
    #                 )
    #                 break
    #         else:
    #             print("englishquestionhistory is None!!!!")
    #             table.put_item(
    #                 Item={
    #                     'PK': 'englishquestionhistory',
    #                     'SK': 'englishquestionhistory#user#' + uuid,
    #                     'results': {
    #                         'stage_1': {
    #                             'lastDate': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
    #                             'numberOfCompletion': 101
    #                         }
    #                     },
    #                     'type': 'userenglishquestionhistory',
    #                 }
    #             ),
    #
    #             # get existing firstTimeAddCoin
    #             getAllCoin = table.get_item(
    #                 Key={
    #                     'PK': 'englishqusetionsetting',
    #                     'SK': 'englishqusetionsetting'
    #                 }
    #             )
    #             firstTimeCoin = getAllCoin['Item']['firstTimeAddCoin']
    #             regularCoin = getAllCoin['Item']['regularAddCoin']
    #             type = getAllCoin['Item']['type']
    #
    #             # create englishqusetionsetting coin
    #             table.put_item(
    #                 Item={
    #                     'PK': 'englishqusetionsetting',
    #                     'SK': 'englishqusetionsetting',
    #                     'firstTimeAddCoin': firstTimeCoin + 3,
    #                     'regularAddCoin': regularCoin,
    #                     'type': type,
    #                 }
    #             )
    #
    #             break
    #         break
    #     else:
    #         print("Stage SK is not found!!!")
    #         break


lambda_handler({'arguments':
                    {'input':
                         {'stageSortKey': 'stage#76b9a255-bbb0-482f-9745-f79429bbc66d'}
                     }
                }, "cd")
