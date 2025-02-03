# 🚀 Discord Server Cloner

## 📜 Description
The **Discord Server Cloner** is a powerful tool that allows you to replicate an entire Discord server structure, including roles, channels, categories, and emojis. This tool uses the Discord API to fetch details from a source server and applies them to a target server, making migration and backup easier.

---

## ⚡ Features
- 🏗 **Clone Server Structure** – Copies all categories, channels, and roles from the source server to the target server.
- 🎭 **Role Cloning** – Preserves role names, permissions, and settings.
- 📂 **Channel Cloning** – Duplicates both text and voice channels along with permissions.
- 🎨 **Emoji Cloning** – Transfers emojis from the source server.
- 🖼 **Server Icon Copy** – Downloads and applies the source server's icon.
- 🔄 **Automatic Rate Limit Handling** – Waits and retries API calls when necessary.
- 💡 **Tkinter GUI** – Provides an easy-to-use interface for entering token and server IDs.

---

## 🔧 Installation
### Prerequisites
- Python 3.8+
- `pip install requests tkinter`

### Running the Program
1. Clone the repository or download the script:
   ```sh
   git clone https://github.com/yourusername/discord-server-cloner.git
   cd discord-server-cloner
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the script:
   ```sh
   python Servercloner.py
   ```

---

## 🛠 How to Use
1. **Enter your Discord User Token** (You must have administrator rights on both servers).
2. **Provide the Source Server ID** (The server you want to clone).
3. **Provide the Target Server ID** (The server where the clone should be applied).
4. Click **"Clone Server"** and wait for the process to complete.

> 🛑 **Disclaimer:** The usage of Discord user tokens is against Discord's Terms of Service. This tool is for educational purposes only.

---

## 🔍 Troubleshooting
- ❌ **Invalid Token Error** – Ensure you have entered a valid Discord user token.
- 🚫 **Permissions Error** – Verify you have admin permissions on both servers.
- ⏳ **Rate Limiting** – The program automatically waits and retries requests if Discord enforces rate limits.

---

## 📜 License
This project is open-source and for educational purposes only. Any misuse of this tool is the responsibility of the user.

---

## 🤝 Contributing
Contributions are welcome! Feel free to submit a pull request or report issues.

---

## 📞 Support
For any questions or support, please contact `your_email@example.com`.

