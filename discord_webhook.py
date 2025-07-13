"""
    @author RazrCraft
    @create date 2025-06-25 15:36:23
    @modify date 2025-06-25 16:55:22
    @desc Discord Webhook Send Example
 """
import sys
import requests

if len(sys.argv) < 2 or not sys.argv[1].strip():
    print("Error: Content argument is required and cannot be empty.", file=sys.stderr)
    print("Usage: discord_webhook <content>", file=sys.stderr)
    sys.exit(1)

content = " ".join(sys.argv[1:])

# Replace with your actual Discord webhook URL
webhook_url = "YOUR_DISCORD_WEBHOOK_URL"

# Define the message data
data = {
    "content": f"{content}",
    "username": "Python Bot",  # Optional: Customize the sender"s name
    "avatar_url": "https://img.icons8.com/color/64/python.png" # Optional: Customize the sender"s avatar
}

# Send the POST request
response = requests.post(webhook_url, json=data, timeout=10)

# Check the response status
if response.status_code == 204:
    print("Message sent successfully!")
elif response.status_code == 429:
    print(f"Rate limited by Discord. Please wait before sending again. (Status: {response.status_code})")
else:
    print(f"Failed to send message: {response.status_code} - {response.text}")
