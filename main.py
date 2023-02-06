import request
import net
import cellLocator
import modem
import utime
import quecgnss
import ure
from misc import Power
from misc import ADC
from machine import RTC
from machine import Timer
from machine import ExtInt
from machine import Pin
from usr.led import LED
from usr.buzzer import Buzzer
from machine import I2C
from usr.LIS2DH12 import Lis2dh12

# server response:  vibre command: ,2,1,60,0,0,0*
#                   LED command:   ,2,0,60,0,1,0*
#                   Off command:   ,2,0,60,0,0,1*
#                   FOTA command:  ,2,0,60,1,0,0*    
# from machine import UART
TouchLED = LED(Pin.GPIO18, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
B3_LED   = LED(Pin.GPIO3, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
B2_LED   = LED(Pin.GPIO4, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
B1_LED   = LED(Pin.GPIO2, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
B0_LED   = LED(Pin.GPIO1, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
Band_LED = LED(Pin.GPIO19, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
Charger_LED = LED(Pin.GPIO9, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0) 
IR_Tx = LED(Pin.GPIO46, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0) 
Vibre = Buzzer(Pin.GPIO23, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
adc=ADC()
adc.open()
i2c_dev = I2C(I2C.I2C0, I2C.STANDARD_MODE)
accel_int_pin = Pin(Pin.GPIO25, Pin.IN, Pin.PULL_PU, 0)
accel_dev = Lis2dh12(i2c_dev,accel_int_pin)
# accel_dev.int_enable(MOVE_RECOGNIZE,0x02)
accel_dev.start_sensor()

SOS=0
Charger=0
# Band=0; 
BandTamper=0
BandTamperSent=1
doorTamper=0
doorTamperSent=1
Temperature=0
Accel=0
vbat=0

def touchFunc(args):
    global SOS
    TouchLED.start_flicker(1000,1000,2)
    if (args[1]==0):
        # print("Touch Args[1] = 0 ")
        SOS = 1;
    if (args[1]==0):
        if (vbat > 90):
            B3_LED.on()
        else:
            B3_LED.off()
        if (vbat > 75):
            B2_LED.on()
        else:
            B2_LED.off()
        if (vbat > 50):
            B1_LED.on()
        else:
            B1_LED.off()
        if (vbat > 25):
            B0_LED.on()
        else:
            B0_LED.start_flicker(1000, 10000, 2)
    if (args[1]==1):
        B3_LED.off()
        B2_LED.off()
        B1_LED.off()
        B0_LED.off()

def chargeFunc(args):
        global Charger
        global vbat
        if (args[1]==1):
            Charger_LED.on();
            Charger = 1;
        if (args[1]==0):
            Charger_LED.off();
            Charger = 0;
        if (Charger==1):
            if (vbat > 90):
                B3_LED.on()
            else:
                B3_LED.off()
            if (vbat > 75):
                B2_LED.on()
            else:
                B2_LED.off()
            if (vbat > 50):
                B1_LED.on()
            else:
                B1_LED.off()
            if (vbat > 25):
                B0_LED.on()
            else:
                B0_LED.start_flicker(1000, 10000, 2)
                Vibre.start_flicker(500,1000,3)
                
        else:
            B3_LED.off()
            B2_LED.off()
            B1_LED.off()
            B0_LED.off()
            



Touch_extInt = ExtInt(ExtInt.GPIO14, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_DISABLE, touchFunc)
Touch_extInt.enable()
Charger_extInt = ExtInt(ExtInt.GPIO22, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, chargeFunc)
Charger_extInt.enable()

# uart = UART(UART.UART2,9600,8,0,1,0)
url = "http://psimap.ir/api/signals/ws6/"
quecgnss.init()
no_gnss_loc1=0
data_send_period=10
# no_gnss_loc2=0
sim_id = 0
imei1 = modem.getDevImei()
net.setModemFun(0)
net.setModemFun(1)
net.setApn('mcinet',0)
rtc = RTC()
TrackerMsgFormat = "*{imei};T41FoTA;{AorV};{date};{time};{GLat};{GLong};{time_s};{Blat};{Blong};{GSpeed};{GCog};{Gsat};{GHdop};{csq};{vbat};{Charger};{BandTamper};{Temperature};{mcc1}|{mnc1}|{lac1}|{cid1}|{rssi1};{mcc2}|{mnc2}|{lac2}|{cid2}|{rssi2};{mcc3}|{mnc3}|{lac3}|{cid3}|{rssi3};{mcc4}|{mnc4}|{lac4}|{cid4}|{rssi4};{mcc5}|{mnc5}|{lac5}|{cid5}|{rssi5};{mcc6}|{mnc6}|{lac6}|{cid6}|{rssi6};{mcc7}|{mnc7}|{lac7}|{cid7}|{rssi7};{sim_id};{doorTamper};{Accel};{SOS};0!"
#TrackerMsgFormat = "*{imei};T41CH140111;{AorV};{date};{time};{GLat};{GLong};{time_s};{Blat};{Blong};{GSpeed};{GCog};{Gsat};{GHdop};{csq};{vbat};{charger};{Band};{Temperature};{mcc1}|{mnc1}|{lac1}|{cid1}|{rssi1};{mcc2}|{mnc2}|{lac2}|{cid2}|{rssi2};{mcc3}|{mnc3}|{lac3}|{cid3}|{rssi3};{mcc4}|{mnc4}|{lac4}|{cid4}|{rssi4};{mcc5}|{mnc5}|{lac5}|{cid5}|{rssi5};{mcc6}|{mnc6}|{lac6}|{cid6}|{rssi6};{mcc7}|{mnc7}|{lac7}|{cid7}|{rssi7};{sim_id};{doorTamper};{Accel};{SoS};0!"
timer = Timer(Timer.Timer1)
TamperTimer = Timer(Timer.Timer2)

def TamperFunc(args):
    global BandTamper
    global BandTamperSent
    global doorTamper
    global doorTamperSent
    
    Band1=0; Band0=0;doorValue=0
    doorValue=adc.read(ADC.ADC1)
    IR_Tx.on()
    Band1=adc.read(ADC.ADC0)
    IR_Tx.off()
    Band0=adc.read(ADC.ADC0)
    if ((Band1<600) and (Band0>1000)):
        if (BandTamperSent==1):
            BandTamper=Band1
            BandTamperSent=0
    if ( doorValue<21):
        if (doorTamperSent==1):
            doorTamper=doorValue
            doorTamperSent=0
    if ((Band1<600) and (Band0>1000) and (doorValue<21)):
        Band_LED.off()
    if ((Band1>600)):
        Band_LED.on()
        BandTamper=Band1
        BandTamperSent=0
    if (doorValue>20):
        Band_LED.on()
        doorTamper=doorValue
        doorTamperSent=0
    if (Band0 < 600) :
        Band_LED.start_flicker(1000,2000,2)
        BandTamper=3800-Band0
        BandTamperSent=0
        
    
    


def func(args):
    global data_send_period
    global Charger
    global SOS
    global Band
    global doorTamper
    global Temperature
    global Accel
    global vbat
    cellInfoData = net.getCellInfo()
    mcc1=cellInfoData[2][0][2]; mnc1=cellInfoData[2][0][3]; lac1=hex(cellInfoData[2][0][4]); cid1=hex((cellInfoData[2][0][1])%65536); rssi1=cellInfoData[2][0][7]
    if len(cellInfoData[2]) >=2 :
        mcc2=cellInfoData[2][1][2]; mnc2=cellInfoData[2][1][3]; lac2=hex(cellInfoData[2][1][4]); cid2=hex((cellInfoData[2][1][1])%65536); rssi2=cellInfoData[2][1][7]
    else :
        mcc2=0;mnc2=0;lac2=0;cid2=0;rssi2=0;
    if len(cellInfoData[2]) >=3 :
        mcc3=cellInfoData[2][2][2]; mnc3=cellInfoData[2][2][3]; lac3=hex(cellInfoData[2][2][4]); cid3=hex((cellInfoData[2][2][1])%65536); rssi3=cellInfoData[2][2][7]
    else :
        mcc3=0;mnc3=0;lac3=0;cid3=0;rssi3=0;
    if len(cellInfoData[2]) >=4 :
        mcc4=cellInfoData[2][3][2]; mnc4=cellInfoData[2][3][3]; lac4=hex(cellInfoData[2][3][4]); cid4=hex((cellInfoData[2][3][1])%65536); rssi4=cellInfoData[2][3][7]
    else :
        mcc4=0;mnc4=0;lac4=0;cid4=0;rssi4=0;
    if len(cellInfoData[2]) >=5 :
        mcc5=cellInfoData[2][4][2]; mnc5=cellInfoData[2][4][3]; lac5=hex(cellInfoData[2][4][4]); cid5=hex((cellInfoData[2][4][1])%65536); rssi5=cellInfoData[2][4][7]
    else :
        mcc5=0;mnc5=0;lac5=0;cid5=0;rssi5=0;
    if len(cellInfoData[2]) >=6 :
        mcc6=cellInfoData[2][5][2]; mnc6=cellInfoData[2][5][3]; lac6=hex(cellInfoData[2][5][4]); cid6=hex((cellInfoData[2][5][1])%65536); rssi6=cellInfoData[2][5][7]
    else :
        mcc6=0;mnc6=0;lac6=0;cid6=0;rssi6=0;
    if len(cellInfoData[2]) >=7 :
        mcc7=cellInfoData[2][6][2]; mnc7=cellInfoData[2][6][3]; lac7=hex(cellInfoData[2][6][4]); cid7=hex((cellInfoData[2][6][1])%65536); rssi7=cellInfoData[2][6][7]
    else :
        mcc7=0;mnc7=0;lac7=0;cid7=0;rssi7=0;
    csq = net.csqQueryPoll()
    time_s = utime.mktime(utime.localtime())
    vbat = Power.getVbatt()/4200*100
    if (vbat < 25):
        Vibre.start_flicker(500,1000,3)
        
    # if(Charger == 1):   
    data=quecgnss.read(4096)
    #data[1].decode()
    #r=ure.search("GNGGA(.+?)V", data[1].decode())
    #print(buf,"\r\n")
    gngga1 = data[1].split("$GNGGA,")[1].split("\r\n")[0].split(",")
    gnrmc1 = data[1].split("$GNRMC,")[1].split("\r\n" )[0].split(",")
    if (len(gnrmc1)>0):
        if ((gnrmc1[0]) != ''):
            time_gps = str(int(float(gnrmc1[0])))
        else:
            time_gps = ''
    time = time_gps
    if (len(gnrmc1)>8):
        if ((gnrmc1[8]) != ''):
            date_gps = str(int(gnrmc1[8]))
        else:
            date_gps = ''
    date = date_gps
    if (len(date) == 5):
        date='0'+date
    GLat=str(gnrmc1[2])#str(gngga1[1])#Effect_latitude )
    GLong=str(gnrmc1[4])#str(gngga1[3])#Effect_longitude )
    Gsat=str(gngga1[6])
    GHdop=str(gngga1[7])
    #print('equipment IMET',imei)
    print(gngga1[2],'',GLat)
    print(gngga1[4],'',GLong)
    GCog = gnrmc1[6]
    if GCog == '' :
        GCog = 0
    GSpeed = gnrmc1[5]
    if GSpeed == '' :
        GSpeed = 0
    AorV = gnrmc1[1]
    # if GLat == '' or GLong == '' :
        # AorV = 'V'
    # else :
        # AorV = 'A'
    Blat=''
    Blong=''
    acc=0
    # if AorV == 'V' :
        # no_gnss_loc1 +=1
    # else :
        # no_gnss_loc1 = 0
    # if no_gnss_loc1 > 10 :
        # cellLocationData=cellLocator.getLocation("www.queclocator.com", 80, "1111111122222222", 8, 1)
        # Blat=cellLocationData[1]
        # Blong=cellLocationData[0]
        # acc=cellLocationData[2]
    acc = accel_dev.read_acceleration()
    Accel = (acc[0]+acc[1]+acc[2]) / 3
    Temperature = accel_dev.read_temperature()
    if (Charger == 1):
        notCharger=0
    else:
        notCharger=1
    TrackerData = TrackerMsgFormat.format(AorV=AorV, GLat=GLat, GLong=GLong, imei=imei1, date=date, time=time, vbat=vbat, sim_id=sim_id, Blat=Blat, Blong=Blong, acc=acc, time_s=time_s, csq=csq, Gsat=Gsat, GHdop=GHdop, mcc1=mcc1, mcc2=mcc2, mcc3=mcc3, mcc4=mcc4, mcc5=mcc5, mcc6=mcc6, mcc7=mcc7, mnc1=mnc1, mnc2=mnc2, mnc3=mnc3, mnc4=mnc4, mnc5=mnc5, mnc6=mnc6, mnc7=mnc7, lac1=lac1, lac2=lac2, lac3=lac3, lac4=lac4, lac5=lac5, lac6=lac6, lac7=lac7, cid1=cid1, cid2=cid2, cid3=cid3, cid4=cid4, cid5=cid5, cid6=cid6, cid7=cid7, rssi1=rssi1, rssi2=rssi2, rssi3=rssi3, rssi4=rssi4, rssi5=rssi5, rssi6=rssi6, rssi7=rssi7, GCog=GCog, GSpeed=GSpeed, SOS=SOS, doorTamper=doorTamper, BandTamper=BandTamper, Accel=Accel, Charger=notCharger, Temperature=Temperature)
    print(TrackerData)
    url_request = url + TrackerData
    response = request.get(url_request)
    response_txt = next(response.content)
    response_txt_csv = response_txt.split(",")
    print(response_txt)
    if(response_txt_csv[0] == '-1') :
        print('not logged \r\n')
    # if ((data_send_period!=int(response_txt_csv[3])) and (response_txt_csv[3]!='-1')) :
        # data_send_period=int(response_txt_csv[3])
        # timer.stop()
        # timer_period=data_send_period*1000
        # timer.start(period=timer_period, mode=timer.PERIODIC, callback=func)
    if(int(response_txt_csv[1]) == 2):
        if (int(response_txt_csv[2]) == 1):
            Vibre.start_flicker(2000,800,2)
        if (int(response_txt_csv[5]) == 1):
            TouchLED.start_flicker(200,800,2)
            Band_LED.start_flicker(200,800,2)
            Charger_LED.start_flicker(200,800,2)
            B3_LED.start_flicker(200,800,2)
            B2_LED.start_flicker(200,800,2)
            B1_LED.start_flicker(200,800,2)
            B0_LED.start_flicker(200,800,2)
        if (response_txt_csv[6] == "1*"):
            print("Turn off: N/I yet!")
        if (int(response_txt_csv[4]) == 1):
            print("FOTA : N/I yet!")
    
    SOS=0;Charger=0;BandTamperSent=1;doorTamperSent=1;Temperature=0;Accel=0
    response.close()
    
    # if uart.any() > 0:
        # buf = uart.read(uart.any())
        # buf = str(buf,"utf8")
        # gngga2 = buf[1].split("$GPGGA,")[1].split("\r\n" )[0].split(",")
        # time_gps1 = gngga2[0]
        # GLat1=str(gngga2[1])#Effect_latitude )
        # GLong1=str(gngga2[3])#Effect_longitude )
        # Gsat1=str(gngga2[6])
        # GHdop1=str(gngga2[7])
        # #print('equipment IMET',imei)
        # print(gngga2[2],'',GLat1)
        # print(gngga2[4],'',GLong1)
        # gnrmc2 = buf[1].split("$GPRMC,")[1].split("\r\n" )[0].split(",")
        # GCog1 = gnrmc2[6]
        # GSpeed1 = gnrmc2[5]
        # if GLat1 == '' or GLong1 == '' :
            # AorV1 = 'V'
        # else : 
            # AorV1 = 'A'
        # Blat1=''
        # Blong1=''
        # acc1=0
        # if AorV1 == 'V' :
            # no_gnss_loc2 +=1
        # else :
            # no_gnss_loc2 = 0
        # if no_gnss_loc2 > 10 :
            # cellLocationData=cellLocator.getLocation("www.queclocator.com", 80, "1111111122222222", 8, 1)
            # Blat1=cellLocationData[1]
            # Blong1=cellLocationData[0]
            # acc1=cellLocationData[2]
        # TrackerData1 = TrackerMsgFormat.format(AorV=AorV1, GLat=GLat1, GLong=GLong1, imei=imei2, date=date, time=time, vbat=vbat, sim_id=sim_id, Blat=Blat1, Blong=Blong1, acc=acc1, time_s=time_s, csq=csq, Gsat=Gsat1, GHdop=GHdop1, mcc1=mcc1, mcc2=mcc2, mcc3=mcc3, mnc1=mnc1, mnc2=mnc2, mnc3=mnc3, lac1=lac1, lac2=lac2, lac3=lac3, cid1=cid1, cid2=cid2, cid3=cid3, rssi1=rssi1, rssi2=rssi2, rssi3=rssi3, GCog=GCog1, GSpeed=GSpeed1)
        # print(TrackerData1)
        # url_request = url + TrackerData1
        # response = request.get(url_request)
        # response_txt = next(response.content)
        # print(response_txt)
        # if((response_txt[1] == '-' and response_txt[2] == '1') or (response_txt[2] != '1')) :
            # print('not logged \r\n')
        # response.close()

if __name__ == '__main__':
    # global data_send_period
    Vibre.start_flicker(200,1000,1)
    timer_period=data_send_period*1000
    timer.start(period=timer_period, mode=timer.PERIODIC, callback=func)
    TamperTimer.start(period=4000, mode=timer.PERIODIC, callback=TamperFunc)
    # while 1:
        # utime.sleep(data_send_period)
        
        # func()
