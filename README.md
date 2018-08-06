# urllib-lambda-webpage-check
python/boto3/lambda script to send a request to an Office 365 landing page as a user, \
parses return details to confirm a successful redirect to the organisation ADFS homepage, \
confirms homepage is correct, raises any errors, and sends a consolodated report to an AWS SNS topic.

IAM role will need SNS and CloudWatch permissions.

This was designed as a simple nightly check to automate a SysAdmin process.

To confirm character count and server names, run the script once and pull details from the response.

Still needs: URL/HTTPError.code + .reason in exception handling.

Runs locally no probs, known issue with Lambda/SNS however: produces 2 emails for failures - https://stackoverflow.com/questions/51705061/lambda-boto3-python-issue
