import boto3
import botocore.config
import json
from datetime import datetime

def blog(topic:str)-> str:
    prompt = f"""<s>[INST]Human: Write a 250 word blog post on the topic {topic}
    Assistant:[/INST]
    """ 
    body={
        "prompt": prompt,
        "max_gen_len" :512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        bedrock = boto3.client("bedrock_runtime", region_name="us-east-1", 
                               config=botocore.config.Config(read_timeout=300, retries={"max_attempts": 3}))
        response = bedrock.invoke_model(body=json.dumps(body), modelId="meta.llama2-13b-chat-v1")

        response_content=response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)
        blog_details = response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog post: {e}")
        return " "
    

def save_to_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
    print(f"Blog post saved to s3 bucket {s3_bucket} with key {s3_key}")
    return s3_key
    
def lambda_handler(event, context):
    
    event=json.loads(event['body'])
    topic=event['blog_topic']
    generate_blog=blog(topic=topic)

    if generate_blog:
        current_time = datetime.now().strftime('%H%M%S')
        s3_key=f"output/{current_time}.txt"
        s3_bucket='blogenerator'
        save_to_s3(s3_key, s3_bucket, generate_blog)
    
    else:
        print("No blog generated")

    return {
        'statusCode': 200,
        'body': json.dumps('Blog generated successfully')
    }