# urllib-lambda-webpage-check
python/boto3/lambda script to send a request to an Office 365 landing page as a user, \
parses return details to confirm a successful redirect to the organisation ADFS homepage, \
confirms homepage is correct, raises any errors, and sends a consolodated report to an AWS SNS topic.

IAM role will need SNS and CloudWatch permissions.

This was designed as a simple nightly check to automate a SysAdmin process.

To confirm character count and server names, run the script once and pull details from the response.

Still needs: URL/HTTPError.code + .reason in exception handling.

Have run through IDLE no probs (comment out from "message = sns.publish..", print lines notificationheader and \
notificationbody, add pagecheck() to end. pagecheck() should/will be main().

Will update once run through Lambda. Shortly.
