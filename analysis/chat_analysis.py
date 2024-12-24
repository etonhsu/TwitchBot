import json
from collections import Counter

def load_chat_logs(file_path):
    """
    Load chat logs from a JSON file.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def analyze_chat_logs(chat_log_data):
    """
    Analyze chat logs to determine chats per user and total unique chatters per period and overall.
    """
    overall_user_chats = Counter()
    period_user_counts = []
    total_chatters = set()

    # Process each 10-minute period
    for period in chat_log_data:
        period_chat_counts = Counter()
        period_chatters = set()

        # Count chats per user in this period
        for chat in period['chat_logs']:
            username = chat['username']
            period_chat_counts[username] += 1
            period_chatters.add(username)
            overall_user_chats[username] += 1
            total_chatters.add(username)

        # Append period data
        sorted_period_chat_counts = dict(sorted(period_chat_counts.items(), key=lambda x: x[1], reverse=True))
        period_user_counts.append({
            "start_time": period['start_time'],
            "end_time": period['end_time'],
            "unique_chatters": len(period_chatters),
            "chats_per_user": sorted_period_chat_counts  # Sorted by message count
        })

    # Summarize overall data
    sorted_overall_user_chats = dict(sorted(overall_user_chats.items(), key=lambda x: x[1], reverse=True))
    overall_summary = {
        "total_unique_chatters": len(total_chatters),
        "total_chats_per_user": sorted_overall_user_chats  # Sorted by message count
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
    input_file = "../dishsoap_chat_log.json"  # Replace with your actual file path
    output_file = "chat_log_analysis.json"

    # Load, analyze, and save chat log analysis
    chat_logs = load_chat_logs(input_file)
    period_data, overall_summary = analyze_chat_logs(chat_logs)
    save_analysis_results(output_file, period_data, overall_summary)
