smartduvet

wifi:
    public static String WIFI_SSID_LOCAL = "SmartDuvet";
    public static String WIFI_PASS_LOCAL = "smduvet@2011";

url http://192.168.4.1

GET /api/info
->
{
	"temp_right":	6,
	"temp_left":	6,
	"light_onoff":	true,
	"light_value":	"230 255 43 64",
	"schedule_value":	"11:4",
	"schedule_onoff":	true,
	"wifi_version":	9,
	"ssid_wifi":	"Redmi",
	"sta_ip":	"",
	"wifi_sta_connected":	false,
	"serialId":	"defaultboard2",
	"serialId_len":	0,
	"macAddress":	"A1:54:FF:05:AA:FD",
	"wifi_available":	[{
			"ssid":	"Villa de la Vita",
			"rssi":	-61
		}, {
			"ssid":	"villadelavita_iot",
			"rssi":	-61
		}, {
			"ssid":	"Faiza Saqlain",
			"rssi":	-87
		}, {
			"ssid":	"Villa de la Vita",
			"rssi":	-90
		}, {
			"ssid":	"villadelavita_iot",
			"rssi":	-93
		}, {
			"ssid":	"",
			"rssi":	0
		}, {
			"ssid":	"",
			"rssi":	0
		}],
	"time_system":	[0, 0, 0]
}

rgba = light_value.split(" ") 
r = rgba[0], g = rgba[1], b = rgba[2], intensity = [rgba3]


{
	"temp_right":	6,
	"temp_left":	6,
	"light_onoff":	true,
	"light_value":	"230 255 43 64",
	"schedule_value":	"11:4",
	"schedule_onoff":	true,
	"wifi_version":	9,
	"ssid_wifi":	"villadelavita_iot",
	"sta_ip":	"10.10.107.72",
	"wifi_sta_connected":	true,
	"serialId":	"defaultboard2",
	"serialId_len":	0,
	"macAddress":	"A1:54:FF:05:AA:FD",
	"wifi_available":	[{
			"ssid":	"Villa de la Vita",
			"rssi":	-60
		}, {
			"ssid":	"villadelavita_iot",
			"rssi":	-61
		}, {
			"ssid":	"Villa de la Vita",
			"rssi":	-89
		}, {
			"ssid":	"villadelavita_iot",
			"rssi":	-89
		}],
	"time_system":	[17, 57, 13]
}



GET /api/scanwifi
-> 200 text/html
Scanning Wifi

# refreshes wifi_available in /api/info

GET /api/gettimesystem
-> 200 text/html
Getting time system successfully

# refreshes time_system in /api/info



POST /api/boxsettings
{
Mac_add_1: mac_int[0]
Mac_add_2: mac_int[1]
Mac_add_3: mac_int[2]
Mac_add_4: mac_int[3]
Mac_add_5: mac_int[4]
Mac_add_6: mac_int[5]
serialId: processDataSerialIDSend(serialId)
}

function hexStringToIntrray(str) {
        return new Array(str.length / 2).fill().map((_, i) => parseInt(str.substring(i * 2, (i + 1) * 2), 16))
    }

function processMacAddressSend(mac) {
    return hexStringToIntrray(mac.replaceAll(":", ""))
}

 function processDataSerialIDSend(serialId) {
        return `${serialId.length.toString().padStart(2, "0")}06B_SERIAL:${serialId}B_PASS:123456`;
}

mac_int = processMacAddressSend(mac)





POST /api/makbednow
{}



POST /api/schedule
{
schedule_onoff:  # 2 - true/3 - false
schedule_hour: # number
schedule_minute: # number
}



                int parseInt = Integer.parseInt(MainActivity.savedMin);
                int parseInt2 = Integer.parseInt(MainActivity.savedHour);
                if (BedFragment.this.timePresetAmPm.getText().equals("PM")) {
                    if (parseInt2 < 12) {
                        parseInt2 += 12;
                    }
                } else if (parseInt2 == 12) {
                    parseInt2 = 0;
                }
                if (parseInt2 >= 24) {
                    parseInt2 = 0;
                }

schedule_hour = parseInt2
schedule_minute = parseInt




POST /api/light
{
light_onoff: # true/false
red: # 0-255
green: # 0-255
blue: # 0-255
intensity: # 0-255
}




POST /api/temp/left
{ temp_left: }
POST /api/temp/right
{ temp_right: }


