from core.base.model.ProjectAliceObject import ProjectAliceObject


class TasmotaConfigs(ProjectAliceObject):
	BACKLOG_CONFIGS = [
		{
			'cmds'     : [
				'ssid1 {ssid}',
				'password1 {wifipass}'
			],
			'waitAfter': 15
		},
		{
			'cmds'     : [
				'MqttHost {mqtthost}',
				'MqttClient {type}_{location}',
				'TelePeriod 0',
				'module 18'
			],
			'waitAfter': 8
		},
		{
			'cmds'     : [
				'gpio0 9',
				'gpio12 21'
			],
			'waitAfter': 8
		},
		{
			'cmds'     : [
				'friendlyname {type} - {location}'
			],
			'waitAfter': 8
		},
		{
			'cmds'     : [
				'switchmode 2',
				'switchtopic 0'
			],
			'waitAfter': 8
		},
		{
			'cmds'     : [
				'topic {identifier}',
				'grouptopic all',
				'fulltopic projectalice/devices/tasmota/%prefix%/%topic%/',
				'prefix1 cmd',
				'prefix2 feedback',
				'prefix3 feedback'
			],
			'waitAfter': 8
		},
		{
			'cmds'     : [
				'rule1 on System#Boot do publish projectalice/devices/tasmota/feedback/hello/{identifier} {{"siteId":"{location}","deviceType":"{type}","uid":"{identifier}"}} endon',
				'rule1 1',
				'rule2 on switch1#state do publish projectalice/devices/tasmota/feedback/{identifier} {{"siteId":"{location}","deviceType":"{type}","feedback":%value%,"uid":"{identifier}"}} endon',
				'rule2 1',
				'restart 1'
			],
			'waitAfter': 5
		}
	]

	BACKLOG_TEMPSENSORCONFIGS = [
		{
			'cmds'     : [
				'ssid1 {ssid}',
				'password1 {wifipass}'
			],
			'waitAfter': 15
		},
		{
			'cmds'     : [
				'MqttHost {mqtthost}',
				'MqttClient {type}_{location}',
				'TelePeriod 300',
				'module 18'
			],
			'waitAfter': 8
		},
		{
			'cmds'     : [
				'gpio{gpio} 1'
			],
			'waitAfter': 8
		},
		{
			'cmds'     : [
				'friendlyname {type} - {location}'
				],
			'waitAfter': 8
		},
		{
			'cmds'     : [
				'switchmode 0',
				'switchtopic 0'
			],
			'waitAfter': 8
		},
		{
			'cmds'     : [
				'topic {identifier}',
				'grouptopic all',
				'fulltopic projectalice/devices/tasmota/%prefix%/%topic%/',
				'prefix1 cmd',
				'prefix2 feedback',
				'prefix3 feedback'
			],
			'waitAfter': 8
		},
		{
			'cmds'     : [
				'rule1 on System#Boot do publish projectalice/devices/tasmota/feedback/hello/{identifier} {{"siteId":"{location}","deviceType":"{type}","uid":"{identifier}"}} endon',
				'rule1 1',
			],
			'waitAfter': 12
		},
		{
			'cmds'     : [
				'rule2 on tele-{brand}#temperature do var1 %value% endon on tele-{brand}#Humidity do var2 %value% endon on tele-{brand}#{sensorValue} do var3 %value% endon on tele-{brand}#{sensorValue} do event sendtemp endon on event#sendtemp do publish projectalice/devices/tasmota/feedback/{identifier}/sensor {{"sensorType":"{brand}","siteId":"{location}","deviceType":"{type}","Temperature":"%Var1%","Humidity":"%Var2%","{sensorValue}":"%Var3%","uid":"{identifier}"}} endon ',
				'rule2 1',
				'restart 1'
			],
			'waitAfter': 8
		}
	]

	BASE_TOPIC = 'projectalice/devices/tasmota/cmd/{identifier}'

	CONFIGS = {
		'wemos': {
			'switch': [
				[
					{
						'topic'  : BASE_TOPIC + '/Module',
						'payload': '18'
					}
				],
				[
					{
						'topic'  : BASE_TOPIC + '/MqttClient',
						'payload': 'switch_{location}'
					},
					{
						'topic'  : BASE_TOPIC + '/Gpio0',
						'payload': '9'
					},
					{
						'topic'  : BASE_TOPIC + '/Gpio12',
						'payload': '21'
					},
					{
						'topic'  : BASE_TOPIC + '/Prefix1',
						'payload': 'cmd'
					},
					{
						'topic'  : BASE_TOPIC + '/Prefix2',
						'payload': 'feedback'
					},
					{
						'topic'  : BASE_TOPIC + '/Prefix3',
						'payload': 'feedback'
					},
					{
						'topic'  : BASE_TOPIC + '/GroupTopic',
						'payload': 'all'
					},
					{
						'topic'  : BASE_TOPIC + '/TelePeriod',
						'payload': '0'
					},
					{
						'topic'  : BASE_TOPIC + '/FriendlyName',
						'payload': 'Switch - {location}'
					},
					{
						'topic'  : BASE_TOPIC + '/SwitchMode',
						'payload': '2'
					},
					{
						'topic'  : BASE_TOPIC + '/SwitchTopic',
						'payload': '0'
					},
					{
						'topic'  : BASE_TOPIC + '/Topic',
						'payload': '0'
					},
					{
						'topic'  : BASE_TOPIC + '/rule1', #NOSONAR
						'payload': 'on switch1#state do publish projectalice/devices/tasmota/feedback/{identifier} {{"siteId":"{location}","deviceType":"{type}","feedback":%value%,"uid":"{identifier}"}} endon'
					},
					{
						'topic'  : BASE_TOPIC + '/rule1',
						'payload': '1'
					},
					{
						'topic'  : BASE_TOPIC + '/Restart',
						'payload': '1'
					}
				]
			],
			'pir'   : [
				[
					{
						'topic'  : BASE_TOPIC + '/Module',
						'payload': '18'
					}
				],
				[
					{
						'topic'  : BASE_TOPIC + '/MqttClient',
						'payload': 'PIR_{location}'
					},
					{
						'topic'  : BASE_TOPIC + '/Gpio0',
						'payload': '9'
					},
					{
						'topic'  : BASE_TOPIC + '/Gpio12',
						'payload': '21'
					},
					{
						'topic'  : BASE_TOPIC + '/FriendlyName',
						'payload': 'PIR - {location}'
					},
					{
						'topic'  : BASE_TOPIC + '/SwitchMode',
						'payload': '1'
					},
					{
						'topic'  : BASE_TOPIC + '/SwitchTopic',
						'payload': '0'
					},
					{
						'topic'  : BASE_TOPIC + '/rule1',
						'payload': 'on switch1#state do publish projectalice/devices/tasmota/feedback/{identifier} {{"siteId":"{location}","deviceType":"{type}","feedback":%value%,"uid":"{identifier}"}} endon'
					},
					{
						'topic'  : BASE_TOPIC + '/rule1',
						'payload': '1'
					},
					{
						'topic'  : BASE_TOPIC + '/Restart',
						'payload': '1'
					}
				]
			]
		}
	}


	def __init__(self, deviceType: str, uid: str):
		super().__init__()
		self._name = 'TasmotaConfigs'
		self._brand = 'DHT11'
		self._gpioUsed = 0
		self._deviceType = deviceType
		self._uid = uid


	#@staticmethod
	def getTasmotaDownloadLink(self) -> str:
		if 'BME280' in self._brand:
			return 'https://github.com/arendst/Tasmota/releases/download/v8.3.1/tasmota-sensors.bin'
		else:
			return 'https://github.com/arendst/Tasmota/releases/download/v8.3.1/tasmota.bin'


	@property
	def deviceType(self) -> str:
		return self._deviceType


	@property
	def uid(self) -> str:
		return self._uid


	def getConfigs(self, deviceBrand: str, location: str) -> list:
		if deviceBrand not in self.CONFIGS:
			self.logError(f'[{self._name}] Devices brand "{deviceBrand}" unknown')
			return list()

		elif self._deviceType not in self.CONFIGS[deviceBrand]:
			self.logError(f'[{self._name}] Devices type "{self._deviceType}" unknown')
			return list()

		else:
			confs = self.CONFIGS[deviceBrand][self._deviceType].copy()
			for deviceConfs in confs:
				for conf in deviceConfs:
					conf['topic'] = conf['topic'].format(identifier=self._uid)
					conf['payload'] = conf['payload'].format(identifier=self._uid, location=location, type=self._deviceType)
			return confs


	def getBacklogConfigs(self, location: str) -> list:
		sensorValue: str
		if 'BME280' in self._brand:
			sensorValue = 'Pressure'
		else:
			sensorValue = 'DewPoint'
		cmds = list()
		if 'envSensor' in self._deviceType:
			if self.checkSensorBrand:
				runConfigs = self.BACKLOG_TEMPSENSORCONFIGS
			else:
				runConfigs = self.BACKLOG_CONFIGS
		else:
			runConfigs = self.BACKLOG_CONFIGS
		for cmdGroup in runConfigs:
			group = dict()
			group['cmds'] = [cmd.format(
				mqtthost=self.Commons.getLocalIp(),
				identifier=self._uid,
				location=location,
				type=self._deviceType,
				ssid=self.ConfigManager.getAliceConfigByName('ssid'),
				wifipass=self.ConfigManager.getAliceConfigByName('wifipassword'),
				brand=self._brand,
				gpio=self._gpioUsed,
				sensorValue=sensorValue
			) for cmd in cmdGroup['cmds']] # type: ignore

			group['waitAfter'] = cmdGroup['waitAfter'] # type: ignore
			cmds.append(group)

		return cmds


	@staticmethod
	def checkSensorBrand() -> bool:
		supportedSensors = ('BME280', 'DHT11', 'DHT22', 'AM2302', 'AM2301')
		for brand in supportedSensors:
			if brand in supportedSensors:
				return True
			else:
				return False
