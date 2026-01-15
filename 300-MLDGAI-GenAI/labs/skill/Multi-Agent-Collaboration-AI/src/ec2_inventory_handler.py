import json
import boto3
import os
from typing import Dict, Any
import logging
from decimal import Decimal
from datetime import datetime, timezone
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
ec2_instances_table = dynamodb.Table(os.environ.get('EC2_INSTANCES_TABLE_NAME', 'EC2-Instances'))

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    EC2 instance inventory management Lambda function for Bedrock Agent action group.
    Handles EC2 instance-related queries and operations.
    """
    
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract the action and parameters from the event
        action = event.get('actionGroup', '')
        api_path = event.get('apiPath', '')
        http_method = event.get('httpMethod', '')
        parameters = event.get('parameters', [])
        
        # Convert parameters list to dictionary for easier access
        params_dict = {}
        for param in parameters:
            params_dict[param['name']] = param['value']
        
        logger.info(f"Action: {action}, API Path: {api_path}, Method: {http_method}")
        logger.info(f"Parameters: {params_dict}")
        
        # Route to appropriate function based on API path
        if api_path == '/checkInstance' and http_method == 'POST':
            return check_instance(params_dict, action, api_path, http_method)
        elif api_path == '/listInstances' and http_method == 'POST':
            return list_instances(params_dict, action, api_path, http_method)
        elif api_path == '/countInstancesByType' and http_method == 'POST':
            return count_instances_by_type(params_dict, action, api_path, http_method)
        elif api_path == '/getRunningInstances' and http_method == 'POST':
            return get_running_instances(params_dict, action, api_path, http_method)
        elif api_path == '/getInstancesByZone' and http_method == 'POST':
            return get_instances_by_zone(params_dict, action, api_path, http_method)
        else:
            return {
                'messageVersion': '1.0',
                'response': {
                    'actionGroup': action,
                    'apiPath': api_path,
                    'httpMethod': http_method,
                    'httpStatusCode': 400,
                    'responseBody': {
                        'application/json': {
                            'body': json.dumps({
                                'error': f'Unsupported operation: {http_method} {api_path}'
                            })
                        }
                    }
                }
            }
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', ''),
                'apiPath': event.get('apiPath', ''),
                'httpMethod': event.get('httpMethod', ''),
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({
                            'error': f'Internal server error: {str(e)}'
                        })
                    }
                }
            }
        }

def check_instance(params: Dict[str, str], action_group: str, api_path: str, http_method: str) -> Dict[str, Any]:
    """Check details for a specific EC2 instance."""
    
    instance_id = params.get('instance_id', '')
    
    if not instance_id:
        return create_error_response('instance_id parameter is required', 400, action_group, api_path, http_method)
    
    try:
        # Query DynamoDB for instance data
        response = ec2_instances_table.get_item(
            Key={'instance_id': instance_id}
        )
        
        if 'Item' in response:
            item = response['Item']
            result = {
                'instance_id': instance_id,
                'instance_type': item.get('instance_type', 'unknown'),
                'state': item.get('state', 'unknown'),
                'availability_zone': item.get('availability_zone', 'unknown'),
                'launch_time': item.get('launch_time', ''),
                'private_ip': item.get('private_ip', ''),
                'public_ip': item.get('public_ip', ''),
                'tags': item.get('tags', {}),
                'last_updated': item.get('last_updated', datetime.now(timezone.utc).isoformat())
            }
        else:
            result = {
                'instance_id': instance_id,
                'error': 'EC2 instance not found in inventory'
            }
            
    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")
        return create_error_response(f"Database error: {str(e)}", 500, action_group, api_path, http_method)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return create_error_response(f"Unexpected error: {str(e)}", 500, action_group, api_path, http_method)
    
    return create_success_response(result, action_group, api_path, http_method)

def list_instances(params: Dict[str, str], action_group: str, api_path: str, http_method: str) -> Dict[str, Any]:
    """List all EC2 instances or filter by state, type, or availability zone."""
    
    state_filter = params.get('state', '')
    instance_type_filter = params.get('instance_type', '')
    availability_zone_filter = params.get('availability_zone', '')
    limit = int(params.get('limit', '20'))
    
    try:
        # Build scan parameters
        scan_params = {
            'Limit': limit
        }
        
        # Add filter expressions based on provided parameters
        filter_expressions = []
        expression_values = {}
        expression_names = {}
        
        if state_filter:
            filter_expressions.append('#state_attr = :state')
            expression_values[':state'] = state_filter
            expression_names['#state_attr'] = 'state'
            
        if instance_type_filter:
            filter_expressions.append('instance_type = :itype')
            expression_values[':itype'] = instance_type_filter
            
        if availability_zone_filter:
            filter_expressions.append('availability_zone = :az')
            expression_values[':az'] = availability_zone_filter
        
        if filter_expressions:
            scan_params['FilterExpression'] = ' AND '.join(filter_expressions)
            scan_params['ExpressionAttributeValues'] = expression_values
            if expression_names:
                scan_params['ExpressionAttributeNames'] = expression_names
        
        response = ec2_instances_table.scan(**scan_params)
        
        instances = []
        for item in response.get('Items', []):
            instances.append({
                'instance_id': item.get('instance_id', ''),
                'instance_type': item.get('instance_type', 'unknown'),
                'state': item.get('state', 'unknown'),
                'availability_zone': item.get('availability_zone', 'unknown'),
                'launch_time': item.get('launch_time', ''),
                'private_ip': item.get('private_ip', ''),
                'public_ip': item.get('public_ip', ''),
                'tags': item.get('tags', {})
            })
        
        result = {
            'instances': instances,
            'total_count': len(instances),
            'filters_applied': {
                'state': state_filter if state_filter else 'all',
                'instance_type': instance_type_filter if instance_type_filter else 'all',
                'availability_zone': availability_zone_filter if availability_zone_filter else 'all'
            },
            'scanned_count': response.get('ScannedCount', 0)
        }
        
    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")
        return create_error_response(f"Database error: {str(e)}", 500, action_group, api_path, http_method)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return create_error_response(f"Unexpected error: {str(e)}", 500, action_group, api_path, http_method)
    
    return create_success_response(result, action_group, api_path, http_method)

def count_instances_by_type(params: Dict[str, str], action_group: str, api_path: str, http_method: str) -> Dict[str, Any]:
    """Count EC2 instances by instance type, optionally filtered by state."""
    
    instance_type_filter = params.get('instance_type', '')
    state_filter = params.get('state', 'running')  # Default to running instances
    
    try:
        if instance_type_filter:
            # Use GSI to query specific instance type
            index_name = 'InstanceTypeIndex'
            
            if state_filter:
                # Query the index and filter by state
                response = ec2_instances_table.query(
                    IndexName=index_name,
                    KeyConditionExpression='instance_type = :itype',
                    FilterExpression='#state_attr = :state',
                    ExpressionAttributeNames={
                        '#state_attr': 'state'
                    },
                    ExpressionAttributeValues={
                        ':itype': instance_type_filter,
                        ':state': state_filter
                    }
                )
            else:
                # Query the index without state filter
                response = ec2_instances_table.query(
                    IndexName=index_name,
                    KeyConditionExpression='instance_type = :itype',
                    ExpressionAttributeValues={
                        ':itype': instance_type_filter
                    }
                )
            
            count = response.get('Count', 0)
            result = {
                'instance_type': instance_type_filter,
                'state_filter': state_filter if state_filter else 'all',
                'count': count,
                'instances': [
                    {
                        'instance_id': item.get('instance_id', ''),
                        'state': item.get('state', ''),
                        'availability_zone': item.get('availability_zone', ''),
                        'launch_time': item.get('launch_time', '')
                    }
                    for item in response.get('Items', [])
                ]
            }
        else:
            # Count all instances grouped by type
            scan_params = {}
            
            if state_filter:
                scan_params['FilterExpression'] = '#state_attr = :state'
                scan_params['ExpressionAttributeNames'] = {'#state_attr': 'state'}
                scan_params['ExpressionAttributeValues'] = {':state': state_filter}
            
            response = ec2_instances_table.scan(**scan_params)
            
            # Group by instance type
            type_counts = {}
            instances_by_type = {}
            
            for item in response.get('Items', []):
                itype = item.get('instance_type', 'unknown')
                if itype not in type_counts:
                    type_counts[itype] = 0
                    instances_by_type[itype] = []
                
                type_counts[itype] += 1
                instances_by_type[itype].append({
                    'instance_id': item.get('instance_id', ''),
                    'state': item.get('state', ''),
                    'availability_zone': item.get('availability_zone', ''),
                    'launch_time': item.get('launch_time', '')
                })
            
            result = {
                'state_filter': state_filter if state_filter else 'all',
                'total_instances': sum(type_counts.values()),
                'instance_type_counts': type_counts,
                'instances_by_type': instances_by_type
            }
        
    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")
        return create_error_response(f"Database error: {str(e)}", 500, action_group, api_path, http_method)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return create_error_response(f"Unexpected error: {str(e)}", 500, action_group, api_path, http_method)
    
    return create_success_response(result, action_group, api_path, http_method)

def get_running_instances(params: Dict[str, str], action_group: str, api_path: str, http_method: str) -> Dict[str, Any]:
    """Get all running EC2 instances."""
    
    instance_type_filter = params.get('instance_type', '')
    
    try:
        # Use state index to get running instances
        index_name = 'StateIndex'
        
        query_params = {
            'IndexName': index_name,
            'KeyConditionExpression': '#state_attr = :state',
            'ExpressionAttributeNames': {
                '#state_attr': 'state'
            },
            'ExpressionAttributeValues': {
                ':state': 'running'
            }
        }
        
        if instance_type_filter:
            query_params['FilterExpression'] = 'instance_type = :itype'
            query_params['ExpressionAttributeValues'][':itype'] = instance_type_filter
        
        response = ec2_instances_table.query(**query_params)
        
        running_instances = []
        for item in response.get('Items', []):
            running_instances.append({
                'instance_id': item.get('instance_id', ''),
                'instance_type': item.get('instance_type', 'unknown'),
                'availability_zone': item.get('availability_zone', 'unknown'),
                'launch_time': item.get('launch_time', ''),
                'private_ip': item.get('private_ip', ''),
                'public_ip': item.get('public_ip', ''),
                'tags': item.get('tags', {})
            })
        
        result = {
            'running_instances': running_instances,
            'count': len(running_instances),
            'instance_type_filter': instance_type_filter if instance_type_filter else 'all'
        }
        
    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")
        return create_error_response(f"Database error: {str(e)}", 500, action_group, api_path, http_method)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return create_error_response(f"Unexpected error: {str(e)}", 500, action_group, api_path, http_method)
    
    return create_success_response(result, action_group, api_path, http_method)

def get_instances_by_zone(params: Dict[str, str], action_group: str, api_path: str, http_method: str) -> Dict[str, Any]:
    """Get EC2 instances grouped by availability zone."""
    
    availability_zone = params.get('availability_zone', '')
    state_filter = params.get('state', '')
    
    try:
        scan_params = {}
        filter_expressions = []
        expression_values = {}
        expression_names = {}
        
        if availability_zone:
            filter_expressions.append('availability_zone = :az')
            expression_values[':az'] = availability_zone
            
        if state_filter:
            filter_expressions.append('#state_attr = :state')
            expression_values[':state'] = state_filter
            expression_names['#state_attr'] = 'state'
        
        if filter_expressions:
            scan_params['FilterExpression'] = ' AND '.join(filter_expressions)
            scan_params['ExpressionAttributeValues'] = expression_values
            if expression_names:
                scan_params['ExpressionAttributeNames'] = expression_names
        
        response = ec2_instances_table.scan(**scan_params)
        
        if availability_zone:
            # Return instances for specific zone
            instances = []
            for item in response.get('Items', []):
                instances.append({
                    'instance_id': item.get('instance_id', ''),
                    'instance_type': item.get('instance_type', 'unknown'),
                    'state': item.get('state', 'unknown'),
                    'launch_time': item.get('launch_time', ''),
                    'private_ip': item.get('private_ip', ''),
                    'public_ip': item.get('public_ip', '')
                })
            
            result = {
                'availability_zone': availability_zone,
                'state_filter': state_filter if state_filter else 'all',
                'instances': instances,
                'count': len(instances)
            }
        else:
            # Group instances by availability zone
            zones = {}
            for item in response.get('Items', []):
                zone = item.get('availability_zone', 'unknown')
                if zone not in zones:
                    zones[zone] = []
                
                zones[zone].append({
                    'instance_id': item.get('instance_id', ''),
                    'instance_type': item.get('instance_type', 'unknown'),
                    'state': item.get('state', 'unknown'),
                    'launch_time': item.get('launch_time', ''),
                    'private_ip': item.get('private_ip', ''),
                    'public_ip': item.get('public_ip', '')
                })
            
            zone_counts = {zone: len(instances) for zone, instances in zones.items()}
            
            result = {
                'state_filter': state_filter if state_filter else 'all',
                'zones': zones,
                'zone_counts': zone_counts,
                'total_instances': sum(zone_counts.values())
            }
        
    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")
        return create_error_response(f"Database error: {str(e)}", 500, action_group, api_path, http_method)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return create_error_response(f"Unexpected error: {str(e)}", 500, action_group, api_path, http_method)
    
    return create_success_response(result, action_group, api_path, http_method)

def create_success_response(data: Dict[str, Any], action_group: str, api_path: str, http_method: str) -> Dict[str, Any]:
    """Create a successful response for Bedrock Agent."""
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': action_group,
            'apiPath': api_path,
            'httpMethod': http_method,
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(data, default=str)
                }
            }
        }
    }

def create_error_response(error_message: str, status_code: int, action_group: str, api_path: str, http_method: str) -> Dict[str, Any]:
    """Create an error response for Bedrock Agent."""
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': action_group,
            'apiPath': api_path,
            'httpMethod': http_method,
            'httpStatusCode': status_code,
            'responseBody': {
                'application/json': {
                    'body': json.dumps({
                        'error': error_message
                    })
                }
            }
        }
    }