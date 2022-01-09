import esptool
import re
import requests
import serial
import threading
import time
from esptool import ESPLoader
from pathlib import Path
from typing import Dict

from core.base.model.AliceSkill import AliceSkill
from core.device.model.Device import Device
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import MqttHandler
from core.util.model.TelemetryType import TelemetryType
# noinspection PyPackages
from .TasmotaConfigs import TasmotaConfigs


class Tasmota(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: This skill allows you to not only connect tasmota esp devices, but listen to them
	"""

	def __init__(self):
		self._initializingSkill = False
		self._confArray = []
		self._tasmotaConfigs = None
		self._broadcastFlag = threading.Event()
		self._flashThread = None
		self._isActive = True
		super().__init__()


	@MqttHandler('projectalice/devices/tasmota/feedback/hello/+')
	def connectingHandler(self, session: DialogSession):
		identifier = session.intentName.split('/')[-1]
		if identifier:
			self.DeviceManager.deviceConnecting(uid=identifier)


	@MqttHandler('projectalice/devices/tasmota/feedback/bye/+')
	def disconnectingHandler(self, session: DialogSession):
		identifier = session.intentName.split('/')[-1]
		if identifier:
			self.DeviceManager.deviceDisconnecting(uid=identifier)


	def envSensorResults(self, newPayload: dict, deviceUid: str, locationId: int):
		deviceId = self.DeviceManager.getDevice(uid=deviceUid).id

		for item in newPayload.items():
			teleType: str = item[0]
			teleType = teleType.upper()
			# TODO some of these may need moved to another method ? added because they are all environmental sensing
			self.logDebug(f'Reading environmental sensor type {teleType}: {item[1]}')  # uncomment me to see incoming temperature payload
			try:
				if 'TEMPERATURE' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.TEMPERATURE, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'HUMIDITY' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.HUMIDITY, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'DEWPOINT' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.DEWPOINT, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'PRESSURE' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.PRESSURE, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'GAS' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.GAS, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'AIR_QUALITY' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.AIR_QUALITY, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'UV_INDEX' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.UV_INDEX, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'NOISE' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.NOISE, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'CO2' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.CO2, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'RAIN' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.RAIN, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'SUM_RAIN_1' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.SUM_RAIN_1, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'SUM_RAIN_24' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.SUM_RAIN_24, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'WIND_STRENGTH' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.WIND_STRENGTH, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'WIND_ANGLE' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.WIND_ANGLE, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'GUST_STRENGTH' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.GUST_STRENGTH, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'GUST_ANGLE' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.GUST_ANGLE, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)
				elif 'Illuminance' in teleType:
					self.TelemetryManager.storeData(ttype=TelemetryType.LIGHT, value=item[1], service=self.name, deviceId=deviceId, locationId=locationId)

				# TODO Capture if SWITCH OR POWER and send to another method for database storing/action somewhere ?
			except Exception as e:
				self.logError(f'An exception occurred adding {teleType} reading: {e}')


	@staticmethod
	def makeSingleDict(newPayload):
		singleDict = {}
		for k, v in newPayload.items():
			if isinstance(v, dict):
				singleDict.update(v)
			else:
				singleDict.update({k: v})
		return singleDict


	@MqttHandler('projectalice/devices/tasmota/feedback/+/SENSOR')
	def sensorTeleFeedback(self, session: DialogSession):
		if not self.ConfigManager.getAliceConfigByName('enableDataStoring'):
			self._isActive = False
			self.logInfo('Data storing is disabled')
			return

		payload: Dict = session.payload
		uid = session.intentName.split("/")[-2]
		device = self.DeviceManager.getDeviceByUID(uid=uid)
		if not device:
			return

		location = device.getMainLocation()

		relevantPayload = dict()
		reg = re.compile("POWER.")
		reg2 = re.compile("Switch.")

		for key, item in payload.items():
			if isinstance(item, dict) or 'Switch' in item or 'POWER' in item or bool(re.match(reg, key)) or bool(re.match(reg2, key)):
				relevantPayload[key] = item

		cleanedDictionary = self.makeSingleDict(relevantPayload)

		self.envSensorResults(newPayload=cleanedDictionary, deviceUid=session.deviceUid, locationId=location.id)


	@MqttHandler('projectalice/devices/tasmota/feedback/+')
	def feedbackHandler(self, session: DialogSession):
		deviceUid = session.deviceUid
		payload = session.payload
		feedback = payload.get('feedback')
		if not feedback:
			return

		deviceType = payload['deviceType']

		if deviceType == 'switch':
			if feedback > 0:
				self.SkillManager.skillBroadcast('buttonPressed', deviceUid=deviceUid)
			else:
				self.SkillManager.skillBroadcast('buttonReleased', deviceUid=deviceUid)
		elif deviceType == 'pir':
			if feedback > 0:
				self.SkillManager.skillBroadcast('motionDetected', deviceUid=deviceUid)
			else:
				self.SkillManager.skillBroadcast('motionStopped', deviceUid=deviceUid)


	def _initConf(self, identifier: str, deviceBrand: str, deviceType: str):
		self._tasmotaConfigs = TasmotaConfigs(deviceType, identifier)
		self._confArray = self._tasmotaConfigs.getConfigs(deviceBrand, self.DeviceManager.broadcastRoom)


	def startTasmotaFlashingProcess(self, device: Device, replyOnDeviceUid: str, session: DialogSession) -> bool:
		if session:
			self.ThreadManager.doLater(interval=0.5, func=self.MqttManager.endDialog, args=[session.sessionId, self.randomTalk('connectESPForFlashing')])
		elif replyOnDeviceUid:
			self.ThreadManager.doLater(interval=0.5, func=self.MqttManager.say, args=[self.randomTalk('connectESPForFlashing')])

		self._broadcastFlag.set()

		binFile = Path('tasmota.bin')
		if binFile.exists():
			binFile.unlink()

		try:
			tasmotaConfigs = TasmotaConfigs(deviceType=device.getDeviceType().ESPTYPE, uid='dummy')
			req = requests.get(tasmotaConfigs.getTasmotaDownloadLink())
			with binFile.open('wb') as file:
				file.write(req.content)
				self.logInfo('Downloaded tasmota.bin')
		except Exception as e:
			self.logError(f'Something went wrong downloading tasmota.bin: {e}')
			self._broadcastFlag.clear()
			return False

		self.ThreadManager.newThread(name='flashThread', target=self.doFlashTasmota, args=[device, replyOnDeviceUid])
		return True


	def doFlashTasmota(self, device: Device, replyOnDeviceUid: str):
		port = self.DeviceManager.findUSBPort(timeout=60)
		if not port:
			if replyOnDeviceUid:
				self.say(text=self.randomTalk('noESPFound', skill='Tasmota'), deviceUid=replyOnDeviceUid)
			self._broadcastFlag.clear()
			return

		if replyOnDeviceUid:
			self.say(text=self.randomTalk('usbDeviceFound', skill='AliceCore'), deviceUid=replyOnDeviceUid)
		try:
			mac = ESPLoader.detect_chip(port=port, baud=115200).read_mac()
			mac = ':'.join([f'{x:02x}' for x in mac])
			cmd = [
				'--port', port,
				'--baud', '115200',
				'--after', 'no_reset', 'write_flash',
				'--flash_mode', 'dout', '0x00000', 'tasmota.bin',
				'--erase-all'
			]

			esptool.main(cmd)
		except Exception as e:
			self.logError(f'Something went wrong flashing esp device: {e}')
			if replyOnDeviceUid:
				self.say(text=self.randomTalk('espFailed', skill='Tasmota'), deviceUid=replyOnDeviceUid)
			self._broadcastFlag.clear()
			return

		self.logInfo('Tasmota flash done')
		if replyOnDeviceUid:
			self.say(text=self.randomTalk('espFlashedUnplugReplug', skill='Tasmota'), deviceUid=replyOnDeviceUid)
		found = self.DeviceManager.findUSBPort(timeout=60)
		if found:
			if replyOnDeviceUid:
				self.say(text=self.randomTalk('espFoundReadyForConf', skill='Tasmota'), deviceUid=replyOnDeviceUid)
			time.sleep(10)
			uid = self.DeviceManager.getFreeUID(mac)
			tasmotaConfigs = TasmotaConfigs(deviceType=device.getDeviceType().ESPTYPE, uid=uid)
			confs = tasmotaConfigs.getBacklogConfigs(device.getMainLocation().getSaveName())
			if not confs:
				self.logError('Something went wrong getting tasmota configuration')
				if replyOnDeviceUid:
					self.say(text=self.randomTalk('espFailed', skill='Tasmota'), deviceUid=replyOnDeviceUid)
			else:
				ser = serial.Serial()
				ser.baudrate = 115200
				ser.port = port
				ser.open()

				try:
					for group in confs:
						command = ';'.join(group['cmds'])
						if len(group['cmds']) > 1:
							command = f'Backlog {command}'

						arr = list()
						if len(command) > 50:
							while len(command) > 50:
								arr.append(command[:50])
								command = command[50:]
							arr.append(f'{command}\r\n')
						else:
							arr.append(f'{command}\r\n')

						for piece in arr:
							ser.write(piece.encode())
							self.logInfo('Sent {}'.format(piece.replace('\r\n', '')))
							time.sleep(0.5)

						time.sleep(group['waitAfter'])

					ser.close()
					self.logInfo('Tasmota flashing and configuring done')
					if replyOnDeviceUid:
						self.say(text=self.randomTalk('espFlashingDone', skill='Tasmota'), deviceUid=replyOnDeviceUid)

					# setting the uid marks the addition as complete
					device.pairingDone(uid=uid)
					self._broadcastFlag.clear()

				except Exception as e:
					self.logError(f'Something went wrong writing configuration to esp device: {e}')
					if replyOnDeviceUid:
						self.say(text=self.randomTalk('espFailed', skill='Tasmota'), deviceUid=replyOnDeviceUid)
					self._broadcastFlag.clear()
					ser.close()
		else:
			if replyOnDeviceUid:
				self.say(text=self.randomTalk('espFailed', skill='Tasmota'), deviceUid=replyOnDeviceUid)
			self._broadcastFlag.clear()


	@property
	def broadcastFlag(self) -> threading.Event:
		return self._broadcastFlag
