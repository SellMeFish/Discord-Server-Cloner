import tkinter as tk
from tkinter import ttk, messagebox
import requests
import base64
import json
import time
import threading
from io import BytesIO

class DiscordCloner:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Discord Server Cloner")
        self.window.geometry("700x500")
        
        self.token = ""
        self.headers = {}
        self.base_url = "https://discord.com/api/v9"
        
        self.create_widgets()
        
    def create_widgets(self):
        tk.Label(self.window, text="User Token:", font=("Arial", 10)).pack(pady=5)
        self.token_entry = tk.Entry(self.window, width=80, font=("Arial", 10))
        self.token_entry.pack()

        tk.Label(self.window, text="Source Server ID:", font=("Arial", 10)).pack(pady=5)
        self.source_id_entry = tk.Entry(self.window, font=("Arial", 10))
        self.source_id_entry.pack()

        tk.Label(self.window, text="Target Server ID:", font=("Arial", 10)).pack(pady=5)
        self.target_id_entry = tk.Entry(self.window, font=("Arial", 10))
        self.target_id_entry.pack()

        self.clone_btn = ttk.Button(self.window, text="Clone Server", command=self.start_clone)
        self.clone_btn.pack(pady=10)

        self.log = tk.Text(self.window, height=18, width=85, font=("Consolas", 9))
        self.log.pack()

    def update_headers(self):
        self.token = self.token_entry.get().strip()
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def log_message(self, message):
        self.log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log.see(tk.END)
        self.window.update_idletasks()

    def start_clone(self):
        self.update_headers()
        threading.Thread(target=self.full_clone_process, daemon=True).start()

    def full_clone_process(self):
        try:
            user_req = requests.get(f"{self.base_url}/users/@me", headers=self.headers)
            if user_req.status_code != 200:
                self.log_message("❌ Invalid token!")
                return

            source_id = self.source_id_entry.get().strip()
            target_id = self.target_id_entry.get().strip()

            source_guild = self.get_guild(source_id)
            target_guild = self.get_guild(target_id)
            if not source_guild or not target_guild:
                return

            self.log_message("🚀 Starting cloning process...")

            self.clear_target_server(target_id)

            self.clone_server_settings(source_guild, target_id)
            
            roles_mapping = self.clone_roles(source_id, target_id)
            
            self.clone_all_channels(source_id, target_id, roles_mapping)
            
            self.clone_emojis(source_id, target_id)

            self.log_message("✅ Cloning completed successfully!")

        except Exception as e:
            self.log_message(f"💥 Critical error: {str(e)}")

    def api_request(self, method, url, **kwargs):
        for _ in range(3):
            response = requests.request(method, url, **kwargs)
            if response.status_code == 429:
                retry_after = response.json().get('retry_after', 5)
                self.log_message(f"⏳ Rate limited. Retrying in {retry_after}s...")
                time.sleep(retry_after)
                continue
            return response
        return response

    def get_guild(self, guild_id):
        req = self.api_request("GET", f"{self.base_url}/guilds/{guild_id}", headers=self.headers)
        if req.status_code != 200:
            self.log_message(f"❌ Server {guild_id} not found!")
            return None
        return req.json()

    def clear_target_server(self, target_id):
        self.log_message("🧹 Clearing target server...")
        
        channels = self.api_request("GET", f"{self.base_url}/guilds/{target_id}/channels", headers=self.headers).json()
        for channel in channels:
            self.api_request("DELETE", f"{self.base_url}/channels/{channel['id']}", headers=self.headers)
            self.log_message(f"🗑️ Deleted channel: {channel['name']}")
            time.sleep(0.7)

        roles = self.api_request("GET", f"{self.base_url}/guilds/{target_id}/roles", headers=self.headers).json()
        for role in roles:
            if role['name'] != '@everyone':
                self.api_request("DELETE", f"{self.base_url}/guilds/{target_id}/roles/{role['id']}", headers=self.headers)
                self.log_message(f"🗑️ Deleted role: {role['name']}")
                time.sleep(0.7)

        emojis = self.api_request("GET", f"{self.base_url}/guilds/{target_id}/emojis", headers=self.headers).json()
        for emoji in emojis:
            self.api_request("DELETE", f"{self.base_url}/guilds/{target_id}/emojis/{emoji['id']}", headers=self.headers)
            self.log_message(f"🗑️ Deleted emoji: {emoji['name']}")
            time.sleep(0.7)

    def clone_server_settings(self, source_guild, target_id):
        self.log_message("⚙️ Cloning server settings...")
        payload = {
            "name": source_guild['name'],
            "description": source_guild.get('description', ''),
            "verification_level": source_guild['verification_level'],
            "afk_timeout": source_guild['afk_timeout']
        }

        if source_guild.get('icon'):
            icon_url = f"https://cdn.discordapp.com/icons/{source_guild['id']}/{source_guild['icon']}.png?size=4096"
            icon_data = requests.get(icon_url).content
            payload["icon"] = f"data:image/png;base64,{base64.b64encode(icon_data).decode('utf-8')}"
            self.log_message("🖼️ Copied server icon")

        self.api_request("PATCH", 
                        f"{self.base_url}/guilds/{target_id}", 
                        headers=self.headers, 
                        json=payload)
        time.sleep(1)

    def clone_roles(self, source_id, target_id):
        self.log_message("🎭 Cloning roles...")
        roles = self.api_request("GET", f"{self.base_url}/guilds/{source_id}/roles", headers=self.headers).json()
        roles_mapping = {}
        
        for role in reversed(roles):
            if role['name'] == '@everyone':
                payload = {
                    "permissions": role['permissions'],
                    "color": role['color'],
                    "hoist": role['hoist'],
                    "mentionable": role['mentionable']
                }
                self.api_request("PATCH",
                                f"{self.base_url}/guilds/{target_id}/roles/{target_id}",  # @everyone ID = guild ID
                                headers=self.headers,
                                json=payload)
                roles_mapping[role['id']] = target_id
                continue
                
            payload = {
                "name": role['name'],
                "permissions": role['permissions'],
                "color": role['color'],
                "hoist": role['hoist'],
                "mentionable": role['mentionable']
            }
            
            new_role = self.api_request("POST",
                                       f"{self.base_url}/guilds/{target_id}/roles",
                                       headers=self.headers,
                                       json=payload).json()
            roles_mapping[role['id']] = new_role['id']
            self.log_message(f"🎭 Created role: {role['name']}")
            time.sleep(0.7)
            
        return roles_mapping

    def clone_all_channels(self, source_id, target_id, roles_mapping):
        self.log_message("📁 Cloning channels...")
        channels = self.api_request("GET", f"{self.base_url}/guilds/{source_id}/channels", headers=self.headers).json()
        category_mapping = {}
        
        for channel in channels:
            if channel['type'] == 4:
                payload = self.create_channel_payload(channel, roles_mapping)
                new_category = self.api_request("POST",
                                               f"{self.base_url}/guilds/{target_id}/channels",
                                               headers=self.headers,
                                               json=payload).json()
                category_mapping[channel['id']] = new_category['id']
                self.log_message(f"📂 Created category: {channel['name']}")
                time.sleep(0.7)

        for channel in channels:
            if channel['type'] != 4:
                payload = self.create_channel_payload(channel, roles_mapping)
                if channel.get('parent_id'):
                    payload['parent_id'] = category_mapping.get(channel['parent_id'])
                    
                new_channel = self.api_request("POST",
                                              f"{self.base_url}/guilds/{target_id}/channels",
                                              headers=self.headers,
                                              json=payload).json()
                self.log_message(f"📄 Created channel: {channel['name']}")
                time.sleep(0.7)

    def create_channel_payload(self, channel, roles_mapping):
        payload = {
            "name": channel['name'],
            "type": channel['type'],
            "position": channel['position'],
            "topic": channel.get('topic', ''),
            "nsfw": channel.get('nsfw', False),
            "rate_limit_per_user": channel.get('rate_limit_per_user', 0),
            "bitrate": channel.get('bitrate', 64000),
            "user_limit": channel.get('user_limit', 0),
            "permission_overwrites": []
        }
        
        for overwrite in channel['permission_overwrites']:
            new_id = roles_mapping.get(overwrite['id'], overwrite['id'])
            payload['permission_overwrites'].append({
                "id": new_id,
                "type": overwrite['type'],
                "allow": str(overwrite['allow']),
                "deny": str(overwrite['deny'])
            })
            
        return payload

    def clone_emojis(self, source_id, target_id):
        self.log_message("🎨 Cloning emojis...")
        emojis = self.api_request("GET", f"{self.base_url}/guilds/{source_id}/emojis", headers=self.headers).json()
        
        for emoji in emojis:
            try:
                extension = "gif" if emoji['animated'] else "png"
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji['id']}.{extension}?quality=lossless"
                emoji_data = requests.get(emoji_url).content
                
                payload = {
                    "name": emoji['name'],
                    "image": f"data:image/{extension};base64,{base64.b64encode(emoji_data).decode('utf-8')}"
                }
                
                self.api_request("POST",
                                f"{self.base_url}/guilds/{target_id}/emojis",
                                headers=self.headers,
                                json=payload)
                self.log_message(f"🎨 Created emoji: {emoji['name']}")
                time.sleep(1)
                
            except Exception as e:
                self.log_message(f"⚠️ Failed to clone emoji {emoji['name']}: {str(e)}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    cloner = DiscordCloner()
    cloner.run()