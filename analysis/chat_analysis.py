import json
from collections import Counter

def load_chat_logs(file_path):
    """
    Load chat logs from a JSON file.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def extended_analyze_chat_logs(chat_log_data):
    """
    Analyze chat logs for various statistics including:
    - Most active chatters per period and overall.
    - Percentage of chatters who are subscribers.
    - Percentage of subscribers who are 6+ month subscribers.
    - Percentage of subscribers who are sub-gifters.
    - Subscribers gained per period and overall.
    """
    overall_user_chats = Counter()
    period_user_counts = []
    total_chatters = set()

    total_messages = 0
    total_subscribers = 0
    six_plus_month_subscribers = 0
    sub_gifters = 0
    total_new_subs = 0

    # Process each 10-minute period
    for period in chat_log_data:
        period_chat_counts = Counter()
        period_chatters = set()
        period_subscribers = 0
        period_new_subs = 0

        # Track mystery gift and subgift counts
        mystery_gifters = {}

        # Count chats per user in this period and analyze badges
        for chat in period['chat_logs']:
            username = chat['username']
            designations = chat['designations']

            period_chat_counts[username] += 1
            period_chatters.add(username)
            overall_user_chats[username] += 1
            total_chatters.add(username)
            total_messages += 1

            # Check for subscription status
            if "subscriber" in designations:
                total_subscribers += 1
                period_subscribers += 1
                # Check for 6+ month subscribers
                sub_duration = int(designations.split("/")[1].split(",")[0]) if "/" in designations else 0
                if sub_duration >= 6:
                    six_plus_month_subscribers += 1
                # Check for sub-gifter status
                if "sub-gifter" in designations:
                    sub_gifters += 1

        # Calculate new subscribers for this period
        for event in period.get("special_events", []):
            event_type = event.get("event_type", "")
            username = event.get("username", "")

            if event_type == "submysterygift":
                # Add mystery gift count
                gift_count = int(event.get("gift_count", 0))
                mystery_gifters[username] = mystery_gifters.get(username, 0) + gift_count
                period_new_subs += gift_count

            elif event_type == "subgift":
                # Count subgifts if not part of a mystery gift
                recipient = event.get("recipient", "")
                if username not in mystery_gifters or mystery_gifters[username] <= 0:
                    period_new_subs += 1
                elif mystery_gifters[username] > 0:
                    # Reduce mystery gift count if it applies to this subgift
                    mystery_gifters[username] -= 1

            elif event_type == "resub":
                # Resubscriptions count as new subs
                period_new_subs += 1

        total_new_subs += period_new_subs

        # Append period data
        sorted_period_chat_counts = dict(sorted(period_chat_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        period_user_counts.append({
            "start_time": period['start_time'],
            "end_time": period['end_time'],
            "unique_chatters": len(period_chatters),
            "chats_per_user": sorted_period_chat_counts,  # Sorted by message count
            "subscribers": period_subscribers,
            "new_subscribers": period_new_subs
        })

    # Summarize overall data
    sorted_overall_user_chats = dict(sorted(overall_user_chats.items(), key=lambda x: x[1], reverse=True)[:10])
    overall_summary = {
        "total_unique_chatters": len(total_chatters),
        "total_chats_per_user": sorted_overall_user_chats,  # Sorted by message count
        "total_messages": total_messages,
        "subscriber_percentage": total_subscribers / total_messages * 100 if total_messages else 0,
        "six_plus_month_subscriber_percentage": six_plus_month_subscribers / total_subscribers * 100 if total_subscribers else 0,
        "sub_gifter_percentage": sub_gifters / total_subscribers * 100 if total_subscribers else 0,
        "total_new_subscribers": total_new_subs
    }

    return period_user_counts, overall_summary

def save_analysis_results(output_path, period_data, overall_summary):
    """
    Save analysis results to a JSON file.
    """
    result = {
        "period_data": period_data,
        "overall_summary": overall_summary
    }
    with open(output_path, 'w') as file:
        json.dump(result, file, indent=4)
    print(f"Analysis saved to {output_path}")

if __name__ == "__main__":
    # Input and output file paths
    input_file = "../noraexplorer_chat_log.json"  # Replace with your actual file path
    output_file = "chat_log_analysis.json"

    # Load, analyze, and save chat log analysis
    chat_logs = load_chat_logs(input_file)
    period_data, overall_summary = extended_analyze_chat_logs(chat_logs)
    save_analysis_results(output_file, period_data, overall_summary)
