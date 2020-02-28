#!/usr/bin/python3

import base64
import os
import requests
from Crypto.Cipher import AES
import hashlib
import time
import json
import threading
from colored import fg, bg, attr



debug = False
outputData = ""

url = ""

class sendChatMessagesThread (threading.Thread):
    #vlákno pre posielanie správ
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while True:
            #chcem docieliť toho a by sa po tom ako užívateľ zadá input, pred inputom ešte niečo napísalo,
            #alebo zmazať to čo napísal, a potom vypísať input
            color = fg('blue')
            print(color + "\n",nickname,": ", end='')
            chatMessageContent = input("")
          
            customPrint(color + nickname + ": " + chatMessageContent + "\n")
            chatMessage = encrypt(chatMessageContent, encryptionKey_Hashed)
            chatMessage = base64.b64encode(chatMessage)
            requestData["chatMessageContent"] = chatMessage
            requestData["command"] = "sendChatMessage"
            requests.post(url, data=requestData)
            if debug == True:
                customPrint("[Debug] post request response:" + responseData + "\n")

class receiveChatMessageThread (threading.Thread):
    #vlákno pre príjimanie správ

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while True:
            requestData["command"] = "getChatRoomPeopleCount"
            response = requests.post(url, data=requestData)
            if debug == True:
                customPrint("[Debug] post request response:" + response.text + "\n")
        
            responseData = json.loads(response.text)
            chatRoomPeopleCount = responseData["chatRoomPeopleCount"]
            if(chatRoomPeopleCount > 1):
                customPrint("[i] Počet osôb v miestnosti:" + str(chatRoomPeopleCount) + "\n")

                while True:
                    responseData
                    requestData["command"] = "receiveChatMessage"
                    response = requests.post(url, data=requestData)  
                    responseData = response.text
                    if debug == True:
                        customPrint("[Debug] post request response:" + responseData + "\n")
                    #print(responseData)
                    if(len(responseData) > 0):
                        responseData = json.loads(response.text)
                        if(responseData["status"] == "success"):
                            senderNickname = responseData["senderNickname"]
                            encryptedReceivedBase64Message = responseData["receivedChatMessage"].encode("utf-8")
                            encryptedReceivedMessage = base64.b64decode(encryptedReceivedBase64Message)  
                            color = fg('red')
                            decryptedMessage = decrypt(encryptedReceivedMessage, encryptionKey_Hashed)
                            customPrint(color + senderNickname + ": " + decryptedMessage[0:decryptedMessage.find("{")] + "\n")
                            responseData = None
                    time.sleep(1)
                else:
                    customPrint("[*] Počet osôb v miestnosti:" + str(chatRoomPeopleCount) + "\n")
                    customPrint("[*] Dalšia kontrola prebehne o 10 sekúnd \n")
            time.sleep(10)

def customPrint(data):
    global outputData
    outputData += data
    os.system("clear")
    print(outputData)


def skontrolujVelkostDat(bytesToProcess):
    result = bytesToProcess
    if len(bytesToProcess) % 16 != 0:
        newString = ""
        newString += bytesToProcess.decode()
        # musím skontrolovať či je potrebné nejaký bytey pridať, či veľkosť stringu nieje práve taká aká má byť
        numberOfBytesToAdd = (16 - len(bytesToProcess) % 16)
        singlePaddingCharacter = chr(0)
        paddingString = numberOfBytesToAdd * singlePaddingCharacter
        newString += paddingString
        result = newString.encode()
        if(debug == True):
            print("[debug][def addPadding] bol pridaný padding:",
                  numberOfBytesToAdd)
    return result
 

def encrypt(data, key):
    #funkcia pre zašifrovanie obsahu správy.
    #používa sa 256bit AES, ECB mód. ECB mimochodom nieje doporučené používať, pre spôsob akým sa bloky dát šifrujú. S
    #kedže sa tu používa AES-ECB, individuálne bloky dát musia 16 bajtov. tu sa kontroluje či je veľkosť dát ktoré sa majú v bajtoch odoslať deliteľná 16-timi. Ak nie, bajty sa do správy ktorá sa má zašifrovať umelo pridajú.
 data = data.encode("utf-8")
 data = skontrolujVelkostDat(data)

 cipher = AES.new(key, AES.MODE_ECB)
 encryptedData = cipher.encrypt(data)
 return encryptedData



def decrypt(data, key):
 #tu by dáta už mali mať správnu dĺžku. Nebude sa upravovať
 cipher = AES.new(key, AES.MODE_ECB)
 decryptedData = cipher.decrypt(data)
 decryptedData = decryptedData.decode()
 return decryptedData

colorss = fg('white')

customPrint(colorss + "Jednoduchý chat \n")
printDebug = input("[*] použiť debug mód? a/n (áno/nie) ")
customPrint("[*] použiť debug mód? a/n (áno/nie) "+ printDebug +"\n")
if printDebug == "a" or printDebug == "A":
    debug == True
    print("[i] používa sa debug mód")
    customPrint("[i] používa sa debug mód \n")
else:
    debug == False
url = input("[*] URL (napríklad http://localhost/ ")
customPrint("[*] URL (napríklad http://localhost/ " + url + "\n")
nickname = input("[*] nick: ")
customPrint("[*] nick: " + nickname + "\n")
chatRoomName = input("[*] názov miestnosti pre chatovanie: ")
customPrint("[*] názov miestnosti pre chatovanie: " + chatRoomName + "\n")
encryptionKey = input("[*] kľúč pre šifrovanie: ")
customPrint("[*] kľúč pre šifrovanie: " + encryptionKey + "\n")
encryptionKey_Hashed = hashlib.sha256(encryptionKey.encode("utf-8"))
encryptionKey_Hashed = encryptionKey_Hashed.digest()
requestData = {
    "nickname": nickname,
    "chatRoomName" : chatRoomName,
    "command" : "initChatSession"
}
responseData = requests.post(url, data=requestData)
parsedResponseData = json.loads(responseData.text)
if parsedResponseData["status"] == "success":
    customPrint("[i] miestnosť vytvorená \n")

    requestData["command"] = "createChatEntryInsideChatRoom"
    response = requests.post(url, data=requestData)
    responseData = response.text
    if debug == True:
        customPrint("[Debug] post request response: " + responseData + "\n")
    parsedResponseData = json.loads(responseData)
    if parsedResponseData["status"] == "success":
        customPrint("[i] vstup v miestnosti bol vytvorený \n")

        # Create new threads
        thread1 = sendChatMessagesThread(1, "Thread-1", 1)
        thread2 = receiveChatMessageThread(2, "Thread-2", 2)

        # Start new Threads
        thread1.start()
        thread2.start()
    else:
        customPrint("[!] vytvorenie vstupu v miestnosti zlyhalo \n")

else:
    customPrint("[!] vytvorenie miestnosti zlyhalo \n")