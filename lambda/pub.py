import boto3
import json

iot_client = boto3.client('iot-data', region_name='ap-southeast-1')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        plant_id = body.get('plant_id')
        state = body.get('state')

        if not isinstance(plant_id, int) or state not in ["on", "off"]:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid request. "plant_id" must be an integer and "state" must be "on" or "off".'})
            }

        message = {
            "actuator": f"relay{plant_id}",
            "state": state
        }

        topic = "sdk/test/python"
        iot_client.publish(
            topic=topic,
            qos=1,
            payload=json.dumps(message)
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Message published to MQTT topic!'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
