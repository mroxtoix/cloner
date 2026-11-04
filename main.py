import asyncio
import os
import sys
import time
import math
import requests

RESET = "\033[0m"
WHITE = "\033[38;2;255;255;255m"
PURPLE = "\033[38;2;180;60;255m"
GREEN = "\033[38;2;40;255;40m"
RED   = "\033[38;2;255;70;70m"

user_token = ""
source_guild_id = None
target_guild_id = None
headers = {}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_exact_image_gradient(t):
    if t < 0.5:
        factor = t * 2.0
        r = int(60 + (180 - 60) * factor)
        g = int(220 - (220 - 60) * factor)
        b = int(255)
    else:
        factor = (t - 0.5) * 2.0
        r = int(180 + (255 - 180) * factor)
        g = int(60 * (1.0 - factor))
        b = int(255 - (255 - 200) * factor)
    return min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))

def rainbow_text(text, offset=0):
    lines = text.splitlines()
    if not lines:
        return ""
    output = []
    for line_idx, line in enumerate(lines):
        if not line.strip():
            output.append("")
            continue
        colored = "      "
        line_len = len(line)
        for i, char in enumerate(line):
            if char == " ":
                colored += char
                continue
            t = (i + offset) / max(line_len - 1, 1)
            t = t % 1.0
            r, g, b = get_exact_image_gradient(t)
            colored += f"\033[1m\033[38;2;{r};{g};{b}m{char}"
        output.append(colored + RESET)
    return "\n".join(output)

def print_rainbow(text, offset=0):
    print(rainbow_text(text, offset))

def print_action(action, offset=0):
    t = time.strftime('%H:%M:%S')
    msg = f"[{t}] -> {action}"
    print(rainbow_text(msg, offset))

def print_red(text):
    print(RED + text + RESET)

def fetch_discord_api(endpoint, method="GET", payload=None):
    url = f"https://discord.com/api/v9{endpoint}"
    if method == "GET":
        r = requests.get(url, headers=headers)
    elif method == "POST":
        r = requests.post(url, headers=headers, json=payload)
    elif method == "PATCH":
        r = requests.patch(url, headers=headers, json=payload)
    
    if r.status_code in [200, 201, 204]:
        try:
            return r.json()
        except:
            return True
    elif r.status_code == 429:
        retry_after = r.json().get('retry_after', 2)
        time.sleep(retry_after)
        return fetch_discord_api(endpoint, method, payload)
    return None