public static void setTemperature(float f, float f2) {
        Float valueOf = Float.valueOf(Math.abs(f - 180.0f));
        if (Utility.LOG_RUN) {
            Log.e("SD", "New Left Temp:" + valueOf);
        }
        Float valueOf2 = Float.valueOf(Math.abs(f2 - 180.0f));
        if (Utility.LOG_RUN) {
            Log.e("SD", "New Right Temp:" + valueOf2);
        }
        int floatValue = ((int) (valueOf.floatValue() / 16.0f)) + 1;
        int i = 11;
        if (floatValue < 1) {
            floatValue = 1;
        } else if (floatValue > 11) {
            floatValue = 11;
        }
        int floatValue2 = ((int) (valueOf2.floatValue() / 16.0f)) + 1;
        if (floatValue2 < 1) {
            i = 1;
        } else if (floatValue2 <= 11) {
            i = floatValue2;
        }
        rightTemperature = i;
        leftTemperature = floatValue;
        int[] iArr = {i, floatValue};


            if (iArr[0] != appValueActive.getRightTemperature()) {
                ApiDataLocalTempRightPost apiDataLocalTempRightPost = new ApiDataLocalTempRightPost();
                apiDataLocalTempRightPost.setTemp_right(iArr[0]);
                if (mWifiNetworkConnected) {
                    vmWifiLocalData.PostTempRightValueLocal(mWifiNetworkIP, apiDataLocalTempRightPost);
                } else {
                    vmWifiLocalData.PostTempRightValueLocal((String) null, apiDataLocalTempRightPost);
                }
                appValueActive.setRightTemperature(iArr[0]);
            }
            if (iArr[1] != appValueActive.getLeftTemperature()) {
                ApiDataLocalTempLeftPost apiDataLocalTempLeftPost = new ApiDataLocalTempLeftPost();
                apiDataLocalTempLeftPost.setTemp_left(iArr[1]);
                if (mWifiNetworkConnected) {
                    vmWifiLocalData.PostTempLeftValueLocal(mWifiNetworkIP, apiDataLocalTempLeftPost);
                } else {
                    vmWifiLocalData.PostTempLeftValueLocal((String) null, apiDataLocalTempLeftPost);
                }
                appValueActive.setLeftTemperature(iArr[1]);
            }
    }




POST /api/wifista
{
ssid_pass: processDataWifiSendSelected(ssid, password)
ssid_wifi: # wifi ssid
pass_wifi:  #wifi pass
}
->
408
Server closed this connection
->
200 
Post wifi connection successfully

# api/scanwifi after api/wifista is mandatory to connect to selected wifi


function processDataWifiSendSelected(ssid, password) {
        return `${(ssid.length.toString().padStart(2, "0"))}${(password.length.toString().padStart(2, "0"))}SSID:${ssid}PASS:${password}`
   }


 private BroadcastReceiver actionProcess = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            Boolean unused = Transmit_Data_BLE.mProcessBLEData = false;
            if (Utils.TRANSMIT_STARTCONNECT.equals(action)) {
                Transmit_Data_BLE.this.startBLEConnection();
            } else if (Utils.TRANSMIT_CLOSESERVICE.equals(action)) {
                Transmit_Data_BLE.this.close_service();
                Transmit_Data_BLE.this.stopSelf();
            } else if (Utils.TRANSMIT_SENDLEDRGB.equals(action)) {
                byte[] byteArrayExtra = intent.getByteArrayExtra(Utils.TRANSMIT_SENDLEDRGB_DATA);
                Transmit_Data_BLE.this.sendLedRGB(byteArrayExtra[0], byteArrayExtra[1], byteArrayExtra[2], byteArrayExtra[3], Boolean.valueOf(byteArrayExtra[4] != 0).booleanValue());
            } else if (Utils.TRANSMIT_SENDSCHEDULE.equals(action)) {
                int[] intArrayExtra = intent.getIntArrayExtra(Utils.TRANSMIT_SENDSCHEDULE_DATA);
                Transmit_Data_BLE.this.setBedMakingSetting(intArrayExtra[0], intArrayExtra[1], intArrayExtra[2]);
            } else if (Utils.TRANSMIT_SENDTEMP.equals(action)) {
                int[] intArrayExtra2 = intent.getIntArrayExtra(Utils.TRANSMIT_SENDTEMP_DATA);
                Transmit_Data_BLE.this.setTemperature(intArrayExtra2[0], intArrayExtra2[1]);
            } else if (Utils.TRANSMIT_MAKEBEDNOW.equals(action)) {
                Transmit_Data_BLE.this.makeBedNow();
            } else if (Utils.TRANSMIT_TIME_GET_TIME.equals(action)) {
                Transmit_Data_BLE.this.sendTimerGetTime();
            } else if (Utils.TRANSMIT_TIME_UPDATE_CLOCK.equals(action)) {
                Transmit_Data_BLE.this.sendTimerUpdateClock();
            } else if (Utils.TRANSMIT_GET_FIRMWAREVERSION.equals(action)) {
                Transmit_Data_BLE.this.getFirmwareVersion();
            } else if (Utils.TRANSMIT_GET_WIFI_STATUS.equals(action)) {
                Transmit_Data_BLE.this.getWifiStatus();
            } else if (Utils.TRANSMIT_SET_WIFI_CONNECT.equals(action) || Utils.TRANSMIT_SET_SERIAL_ID_BOX.equals(action)) {
                Transmit_Data_BLE.this.sendDataWifiService(intent.getStringExtra(Utils.TRANSMIT_SET_WIFI_SERVICE_DATA));
            }
        }
    };




