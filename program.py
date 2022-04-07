import requests
import random
import time
import re
import os


def login():
  url = "https://www.joyclub.de/login/"
  source = s.get(url, headers = headers).text
  cacheKiller = re.search('name="cache_killer"\svalue="(.*?)"', source)

  if cacheKiller:
    data = {
      "user_locale": "en_GB",
      "cache_killer": cacheKiller[1],
      "user_name": user,
      "user_pass": passw,
      "user_keep_logged_in": "1"
    }

    s.post(url, headers = headers, data = data)

def sendMessage(url, recipientId, lastMessageId, nameUser, message):
  urlMessage = "https://www.joyclub.de/clubmailv3/send_personal_message"

  source = s.get(url, headers = headers).text
  cacheKiller = re.search('name="cache_killer"\svalue="(.*?)"', source)

  if cacheKiller:
    field = '{"content":"' + str(message)
    field += '","attached_upload_id":null, "attached_gallery_id":null, '
    field += '"template_id":null, "template_shortname":null, '
    field += '"related_template_topic_id":null, "special":null, '
    field += '"recipient_id":' + str(recipientId) + ', "email_cc":false, '
    field += '"is_system_message":false, "last_message_id":"' + str(lastMessageId)
    field += '", "shared_location":null, "video_call":null, "zendesk_support":null}'

    data = {"cache_killer": str(cacheKiller[1]), "data": field}

    source = s.post(urlMessage, headers = headers, data = data)

    if source.status_code == 200:
      print("Message sent to", nameUser)
    else:
      print("Error sending message")

def getListContacts():
  urlUser = []
  nameUser = []
  recipientId = []
  lastMessageId = []
  urlContact = "https://www.joyclub.de/clubmailv3/#/conversation/"
  urlClubmail = "https://www.joyclub.de/clubmailv3/"

  source = s.get(urlClubmail, headers = headers).text
  cacheKiller = re.search('name="cache_killer"\svalue="(.*?)"', source)

  if cacheKiller:
    urlN = urlClubmail + "get_conversation_list"
    num = 1000

    while True:
      field = '{"archive":false,"conversation_type":null,"limit":' + str(num)
      field += ', "last_conversation_unread":true, "last_conversation_id":"", '
      field += '"sort_time":0, "sort_chronologically":true}'

      data = {"cache_killer": str(cacheKiller[1]), "data": field}

      source = s.post(urlN, headers = headers, data = data)

      if source.status_code == 200:
        _json =  source.json()
        if _json["content"]["page_down_parameter"] is not None:
          num += 1000
        else:
          break
      else:
        print("Error")
        time.sleep(60)

    for j in _json["content"]["conversation_list"]:
      if j["conversation_partner_name"] is not None:
        lastMessageId.append(j["last_message_id"])
        recipientId.append(j["conversation_partner_id"])
        urlUser.append(urlContact + j["conversation_id"])
        nameUser.append(j["conversation_partner_name"])

  return urlUser, nameUser, recipientId, lastMessageId

def start():
  fr = []

  login()

  print("Login ok")

  while True:

    urlUser, nameUser, recipientId, lastMessageId = getListContacts()

    if not os.path.exists("contacts.txt"):
      f = open("contacts.txt", "w")
      f.close()
    else:
      fr = []
      f = open("contacts.txt", "r")
      lines = f.read().splitlines()
      for line in lines:
        if line.strip() != "":
          fr.append(line)
      f.close()

    for i in range(len(urlUser)):
      if nameUser[i] not in fr:
        message = random.choice(messages)
        sendMessage(urlUser[i], recipientId[i], lastMessageId[i], nameUser[i], message)
        f = open("contacts.txt", "a")
        f.write(nameUser[i] + "\n")
        f.close()
        time.sleep(60)

    time.sleep(15)


if __name__ == '__main__':
  messages = []
  user = ""
  passw = ""

  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
  }

  f = open("message.txt", "r")
  lines = f.read().splitlines()
  for line in lines:
    if line.strip() != "":
      messages.append(line)
  f.close()

  f = open("login.txt", "r")
  lines = f.read().splitlines()
  user = lines[0].replace("user:", "").strip()
  passw = lines[1].replace("password:", "").strip()
  f.close()

  s = requests.Session()

  start()