def authenticate_user():
    global user_token, source_guild_id, target_guild_id, headers
    clear_screen()
    
    offset = 0
    for _ in range(3):
        clear_screen()
        print_rainbow(">>> WAKE UP - SERVER CLONER AUTHENTICATION <<<", offset)
        offset += 1
        time.sleep(0.1)
    
    while True:
        sys.stdout.write(rainbow_text("Enter YOUR Account Token: ", offset) + PURPLE)
        user_token = input().strip()
        sys.stdout.write(RESET)
        if user_token:
            break
        print_red("[Error] Token cannot be empty!")

    headers = {
        "Authorization": user_token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    user_info = fetch_discord_api("/users/@me")
    if not user_info or "id" not in user_info:
        print_red("[Fatal Error] Invalid User Token or account restricted!")
        sys.exit(1)
        
    print_action(f"Logged in successfully as user: {user_info['username']}#{user_info.get('discriminator', '0')}", 0)

    while True:
        sys.stdout.write(rainbow_text("Enter Source Server ID (To Copy From): ", 0) + PURPLE)
        s_id = input().strip()
        sys.stdout.write(RESET)
        if s_id.isdigit():
            source_guild_id = s_id
            break
        print_red("[Error] Invalid ID format!")

    while True:
        sys.stdout.write(rainbow_text("Enter Target Server ID (To Paste To): ", 0) + PURPLE)
        t_id = input().strip()
        sys.stdout.write(RESET)
        if t_id.isdigit():
            target_guild_id = t_id
            break
        print_red("[Error] Invalid ID format!")
    
    time.sleep(1)

def draw_dashboard(source_name, target_name, offset):
    clear_screen()
    
    header_info = "User: @siles  |  Developer: michael  |  discord.gg/UPC2"
    print_rainbow(header_info, offset)
    print()

    ascii_logo = """
██╗    ██╗ █████╗ ██╗  ██╗███████╗    ██╗   ██╗██████╗ 
██║    ██║██╔══██╗██║ ██╔╝██╔════╝    ██║   ██║██╔══██╗
██║ █╗ ██║███████║█████╔╝ █████╗      ██║   ██║██████╔╝
██║███╗██║██╔══██║██╔═██╗ ██╔══╝      ██║   ██║██╔═══╝ 
╚███╔███╔╝██║  ██║██║  ██╗███████╗    ╚██████╔╝██║     
 ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝     ╚═════╝ ╚═╝     
    """
    print_rainbow(ascii_logo, offset)
    
    sub_title = "♪ WAKE UP, Server Cloner Tool ♪"
    print_rainbow(sub_title, offset)
    print()

    boxes = """
┌────────────────────────────────────────────────────────────────────────┐
│                      Welcome to WAKE UP Cloner...                      │
│               Developer: michael  |  Server Cloner Tool                │
├────────────────────────────────────────────────────────────────────────┤
│        [1] Info       - Show source and target server details          │
│        [2] Roles      - Clone all roles (Names, Colors, Positions)     │
│        [3] Channels   - Clone all categories and text/voice channels   │
│        [4] Emojis     - Clone all server emojis directly               │
│        [5] Perms      - Sync role permissions                          │
│        [6] Colors     - Sync exact RGB role colors                     │
│        [all] All      - Execute complete full mirror clone instantly   │
│        [clear] Clear  - Clear screen and return to dashboard           │
│        [0] Exit       - Terminate tool safely                          │
├────────────────────────────────────────────────────────────────────────┤
│                    Type [help] to see all commands                     │
└────────────────────────────────────────────────────────────────────────┘
    """
    print_rainbow(boxes, offset)

def draw_help_screen(offset):
    clear_screen()
    
    header_info = "User: @root  |  Developer: michael  |  discord.gg/rayc2"
    print_rainbow(header_info, offset)
    print()

    ascii_logo = """
██╗    ██╗ █████╗ ██╗  ██╗███████╗    ██╗   ██╗██████╗ 
██║    ██║██╔══██╗██║ ██╔╝██╔════╝    ██║   ██║██╔══██╗
██║ █╗ ██║███████║█████╔╝ █████╗      ██║   ██║██████╔╝
██║███╗██║██╔══██║██╔═██╗ ██╔══╝      ██║   ██║██╔═══╝ 
╚███╔███╔╝██║  ██║██║  ██╗███████╗    ╚██████╔╝██║     
 ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝     ╚═════╝ ╚═╝     
    """
    print_rainbow(ascii_logo, offset)
    
    sub_title = "♪ WAKE UP - Help & Information ♪"
    print_rainbow(sub_title, offset)
    print()

    help_box = """
┌────────────────────────────────────────────────────────────────────────┐
│                   - - - - - ABOUT WAKE UP - - - - -                    │
│           Developer: michael  |  User Token Server Cloner              │
├────────────────────────────────────────────────────────────────────────┤
│  Description:                                                          │
│  WAKE UP is an advanced server cloning tool powered by user tokens.    │
│  It allows you to mirror roles, channels, emojis, and permissions.     │
├────────────────────────────────────────────────────────────────────────┤
│  PLEASE WAIT:                                                          │
│  Please wait patiently during the cloning process. Do not close.       │
└────────────────────────────────────────────────────────────────────────┘
    """
    print_rainbow(help_box, offset)

def clone_roles(offset=0):
    print_action("Starting User-Token role cloning...", offset)
    source_roles = fetch_discord_api(f"/guilds/{source_guild_id}/roles")
    if not source_roles:
        print_red("[-] Failed to fetch source roles. Check server ID or permissions.")
        return {}

    role_mapping = {}
    for role in sorted(source_roles, key=lambda x: x['position']):
        if role['managed'] or role['name'] == "@everyone":
            continue
        
        print_action(f"Creating role: {role['name']}", offset)
        payload = {
            "name": role['name'],
            "permissions": role['permissions'],
            "color": role['color'],
            "hoist": role['hoist'],
            "mentionable": role['mentionable']
        }
        new_role = fetch_discord_api(f"/guilds/{target_guild_id}/roles", method="POST", payload=payload)
        if new_role and 'id' in new_role:
            role_mapping[role['id']] = new_role['id']
        time.sleep(0.4)
        
    print_action("Finished: All roles cloned successfully.", offset)
    return role_mapping

def clone_channels(offset=0):
    print_action("Starting User-Token categories and channels cloning...", offset)
    source_channels = fetch_discord_api(f"/guilds/{source_guild_id}/channels")
    if not source_channels:
        print_red("[-] Failed to fetch source channels.")
        return

    categories = [c for c in source_channels if c['type'] == 4]
    cat_mapping = {}

    for cat in sorted(categories, key=lambda x: x['position']):
        print_action(f"Creating category: {cat['name']}", offset)
        payload = {
            "name": cat['name'],
            "type": 4
        }
        new_cat = fetch_discord_api(f"/guilds/{target_guild_id}/channels", method="POST", payload=payload)
        if new_cat and 'id' in new_cat:
            cat_mapping[cat['id']] = new_cat['id']
        time.sleep(0.4)

    other_channels = [c for c in source_channels if c['type'] != 4]
    for channel in sorted(other_channels, key=lambda x: x['position']):
        print_action(f"Creating channel: {channel['name']}", offset)
        parent_id = cat_mapping.get(channel.get('parent_id'))
        payload = {
            "name": channel['name'],
            "type": channel['type'],
            "topic": channel.get('topic', ''),
            "nsfw": channel.get('nsfw', False),
            "bitrate": channel.get('bitrate', 64000),
            "user_limit": channel.get('user_limit', 0),
            "parent_id": parent_id
        }
        fetch_discord_api(f"/guilds/{target_guild_id}/channels", method="POST", payload=payload)
        time.sleep(0.4)

    print_action("Finished: All channels cloned successfully.", offset)

def clone_emojis(offset=0):
    print_action("Starting User-Token emoji cloning...", offset)
    source_emojis = fetch_discord_api(f"/guilds/{source_guild_id}/emojis")
    if not source_emojis:
        print_red("[-] Failed to fetch source emojis.")
        return

    import base64
    for emoji in source_emojis:
        print_action(f"Cloning emoji: {emoji['name']}", offset)
        try:
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji['id']}.png"
            resp = requests.get(emoji_url)
            if resp.status_code == 200:
                b64_image = f"data:image/png;base64,{base64.b64encode(resp.content).decode('utf-8')}"
                payload = {
                    "name": emoji['name'],
                    "image": b64_image
                }
                fetch_discord_api(f"/guilds/{target_guild_id}/emojis", method="POST", payload=payload)
        except Exception as e:
            print_red(f"[-] Emoji error: {e}")
        time.sleep(0.6)

    print_action("Finished: Emojis cloned successfully.", offset)

