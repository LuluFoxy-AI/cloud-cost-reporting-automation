# Cloud Cost Reporting Automation

> Automate your AWS cost reporting and stop manually exporting CSVs every month

## Description

This tool automatically pulls cost data from AWS Cost Explorer API and posts a formatted breakdown to Slack on a weekly basis. No more manual CSV exports, no more spreadsheet wrangling, no more forgetting to send the monthly cost report.

## What It Does

- **Fetches AWS cost data** using the Cost Explorer API
- **Aggregates costs by service** over a configurable time period (default: 7 days)
- **Formats a clean report** showing top services by spend with percentages
- **Posts directly to Slack** via webhook for team visibility
- **Runs on-demand or via cron** for automated weekly/monthly reports

Perfect for DevOps teams, FinOps practitioners, and engineering managers who need regular cost visibility without the manual overhead.

## Installation

### Prerequisites

- Python 3.7 or higher
- AWS account with Cost Explorer enabled
- AWS credentials configured (IAM user with `ce:GetCostAndUsage` permission)
- Slack workspace with webhook access

### Setup

1. Clone this repository:
```bash
git clone https://github.com/LuluFoxy-AI/cloud-cost-reporting-automation.git
cd cloud-cost-reporting-automation
```

2. Install dependencies:
```bash
pip install boto3
```

3. Configure AWS credentials (if not already done):
```bash
aws configure
```

4. Create a Slack webhook:
   - Go to https://api.slack.com/messaging/webhooks
   - Create a new webhook for your workspace
   - Copy the webhook URL

## Usage

### Basic Usage

Set your Slack webhook URL as an environment variable:

```bash
export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
```

Run the script:

```bash
python aws_cost_reporter.py
```

### Custom Time Period

Change the reporting period (default is 7 days):

```bash
export COST_REPORT_DAYS=30
python aws_cost_reporter.py
```

### Automated Weekly Reports

Add to your crontab for weekly Monday morning reports:

```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/script && /usr/bin/python3 aws_cost_reporter.py
```

## Configuration

### Environment Variables

- `SLACK_WEBHOOK_URL` (required): Your Slack webhook URL
- `COST_REPORT_DAYS` (optional): Number of days to include in report (default: 7)

### AWS IAM Permissions

Your AWS user/role needs the following permission:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ce:GetCostAndUsage",
      "Resource": "*"
    }
  ]
}
```

## Free vs Paid Version

### Free Version (This Repository)
- Single AWS account support
- Weekly cost reports by service
- Slack notifications
- Basic formatting

### Pro Version ($39 on Gumroad)
- **Multi-account support** with AWS Organizations
- **Multi-cloud support** (AWS + GCP + Azure)
- **Custom cost allocation tags** and filtering
- **Budget alerts** with threshold notifications
- **Historical trend analysis** with charts
- **Email reports** in addition to Slack
- **Detailed documentation** and setup guides
- **Priority support** via email

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this in your organization.