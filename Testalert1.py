# --- LOGIN (kalau mau lebih proper, tapi sementara pakai session_id juga boleh)
import requests
import pandas as pd
import sys
import json
import datetime
sys.stdout.reconfigure(encoding='utf-8')

print("Start script...") # --- debug 1

url = "https://metapod.durianpay.tech/api/session"

payload = {
    "username": "octavia.george@durian.money",
    "password": "baksoBeranak2002"
}

login_response = requests.post(url, json=payload, timeout=30)

if login_response.status_code != 200:
    print("Login failed:", login_response.text)
    exit()

session_id = login_response.json()['id']
print("Login success")

headers = {
    "X-Metabase-Session": session_id
}

# --- AMBIL DATA
card_id = 591
url = f"https://metapod.durianpay.tech/api/card/{card_id}/query/json"

# --- kalau error yak
try:
    response = requests.post(url, headers=headers, timeout=60)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        exit()

    data = response.json()
    print("Data received:", len(data))

except Exception as e:
    print("Request failed:", e)
    exit()

# --- OLah DATA
df = pd.DataFrame(data if isinstance(data, list) else [])
print(df.head())

# --- SAVE (optional)
# --- df.to_csv("testpython.csv", index=False)
table_preview = df[['merchant_id', 'total_txn', 'avg_amount']].head(5).to_string(index=False)


print("Sending to Teams...")

# --- KIRIM ALERT KE TEAMS
webhook_url = "https://default2b3d6471ba0741a3a821315f6ef697.d1.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/c12e6be9e35f491b9795ca9332c6b50f/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=IrbseQzd1491I-5qgUhSfPSyilkEyFkpj1WI80h6FSw"
metabase_link = "https://metapod.durianpay.tech/question/591"

rows_preview = data[:10]

if len(df) > 0:
    merchant_list = df['merchant_id'].unique().tolist()
    # message = {
    #     "text": "ALERT TRANSAKSI\n\n"
    #             f"Jumlah transaksi: {len(df)}\n"
    #             f"Jumlah merchant: {len(merchant_list)}\n\n"
    #             "Merchant ID:\n"
    #             f"{merchant_list}\n\n"
    #             "Sample Data:\n"
    #             f"{table_preview}\n\n"
    #             f"Link: {metabase_link}"
    # }
    message = {
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "ALERT TRANSAKSI",
                            "weight": "Bolder"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Jumlah transaksi: {len(df)}"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Jumlah merchant: {len(merchant_list)}"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Link Metapod: {metabase_link}"
                        }
                        # ,
                        # {
                        #     "type": "TextBlock",
                        #     "text": table_preview,
                        #     "wrap": True,
                        #     "fontType": "Monospace"
                        # }
                    ]
                }
            }
        ]
    }
    response_teams = requests.post(webhook_url, json=message, timeout=30)
    print("Teams status:", response_teams.status_code)
    print("Teams response:", response_teams.text)
    
else:
    print("No data, no alert sent.")

print("Payload sent to Teams:")
print(json.dumps(message, indent=2))

print("DONE!")
input("Press Enter to exit...")
with open("log.txt", "a") as f:
    f.write("Script jalan\n")
    f.write(f"Run at {datetime.datetime.now()}\n")