def sync_colors(offset=0):
    print_action("Syncing exact RGB role colors...", offset)
    source_roles = fetch_discord_api(f"/guilds/{source_guild_id}/roles")
    target_roles = fetch_discord_api(f"/guilds/{target_guild_id}/roles")
    if not source_roles or not target_roles:
        return

    t_dict = {r['name']: r['id'] for r in target_roles}
    for role in source_roles:
        if role['name'] in t_dict and role['name'] != "@everyone":
            r_id = t_dict[role['name']]
            payload = {"color": role['color']}
            fetch_discord_api(f"/guilds/{target_guild_id}/roles/{r_id}", method="PATCH", payload=payload)
            print_action(f"Synced color for role: {role['name']}", offset)
            time.sleep(0.3)
            
    print_action("Finished: Colors synchronized.", offset)

def run_all(offset=0):
    clear_screen()
    print_rainbow(">>> STARTING FULL USER-TOKEN MIRROR CLONE <<<", offset)
    print_rainbow("--- Please wait while cloning... Server cloning in progress ---", offset)
    clone_roles(offset)
    clone_channels(offset)
    clone_emojis(offset)
    sync_colors(offset)
    print_action("=== FULL SERVER CLONE COMPLETED! ===", offset)
    time.sleep(1.5)

def main():
    authenticate_user()
    
    s_data = fetch_discord_api(f"/guilds/{source_guild_id}")
    t_data = fetch_discord_api(f"/guilds/{target_guild_id}")
    
    s_name = s_data.get('name', 'Source Server') if s_data else 'Source Server'
    t_name = t_data.get('name', 'Target Server') if t_data else 'Target Server'

    offset = 0
    
    import platform
    has_readline = False
    if platform.system() != 'Windows':
        try:
            import readline
            has_readline = True
        except ImportError:
            pass

    commands = ['1', '2', '3', '4', '5', '6', 'all', 'help', 'clear', '0']
    
    if has_readline:
        def completer(text, state):
            matches = [c for c in commands if c.startswith(text)]
            if state < len(matches):
                return matches[state]
            else:
                return None
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

    while True:
        draw_dashboard(s_name, t_name, offset)
        sys.stdout.write(rainbow_text("WAKE-UP> ", offset) + PURPLE)
        choice = input().strip().lower()
        sys.stdout.write(RESET)

        offset += 2

        if not choice:
            continue
        if choice == '0':
            print_rainbow("Exiting tool safely...", offset)
            sys.exit(0)
        elif choice == 'help':
            draw_help_screen(offset)
            sys.stdout.write(rainbow_text("\nPress Enter to return...", offset) + PURPLE)
            input()
            sys.stdout.write(RESET)
        elif choice == 'clear':
            continue
        elif choice == '1':
            clear_screen()
            print_rainbow("=== SERVER DETAILS ===", offset)
            print(PURPLE + f"[*] Source Server: {s_name} (ID: {source_guild_id})")
            print(f"[*] Target Server: {t_name} (ID: {target_guild_id})" + RESET)
            sys.stdout.write(rainbow_text("\nPress Enter to return...", offset) + PURPLE)
            input()
            sys.stdout.write(RESET)
        elif choice == '2':
            clear_screen()
            print_rainbow("--- Please wait, cloning roles in progress ---", offset)
            clone_roles(offset)
            time.sleep(1.5)
        elif choice == '3':
            clear_screen()
            print_rainbow("--- Please wait, cloning channels in progress ---", offset)
            clone_channels(offset)
            time.sleep(1.5)
        elif choice == '4':
            clear_screen()
            print_rainbow("--- Please wait, cloning emojis in progress ---", offset)
            clone_emojis(offset)
            time.sleep(1.5)
        elif choice == '5' or choice == '6':
            clear_screen()
            print_rainbow("--- Please wait, syncing colors and permissions ---", offset)
            sync_colors(offset)
            time.sleep(1.5)
        elif choice == 'all':
            clear_screen()
            run_all(offset)
        else:
            print_red("[Error] Invalid option.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_rainbow("\n[!] Aborted by user.", 0)
        sys.exit(0)