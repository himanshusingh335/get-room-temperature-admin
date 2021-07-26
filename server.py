import firebase_admin
import os
import glob
import time
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(
    "/home/pi/dev/python/temp_server/check-my-temp-5e3d6-firebase-adminsdk-m5rzd-e70cd0a740.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = str((float(temp_string) / 1000.0))+" C"
        return temp_c


while True:
    print(read_temp())
    stream = os.popen('hostname -I')
    ipaddr = stream.read()
    print(ipaddr)
    doc_ref = db.collection(u'room1').document(u'stats')
    doc_ref.set({
        u'temp': read_temp(),
        u'ip': ipaddr,
    })
    time.sleep(120)
