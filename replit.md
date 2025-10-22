# Discord Ballfight Bot

## Overview
This is a Discord bot that manages "ballfight" requests. Users can mention other Discord members to create a ballfight request, which downloads their avatars and sends them for review. Moderators can approve or deny requests using reaction emojis.

## Project Type
- **Backend Discord Bot** (no frontend)
- **Language**: Python 3.11
- **Main Dependencies**: discord.py, Pillow, aiohttp

## Recent Changes
- **2025-10-22**: Imported from GitHub and configured for Replit environment
  - Fixed file paths from Windows to Linux (relative paths)
  - Moved Discord token and channel IDs to environment variables for security
  - Created requirements.txt for dependency management
  - Set up workflow to run the bot
  - Added .gitignore for Python best practices

## How It Works

### Commands
- `!balls @user1 @user2 [@user3...]` - Creates a ballfight request with mentioned users
  - Requires at least 2 users mentioned
  - Downloads avatar images for each mentioned user
  - Sends request to review channel for approval

### Workflow
1. User runs `!balls` command with mentions
2. Bot downloads avatars and creates a request folder
3. Request is sent to review channel with ✅ and ❌ reactions
4. Moderator reacts with ✅ to approve or ❌ to deny
5. Approved requests are moved to accepted folder
6. Denied requests are deleted
7. Results are posted to result channel

## Configuration

### Required Secrets
Set these in Replit Secrets:
- `DISCORD_TOKEN` - Your Discord bot token (required)
- `REVIEW_CHANNEL_ID` - Discord channel ID for review (default: 1429486591440588993)
- `RESULT_CHANNEL_ID` - Discord channel ID for results (default: 1429744076714016829)

### File Structure
```
requests/
├── pending/        # New requests awaiting review
└── accepted/       # Approved requests
```

## Setup Instructions

1. **Get Discord Bot Token**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application or select existing one
   - Go to "Bot" section and copy your token
   - Add token to Replit Secrets as `DISCORD_TOKEN`

2. **Configure Channel IDs**:
   - Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
   - Right-click on review channel > Copy ID
   - Right-click on result channel > Copy ID
   - Add these to Replit Secrets as `REVIEW_CHANNEL_ID` and `RESULT_CHANNEL_ID`

3. **Bot Permissions**:
   Your bot needs these Discord permissions:
   - Read Messages/View Channels
   - Send Messages
   - Attach Files
   - Add Reactions
   - Read Message History

4. **Run the Bot**:
   - Set the required secrets
   - The bot will start automatically via the "Discord Bot" workflow

## Project Architecture
- **ballbot.py** - Main bot file with all commands and event handlers
- **requirements.txt** - Python dependencies
- **requests/** - Storage for request data and avatars (auto-created)

## User Preferences
None specified yet.
