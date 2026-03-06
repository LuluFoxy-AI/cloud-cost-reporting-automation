#!/usr/bin/env python3
"""
AWS Cost Explorer to Slack Reporter

Automatically pulls weekly AWS cost breakdown by service and posts to Slack.
Free tier version - supports single AWS account and basic cost reporting.

Requirements:
- AWS credentials configured (via ~/.aws/credentials or environment variables)
- Slack webhook URL
- boto3 library
"""

import os
import sys
import json
from datetime import datetime, timedelta
from urllib import request, error
from urllib.parse import urlencode

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("Error: boto3 is required. Install with: pip install boto3")
    sys.exit(1)


class AWSCostReporter:
    """Handles AWS Cost Explorer API interactions and report generation."""
    
    def __init__(self, days_back=7):
        """
        Initialize the cost reporter.
        
        Args:
            days_back (int): Number of days to look back for cost data
        """
        self.days_back = days_back
        try:
            self.ce_client = boto3.client('ce', region_name='us-east-1')
        except NoCredentialsError:
            print("Error: AWS credentials not found. Configure via AWS CLI or environment variables.")
            sys.exit(1)
    
    def get_cost_data(self):
        """
        Fetch cost data from AWS Cost Explorer API.
        
        Returns:
            dict: Cost data grouped by service
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=self.days_back)
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            return response
        except ClientError as e:
            print(f"Error fetching cost data: {e}")
            sys.exit(1)
    
    def parse_cost_data(self, raw_data):
        """
        Parse and aggregate cost data by service.
        
        Args:
            raw_data (dict): Raw response from Cost Explorer API
            
        Returns:
            list: Sorted list of tuples (service_name, total_cost)
        """
        service_costs = {}
        
        for result in raw_data.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                service_costs[service] = service_costs.get(service, 0) + cost
        
        # Sort by cost descending
        sorted_costs = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
        return sorted_costs
    
    def format_report(self, cost_data, start_date, end_date):
        """
        Format cost data into a readable report.
        
        Args:
            cost_data (list): Sorted list of (service, cost) tuples
            start_date (str): Report start date
            end_date (str): Report end date
            
        Returns:
            str: Formatted report text
        """
        total_cost = sum(cost for _, cost in cost_data)
        
        report_lines = [
            f"*AWS Cost Report: {start_date} to {end_date}*",
            f"Total Cost: *${total_cost:.2f}*\n",
            "*Top Services by Cost:*"
        ]
        
        # Show top 10 services
        for service, cost in cost_data[:10]:
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            report_lines.append(f"• {service}: ${cost:.2f} ({percentage:.1f}%)")
        
        if len(cost_data) > 10:
            other_cost = sum(cost for _, cost in cost_data[10:])
            other_percentage = (other_cost / total_cost * 100) if total_cost > 0 else 0
            report_lines.append(f"• Other ({len(cost_data) - 10} services): ${other_cost:.2f} ({other_percentage:.1f}%)")
        
        return "\n".join(report_lines)


class SlackNotifier:
    """Handles Slack webhook notifications."""
    
    def __init__(self, webhook_url):
        """
        Initialize Slack notifier.
        
        Args:
            webhook_url (str): Slack webhook URL
        """
        self.webhook_url = webhook_url
    
    def send_message(self, text):
        """
        Send a message to Slack.
        
        Args:
            text (str): Message text to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        payload = {
            'text': text,
            'mrkdwn': True
        }
        
        try:
            req = request.Request(
                self.webhook_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with request.urlopen(req) as response:
                if response.status == 200:
                    print("Successfully sent report to Slack")
                    return True
                else:
                    print(f"Failed to send to Slack. Status: {response.status}")
                    return False
        except error.URLError as e:
            print(f"Error sending to Slack: {e}")
            return False


def main():
    """Main execution function."""
    # Get configuration from environment variables
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    days_back = int(os.environ.get('COST_REPORT_DAYS', '7'))
    
    if not slack_webhook:
        print("Error: SLACK_WEBHOOK_URL environment variable not set")
        print("Set it with: export SLACK_WEBHOOK_URL='your-webhook-url'")
        sys.exit(1)
    
    print(f"Generating AWS cost report for the last {days_back} days...")
    
    # Initialize reporter and fetch data
    reporter = AWSCostReporter(days_back=days_back)
    raw_data = reporter.get_cost_data()
    cost_data = reporter.parse_cost_data(raw_data)
    
    if not cost_data:
        print("No cost data found for the specified period")
        sys.exit(0)
    
    # Generate report
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    report = reporter.format_report(
        cost_data,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    print("\n" + report + "\n")
    
    # Send to Slack
    notifier = SlackNotifier(slack_webhook)
    notifier.send_message(report)


if __name__ == '__main__':
    main()