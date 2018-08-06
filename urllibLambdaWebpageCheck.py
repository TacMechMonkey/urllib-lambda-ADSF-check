# This python/boto3/lambda script sends a request to an Office 365 landing page, parses return details to confirm a successful /
# redirect to the organisation's ADFS homepage, authenticates homepage is correct, raises any errors, and sends a consolodated /
# report to an AWS SNS topic.
# Run once to produce pageserver and htmlchar values for global variables.

# Original from https://github.com/TacMechMonkey/urllib-lambda-webpage-check/edit/master/urllibLambdaWebpageCheck.py
# Known issue: the code produces 2 emails for failures if in Lambda. https://stackoverflow.com/questions/51705061/lambda-boto3-python-issue

# Import required modules
import boto3
import urllib.request
from urllib.request import Request, urlopen
from datetime import datetime
import time
import re

# Global variables to be set
url = "https://outlook.com/CONTOSSO.com"
adfslink = "https://sts.CONTOSSO.com/adfs/ls/?client-request-id="

# Input after first run
pageserver = "Microsoft-HTTPAPI/2.0 Microsoft-HTTPAPI/2.0"
htmlchar = 17600

# Input AWS SNS ARN
snsarn = 'arn:aws:sns:ap-southeast-2:XXXXXXXXXXXXX:Daily_Check_Notifications_CONTOSSO'
sns = boto3.client('sns')

def pagecheck():
    # Present the request to the webpage as coming from a user in a browser
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    values = {'name' : 'user'}
    headers = { 'User-Agent' : user_agent }    
    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')

    # "Null" the Message Detail and Error lists
    msgdet_list = []
    error_list = []

    request = Request(url)
    req = urllib.request.Request(url, data, headers)
    response = urlopen(request)

    with urllib.request.urlopen(request) as response:

        # Get the URL. This gets the real URL. 
        acturl = response.geturl()
        msgdet_list.append("\nThe Actual URL is:")
        msgdet_list.append(str(acturl))

        if adfslink not in acturl:
            error_list.append(str("Redirect Fail"))

        # Get the HTTP resonse code
        httpcode = response.code
        msgdet_list.append("\nThe HTTP code is: ")
        msgdet_list.append(str(httpcode))

        if httpcode//200 != 1:
            error_list.append(str("No HTTP 200 Code"))

        # Get the Headers as a dictionary-like object
        headers = response.info()
        msgdet_list.append("\nThe Headers are:")
        msgdet_list.append(str(headers))

        if response.info() == "":
            error_list.append(str("Header Error"))

        # Get the date of request and compare to UTC (DD MMM YYYY HH MM)
        date = response.info()['date']
        msgdet_list.append("The Date is: ")
        msgdet_list.append(str(date))
        returndate = str(date.split( )[1:5])
        returndate = re.sub(r'[^\w\s]','',returndate)
        returndate = returndate[:-2]
        currentdate = datetime.utcnow()
        currentdate = currentdate.strftime("%d %b %Y %H%M")

        if returndate != currentdate:
            date_error = ("Date Error. Returned Date: ", returndate, "Expected Date: ", currentdate, "Times in UTC (DD MMM YYYY HH MM)")
            date_error = str(date_error)
            date_error = re.sub(r'[^\w\s]','',date_error)
            error_list.append(str(date_error))

        # Get the server
        headerserver = response.info()['server']
        msgdet_list.append("\nThe Server is: ")
        msgdet_list.append(str(headerserver))

        if pageserver not in headerserver:
            error_list.append(str("Server Error"))

        # Get all HTML data and confirm no major change to content size by character lenth (global var: htmlchar
        html = response.read()
        htmllength = len(html)
        msgdet_list.append("\nHTML Length is: ")
        msgdet_list.append(str(htmllength))
        msgdet_list.append("\nThe Full HTML is: ")
        msgdet_list.append(str(html))
        msgdet_list.append("\n")

        if htmllength // htmlchar != 1:
            error_list.append(str("Page HTML Error - incorrect # of characters"))

        if adfslink not in str(acturl):
            error_list.append(str("ADFS Link Error"))

        error_list.append("\n")
        error_count = len(error_list)

        if error_count == 1:
            error_list.insert(0, 'No Errors Found.')
        elif error_count == 2:
            error_list.insert(0, 'Error Found:')
        else:
            error_list.insert(0, 'Multiple Errors Found:')

        # Pass completed results and data to the notification() function
        notification(msgdet_list, error_list)

        # return

# Use AWS SNS to create a notification email with the additional data generated
def notification(msgdet_list, error_list):
    datacheck = str("\n".join(msgdet_list))
    errorcheck = str("\n".join(error_list))
    notificationbody = str(errorcheck + datacheck)

    if error_list != ['No Errors Found.', '\n']:
        result = 'FAILED!'
    else:
        result = 'passed.'

    notificationheader = str('The daily ADFS check has been marked as ' + result)

    if result != 'passed.':

        message = sns.publish(
            TopicArn = snsarn,
            Subject = notificationheader,
            Message = notificationbody
        )

        # Output result to CloudWatch Logs
        print('Response: ' + notificationheader)

        # return

    else:
        error_list = str(error_list)
        print('Response: ' + notificationheader + ' ' + error_list)

        # return

# Trigger the Lambda handler
def lambda_handler(event, context):
    aws_account_ids = [context.invoked_function_arn.split(":")[4]]
    pagecheck()

    return "Successful"
