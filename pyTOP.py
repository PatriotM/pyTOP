import os
import re
import argparse
from datetime import datetime

# Configuration: Define groups to search for
CONFIG_GROUPS = ['iND', 'GROUP2', 'GROUP3']  # Add or modify groups here
USER_DIR = "/glftpd/ftp-data/users"  # User files directory

def parse_user_file(filepath):
    """Parse a user file and return a dictionary with relevant stats."""
    user_data = {
        'username': '',
        'groups': [],
        'dayup': {'files': 0, 'bytes': 0, 'time': 0},
        'daydn': {'files': 0, 'bytes': 0, 'time': 0},
        'monthup': {'files': 0, 'bytes': 0, 'time': 0},
        'monthdn': {'files': 0, 'bytes': 0, 'time': 0}
    }
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
            # Get username from filename
            user_data['username'] = os.path.basename(filepath)
            
            # Find GROUP entries
            group_matches = re.findall(r'GROUP\s+(\S+)\s+\d+', content)
            user_data['groups'] = group_matches
            
            # Find DAYUP stats (Files / Bytes / Time)
            dayup_match = re.search(r'DAYUP\s+(\d+)\s+(\d+)\s+(\d+)', content)
            if dayup_match:
                user_data['dayup'] = {
                    'files': int(dayup_match.group(1)),
                    'bytes': int(dayup_match.group(2)),
                    'time': int(dayup_match.group(3))
                }
            
            # Find DAYDN stats (Files / Bytes / Time)
            daydn_match = re.search(r'DAYDN\s+(\d+)\s+(\d+)\s+(\d+)', content)
            if daydn_match:
                user_data['daydn'] = {
                    'files': int(daydn_match.group(1)),
                    'bytes': int(daydn_match.group(2)),
                    'time': int(daydn_match.group(3))
                }
            
            # Find MONTHUP stats (Files / Bytes / Time)
            monthup_match = re.search(r'MONTHUP\s+(\d+)\s+(\d+)\s+(\d+)', content)
            if monthup_match:
                user_data['monthup'] = {
                    'files': int(monthup_match.group(1)),
                    'bytes': int(monthup_match.group(2)),
                    'time': int(monthup_match.group(3))
                }
            
            # Find MONTHDN stats (Files / Bytes / Time)
            monthdn_match = re.search(r'MONTHDN\s+(\d+)\s+(\d+)\s+(\d+)', content)
            if monthdn_match:
                user_data['monthdn'] = {
                    'files': int(monthdn_match.group(1)),
                    'bytes': int(monthdn_match.group(2)),
                    'time': int(monthdn_match.group(3))
                }
                
    except Exception as e:
        print(f"Error parsing {filepath}: {str(e)}")
    
    return user_data

def format_bytes(size):
    """Convert bytes to human-readable format."""
    size = float(size)
    units = ['KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"

def format_time(seconds):
    """Convert seconds to human-readable time format."""
    if seconds < 60:
        return f"{seconds} seconds"
    minutes = seconds // 60
    seconds = seconds % 60
    if minutes < 60:
        return f"{minutes}m {seconds}s"
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours}h {minutes}m {seconds}s"

def print_daily_stats(users):
    """Print daily upload/download statistics for users, sorted by dayup bytes."""
    # Sort users by dayup bytes in descending order
    sorted_users = sorted(users, key=lambda x: x['dayup']['bytes'], reverse=True)
    
    # Calculate average upload for top 5 users
    top_5_bytes = [user['dayup']['bytes'] for user in sorted_users[:5]]
    avg_upload = sum(top_5_bytes) / 5 if top_5_bytes else 0
    
    # Print Daily Upload/Download Stats
    print(f"\nDaily Upload Stats: TOP avg upload {format_bytes(avg_upload)}")
    print("Count. User/Group Size")
    for idx, user in enumerate(sorted_users, 1):
        # Show only the first group, if any
        group_str = f" ({user['groups'][0]})" if user['groups'] else ""
        if user['dayup']['bytes'] == 0 and user['daydn']['bytes'] == 0:
            print(f"{idx}. {user['username']}{group_str} = no uploads/downloads today")
        else:
            up_size = format_bytes(user['dayup']['bytes'])
            dn_size = format_bytes(user['daydn']['bytes'])
            # Calculate ratio (DN/UP)
            ratio = user['daydn']['bytes'] / user['dayup']['bytes'] if user['dayup']['bytes'] != 0 else "N/A"
            # Format ratio to 2 decimal places if it's a number
            ratio_display = f"{ratio:.2f}" if isinstance(ratio, (int, float)) else ratio
            # Color only UP [size] and DN [size] based on UP > DN
            color_code = "\033[32m" if user['dayup']['bytes'] > user['daydn']['bytes'] else "\033[31m"
            reset_code = "\033[0m"
            print(f"{idx}. {user['username']}{group_str} {color_code}UP {up_size}{reset_code} / {color_code}DN {dn_size}{reset_code} (Ratio: {ratio_display})")

