Bikroy Auto Approve

Automated ad approval tool for Bikroy Admin Dashboard using Playwright and Python.
This script streamlines the manual moderation process by automatically checking ad posting limits and approving eligible ads.

Features:

Automated login session handling (bikroy_login.json)
Reads membership limit text such as 3 of 3 ads in Electronics Free
Detects and skips ads when the posting limit is reached (AOL detection)
Automatically clicks the "Save & Approve" button for valid ads
Provides a clear console summary for Approved, Skipped, and Failed ads
Supports multiple ad URLs for batch approval


Language:	Python 3.10+
Framework:	Playwright
Runtime:	AsyncIO

Project Structure:
auto_approve.py         # Main automation script
bikroy_login.json       # Saved browser session (auto-generated)
debug_limit_error_*.png # Debug screenshots for troubleshooting

Installation and Setup
Step 1: Clone the Repository
git clone https://github.com/yourusername/bikroy-auto-approve.git
cd bikroy-auto-approve

Step 2: Install Dependencies
pip install playwright
playwright install

Step 3: Add Your Ad URLs
Edit the URLS list in auto_approve.py:

URLS = [
    "https://admin.bikroy.com/item/68f8b27a0659bc5fgdjytuii",
    "https://admin.bikroy.com/item/68f8b27a0659bc51sghtytt",
]

Usage:
First Run (Login Setup)

Run the script:
python auto_approve.py

When the browser opens, log in manually to the Bikroy Admin Dashboard.
Once logged in, return to the terminal and press ENTER.
Your session will be saved automatically in bikroy_login.json.
Subsequent Runs (Fully Automated)

The script will:
Check each ad’s posting limit
Skip ads when the limit is full
Click Save & Approve for the rest
The end summary will display:

Approved: X
Skipped (AOL): Y
Failed: Z

How It Works

Login Handling
Saves your Playwright browser session to avoid repeated login steps.

Limit Detection
Reads:
<span class="ui-bubble is-membership-limits">3 of 3 ads in Electronics Free</span>
If the current value equals the maximum (for example, 3 of 3), the ad is skipped automatically.

Approval Automation
If the limit is not full, the script locates and clicks the "Save & Approve" button.

Troubleshooting
If the console shows Limit bubble not found, increase the timeout or verify the selector.
If your login session expires, delete bikroy_login.json and run the login process again.
Debug screenshots (debug_limit_error_*.png) are saved automatically when errors occur.

License
This project is intended for internal operational automation within Bikroy.
Ensure compliance with all company security, data, and access policies before deployment.
