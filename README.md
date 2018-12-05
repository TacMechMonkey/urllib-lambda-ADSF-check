# urllib-lambda-webpage-check
python/boto3/lambda script to send a request to an Office 365 landing page as a user, \
parses return details to confirm a successful redirect to the organisation ADFS homepage, \
confirms homepage is correct, raises any errors, and sends a consolodated report to an AWS SNS topic.

Requirements:
- CloudWatch cron trigger every minute { 0/1 * * * ? * }
- No VPC
- 128mb, 10secs is sufficient
- IAM role will need SNS and CloudWatch permissions

IAM policy example:

{
    
    "Version": "2012-10-17",
    
    "Statement": [
    
        {
        
            "Effect": "Allow",
            
            "Action": "sns:Publish",
            
            "Resource": "arn:aws:sns:ap-southeast-2:*"
            
        },
        
        {
        
            "Effect": "Allow",
            
            "Action": "logs:*",
            
            "Resource": "arn:aws:logs:*:*:*"
            
        }
        
    ]
    
} 


This was designed as a simple nightly check to automate a SysAdmin process.

To confirm character count and server names, run the script once and pull details from the response.