def print_monthly_stats(users):
    """Print monthly upload/download statistics for users, sorted by monthup bytes and monthdn bytes."""
    # Sort users by monthup bytes (descending), then by monthdn bytes (descending) for users with no uploads
    sorted_users = sorted(users, key=lambda x: (x['monthup']['bytes'], x['monthdn']['bytes'] if x['monthup']['bytes'] == 0 else 0), reverse=True)
    
    # Calculate average upload for top 5 users
    top_5_bytes = [user['monthup']['bytes'] for user in sorted_users[:5]]
    avg_upload = sum(top_5_bytes) / 5 if top_5_bytes else 0
    
    # Print Monthly Upload/Download Stats
    print(f"\nMonthly Upload Stats: TOP avg upload {format_bytes(avg_upload)}")
    print("Count. User/Group Size")
    for idx, user in enumerate(sorted_users, 1):
        # Show only the first group, if any
        group_str = f" ({user['groups'][0]})" if user['groups'] else ""
        if user['monthup']['bytes'] == 0 and user['monthdn']['bytes'] == 0:
            print(f"{idx}. {user['username']}{group_str} = no uploads/downloads this month")
        else:
            up_size = format_bytes(user['monthup']['bytes'])
            dn_size = format_bytes(user['monthdn']['bytes'])
            # Calculate ratio (DN/UP)
            ratio = user['monthdn']['bytes'] / user['monthup']['bytes'] if user['monthup']['bytes'] != 0 else "N/A"
            # Format ratio to 2 decimal places if it's a number
            ratio_display = f"{ratio:.2f}" if isinstance(ratio, (int, float)) else ratio
            # Color only UP [size] and DN [size] based on UP > DN
            color_code = "\033[32m" if user['monthup']['bytes'] > user['monthdn']['bytes'] else "\033[31m"
            reset_code = "\033[0m"
            print(f"{idx}. {user['username']}{group_str} {color_code}UP {up_size}{reset_code} / {color_code}DN {dn_size}{reset_code} (Ratio: {ratio_display})")

def main():
    """Main function to process user files and display stats based on command-line arguments."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Display user upload/download statistics")
    parser.add_argument('--day', action='store_true', help="Show daily upload/download stats")
    parser.add_argument('--month', action='store_true', help="Show monthly upload/download stats")
    args = parser.parse_args()
    
    if not (args.day or args.month):
        print("Error: Please specify either --day or --month")
        return
    
    if args.day and args.month:
        print("Error: Please specify only one of --day or --month")
        return
    
    ind_users = []
    
    # Check if directory exists
    if not os.path.exists(USER_DIR):
        print(f"Error: Directory {USER_DIR} does not exist")
        return
    
    # Process each file in the user directory
    for filename in os.listdir(USER_DIR):
        filepath = os.path.join(USER_DIR, filename)
        if os.path.isfile(filepath):
            user_data = parse_user_file(filepath)
            # Check if user in any of the configured groups
            if any(group in user_data['groups'] for group in CONFIG_GROUPS):
                ind_users.append(user_data)
    
    # Print results
    if not ind_users:
        print(f"No users found in groups: {', '.join(CONFIG_GROUPS)}")
        return
    
    print(f"\nFound {len(ind_users)} users in groups: {', '.join(CONFIG_GROUPS)}")
    print("=" * 50)
    
    if args.day:
        print_daily_stats(ind_users)
    elif args.month:
        print_monthly_stats(ind_users)

if __name__ == "__main__":
    main()
