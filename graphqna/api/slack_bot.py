"""Slack bot integration for GraphQnA."""

import logging
import os
import re
import time
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Print environment variables for debugging (without showing actual values)
logger.info(f"SLACK_BOT_TOKEN exists: {bool(os.environ.get('SLACK_BOT_TOKEN'))}")
logger.info(f"SLACK_APP_TOKEN exists: {bool(os.environ.get('SLACK_APP_TOKEN'))}")
logger.info(f"SLACK_SIGNING_SECRET exists: {bool(os.environ.get('SLACK_SIGNING_SECRET'))}")

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# API configuration
DEFAULT_API_URL = "http://localhost:8000"
API_URL = os.environ.get("GRAPHQNA_API_URL", DEFAULT_API_URL)

# Slack configuration
MONITORED_CHANNELS = os.environ.get("SLACK_MONITORED_CHANNELS", "general,ask_vivun").split(",")
ALWAYS_RESPOND_CHANNELS = os.environ.get("SLACK_ALWAYS_RESPOND_CHANNELS", "ask_vivun").split(",")


def query_graphqna(question: str, method: str = "graphrag") -> Dict[str, Any]:
    """
    Query the GraphQnA API.
    
    Args:
        question: The question to ask
        method: The retrieval method to use
        
    Returns:
        The API response
    """
    url = f"{API_URL}/api/query"
    
    try:
        response = requests.post(
            url,
            json={
                "query": question,
                "retrieval_method": method
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return {
                "error": f"API error: {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        logger.error(f"Error querying GraphQnA: {str(e)}")
        return {
            "error": "Failed to connect to GraphQnA API",
            "details": str(e)
        }


def format_slack_message(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a response for Slack display.
    
    Args:
        response: The API response
        
    Returns:
        Formatted Slack message blocks
    """
    # Check for errors
    if "error" in response:
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Error:* {response.get('error')}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Details: {response.get('details', 'No details provided')}"
                    }
                }
            ]
        }
    
    # Regular response
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Answer:*\n{response.get('answer', 'No answer provided')}"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Method: {response.get('retrieval_method', 'unknown')} | "
                           f"Time: {response.get('query_time', 0):.2f}s"
                }
            ]
        }
    ]
    
    # Add any source references if available
    if "metadata" in response and "sources" in response["metadata"]:
        source_block = {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Sources:* " + ", ".join(response["metadata"]["sources"])
                }
            ]
        }
        blocks.append(source_block)
    
    # Add a feedback section
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "👍 Helpful"
                    },
                    "value": "helpful",
                    "action_id": "feedback_helpful"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "👎 Not Helpful"
                    },
                    "value": "not_helpful",
                    "action_id": "feedback_not_helpful"
                }
            ]
        }
    ])
    
    return {"blocks": blocks}


# Event handlers
@app.event("app_mention")
def handle_app_mention(event, say, client):
    """Handle app mentions in channels."""
    logger.info(f"Received app_mention event: {event}")
    
    # Extract the question from the message
    text = event["text"]
    # Remove the app mention
    question = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
    
    if not question:
        try:
            # Reply in a thread if possible
            thread_ts = event.get("thread_ts", event.get("ts"))
            client.chat_postMessage(
                channel=event["channel"],
                thread_ts=thread_ts,
                text="Please ask me a question! For example: @GraphQnA What is a knowledge graph?"
            )
        except:
            # Fallback to simple say
            say("Please ask me a question! For example: @GraphQnA What is a knowledge graph?")
        return
    
    # Check if message is in a thread
    thread_ts = event.get("thread_ts")
    # Get the correct ts to reply to (either the thread parent or this message)
    reply_ts = thread_ts if thread_ts else event.get("ts")
    
    # Send acknowledgment
    try:
        client.chat_postMessage(
            channel=event["channel"],
            thread_ts=reply_ts,
            text=f"Thinking about: '{question}'..."
        )
    except:
        # Fallback to simple say
        say(f"Thinking about: '{question}'...")
    
    # Query the GraphQnA API
    response = query_graphqna(question)
    
    # Send the formatted response in a thread
    try:
        client.chat_postMessage(
            channel=event["channel"],
            thread_ts=reply_ts,
            **format_slack_message(response)
        )
    except Exception as e:
        logger.error(f"Error sending app_mention response: {str(e)}")
        # Fallback to simple say
        say(**format_slack_message(response))


@app.event("message")
def handle_all_messages(event, say, client):
    """Handle all messages, routing to appropriate handlers based on channel type."""
    logger.info(f"Received message event with subtype: {event.get('subtype')}")
    
    # Skip messages from bots to prevent loops
    if event.get("bot_id"):
        logger.info("Skipping bot message")
        return
        
    # Skip message changed/deleted events
    if event.get("subtype") in ["message_changed", "message_deleted"]:
        logger.info(f"Skipping {event.get('subtype')} event")
        return
    
    # Get the channel type
    channel_type = event.get("channel_type")
    logger.info(f"Message channel type: {channel_type}")
    
    # Debug info
    if "text" in event:
        logger.info(f"Message text: {event['text'][:30]}...")
    
    # Route to appropriate handler
    if channel_type == "im":
        logger.info("Routing to direct message handler")
        handle_direct_message(event, say)
    elif channel_type in ["channel", "group"]:
        logger.info("Routing to channel message handler")
        handle_channel_message(event, say, client)
    else:
        logger.info(f"Ignoring message with channel_type: {channel_type}")
        
# Functions to handle different types of messages
def handle_direct_message(event, say):
    """Handle direct messages to the bot."""
    logger.info(f"Processing direct message: {event.get('text', '')[:20]}...")
    
    # Extract the question
    question = event["text"].strip()
    
    if not question:
        say("Please ask me a question!")
        return
    
    # Send acknowledgment
    say(f"Thinking about: '{question}'...")
    
    # Query the GraphQnA API
    response = query_graphqna(question)
    
    # Send the formatted response
    say(**format_slack_message(response))


def handle_channel_message(event, say, client):
    """Handle messages in channels the bot is in."""
    logger.info(f"Processing channel message: {event.get('text', '')[:20]}...")
    
    # Skip already threaded messages that aren't the parent message
    thread_ts = event.get("thread_ts")
    ts = event.get("ts")
    if thread_ts and thread_ts != ts:
        logger.info("Skipping reply in thread (not the parent message)")
        return
    
    # Get channel info to check if this is a monitored channel
    try:
        channel_info = client.conversations_info(channel=event["channel"])
        channel_name = channel_info["channel"]["name"]
        
        # Only respond in configured monitored channels
        channel_name_lower = channel_name.strip().lower()
        monitored_channels_lower = [c.strip().lower() for c in MONITORED_CHANNELS]
        
        if channel_name_lower not in monitored_channels_lower:
            logger.info(f"Ignoring message in non-monitored channel: {channel_name}")
            return
        
        # Check if we're in an "always respond" channel - special handling for ask_vivun
        is_always_respond = channel_name_lower in [c.strip().lower() for c in ALWAYS_RESPOND_CHANNELS]
        logger.info(f"Processing message in channel: {channel_name} (always respond: {is_always_respond})")
    except Exception as e:
        logger.error(f"Error getting channel info: {str(e)}")
        return
    
    # Extract the question
    question = event["text"].strip()
    
    if not question:
        return
    
    # Get the correct ts to reply to (either the thread parent or this message)
    reply_ts = thread_ts if thread_ts else ts
    
    logger.info(f"Will respond using ts: {reply_ts}")
    
    # Query the GraphQnA API
    response = query_graphqna(question)
    
    # Check if we should respond based on answer quality and channel
    no_info_phrases = [
        "I don't have enough information",
        "I couldn't find information",
        "no relevant information",
        "not enough context"
    ]
    
    has_good_answer = not any(phrase.lower() in response.get("answer", "").lower() for phrase in no_info_phrases)
    
    # Only respond if we have a good answer OR we're in an always-respond channel
    if not has_good_answer and not is_always_respond:
        logger.info(f"Not responding as answer indicates insufficient information and not in always-respond channel")
        return
        
    # If we're in an always-respond channel but don't have a good answer, modify the response
    if not has_good_answer and is_always_respond:
        logger.info("In always-respond channel but no good answer - will add disclaimer")
        current_answer = response.get("answer", "")
        response["answer"] = "I'm not entirely sure about this, but here's what I found:\n\n" + current_answer
    
    # Send the response in a thread
    try:
        client.chat_postMessage(
            channel=event["channel"],
            thread_ts=reply_ts,
            **format_slack_message(response)
        )
        logger.info(f"Sent response in thread")
    except Exception as e:
        logger.error(f"Error sending response: {str(e)}")
        
        # Fallback - try to send a simpler message
        try:
            client.chat_postMessage(
                channel=event["channel"],
                thread_ts=reply_ts,
                text=f"I found an answer: {response.get('answer', 'No answer available')}"
            )
        except Exception as e2:
            logger.error(f"Failed to send even the fallback message: {str(e2)}")
            pass


@app.action("feedback_helpful")
def handle_helpful_feedback(ack, body, say):
    """Handle positive feedback."""
    ack()
    user = body["user"]["name"]
    say(f"Thanks for the feedback, {user}! I'm glad the answer was helpful.")
    # In a real implementation, you would log this feedback for improvement


@app.action("feedback_not_helpful")
def handle_not_helpful_feedback(ack, body, say, client):
    """Handle negative feedback and initiate a follow-up."""
    ack()
    user = body["user"]["name"]
    
    # Open a modal to collect more feedback
    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "feedback_modal",
                "title": {"type": "plain_text", "text": "Feedback"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "feedback_input",
                        "label": {"type": "plain_text", "text": "What was wrong with the answer?"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "feedback_text",
                            "multiline": True,
                            "placeholder": {"type": "plain_text", "text": "Please tell us how we can improve..."}
                        }
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error opening feedback modal: {str(e)}")
        say(f"Thanks for the feedback, {user}. Sorry the answer wasn't helpful!")


@app.view("feedback_modal")
def handle_feedback_submission(ack, body, view, say, client):
    """Handle feedback form submission."""
    ack()
    
    # Extract the feedback text
    feedback = view["state"]["values"]["feedback_input"]["feedback_text"]["value"]
    user = body["user"]["name"]
    
    # Log the feedback for improvement
    logger.info(f"Feedback from {user}: {feedback}")
    
    # In a production system, this would be stored in a database
    # and potentially used for model fine-tuning
    
    # Send a thank you message in the original channel
    try:
        client.chat_postMessage(
            channel=user,
            text=f"Thank you for your feedback! We'll use it to improve future responses."
        )
    except Exception as e:
        logger.error(f"Error sending feedback confirmation: {str(e)}")


def start_slack_bot():
    """Start the Slack bot."""
    try:
        # Check for required environment variables
        if not os.environ.get("SLACK_BOT_TOKEN") or not os.environ.get("SLACK_APP_TOKEN"):
            logger.error("Missing required environment variables: SLACK_BOT_TOKEN or SLACK_APP_TOKEN")
            print("Error: Please set SLACK_BOT_TOKEN and SLACK_APP_TOKEN environment variables")
            print("Example:")
            print("  export SLACK_BOT_TOKEN=xoxb-your-bot-token")
            print("  export SLACK_APP_TOKEN=xapp-your-app-token")
            return
        
        # Show bot token (partially masked)
        bot_token = os.environ.get("SLACK_BOT_TOKEN", "")
        if bot_token:
            masked_token = f"{bot_token[:10]}...{bot_token[-4:]}" if len(bot_token) > 14 else "***"
            print(f"Using bot token: {masked_token}")
        
        # Show app token (partially masked)
        app_token = os.environ.get("SLACK_APP_TOKEN", "")
        if app_token:
            masked_token = f"{app_token[:10]}...{app_token[-4:]}" if len(app_token) > 14 else "***"
            print(f"Using app token: {masked_token}")
        
        # Register events we're listening for
        print("Listening for events: app_mention, message")
        print(f"Monitoring channels: {', '.join(MONITORED_CHANNELS)}")
        print(f"Always-respond channels: {', '.join(ALWAYS_RESPOND_CHANNELS)}")
        print("\nThe bot will respond to:")
        print("  - Direct messages")
        print("  - @mentions in any channel")
        print(f"  - Regular messages in monitored channels: {', '.join(MONITORED_CHANNELS)}")
        print("\nResponse behavior:")
        print("  - All channel responses will be in threads")
        print(f"  - In regular monitored channels: only respond when confident")
        print(f"  - In always-respond channels: respond to all messages, even with low confidence")
        
        # Start socket mode handler
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        print("⚡️ GraphQnA Slack Bot is running!")
        handler.start()
    except Exception as e:
        logger.error(f"Error starting Slack bot: {str(e)}")
        print(f"Error starting Slack bot: {str(e)}")
        # Print more detailed exception info
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    start_slack_bot()