import threading
import time
from pathlib import Path

import esptool
import requests
import serial
from esptool import ESPLoader
from typing import Dict

from core.base.model.AliceSkill import AliceSkill
from core.device.model.Device import Device
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import MqttHandler
from core.util.model.TelemetryType import TelemetryType

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

		super().__init__()


	@MqttHandler('projectalice/devices/tasmota/feedback/hello/+')
	def connectingHandler(self, session: DialogSession):
		identifier = session.intentName.split('/')[-1]
		if self.DeviceManager.getDeviceByUID(identifier):
			# This device is known
			self.logInfo(f'A device just connected in {session.siteId}')
			self.DeviceManager.deviceConnecting(uid=identifier)
		else:
			# We did not ask Alice to add a new device
			if not self.broadcastFlag.is_set():
				self.logWarning('A device is trying to connect to Alice but is unknown')


	@MqttHandler('projectalice/devices/tasmota/feedback/+')
	def feedbackHandler(self, session: DialogSession):
		siteId = session.siteId
		payload = session.payload

		feedback = payload.get('feedback')
		if not feedback:
			return

		deviceType = payload['deviceType']

		if deviceType == 'switch':
			if feedback > 0:
				self.SkillManager.skillBroadcast('buttonPressed', siteId=siteId)
			else:
				self.SkillManager.skillBroadcast('buttonReleased', siteId=siteId)
		elif deviceType == 'pir':
			if feedback > 0:
				self.SkillManager.skillBroadcast('motionDetected', siteId=siteId)
			else:
				self.SkillManager.skillBroadcast('motionStopped', siteId=siteId)


	@MqttHandler('projectalice/devices/tasmota/feedback/+/sensor')
	def sensorHandler(self, session: DialogSession):
		siteId = session.siteId
		payload: Dict = session.payload

		# TODO type should be a field in payload, this is too cpu expensive

		bme280 = payload.get('BME280')
		if bme280:
			self.TelemetryManager.storeData(ttype=TelemetryType.TEMPERATURE, value=bme280['Temperature'], service=self.name, siteId=siteId)
			self.TelemetryManager.storeData(ttype=TelemetryType.HUMIDITY, value=bme280['Humidity'], service=self.name, siteId=siteId)
			self.TelemetryManager.storeData(ttype=TelemetryType.PRESSURE, value=bme280['Pressure'], service=self.name, siteId=siteId)
			return


		dht11 = payload.get('DHT11')
		if not dht11:
			dht11 = payload.get('DHT22')

		if dht11:
			self.TelemetryManager.storeData(ttype=TelemetryType.TEMPERATURE, value=dht11['Temperature'], service=self.name, siteId=siteId)
			self.TelemetryManager.storeData(ttype=TelemetryType.HUMIDITY, value=dht11['Humidity'], service=self.name, siteId=siteId)


	def _initConf(self, identifier: str, deviceBrand: str, deviceType: str):
		self._tasmotaConfigs = TasmotaConfigs(deviceType, identifier)
		self._confArray = self._tasmotaConfigs.getConfigs(deviceBrand, self.DeviceManager.broadcastRoom)


	def startTasmotaFlashingProcess(self, device: Device, replyOnSiteId: str, session: DialogSession) -> bool:
		replyOnSiteId = self.MqttManager.getDefaultSiteId(replyOnSiteId)
		if session:
			self.ThreadManager.doLater(interval=0.5, func=self.MqttManager.endDialog, args=[session.sessionId, self.randomTalk('connectESPForFlashing')])
		elif replyOnSiteId:
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

		self.ThreadManager.newThread(name='flashThread', target=self.doFlashTasmota, args=[device, replyOnSiteId])
		return True


	def doFlashTasmota(self, device: Device, replyOnSiteId: str):
		port = self.DeviceManager.findUSBPort(timeout=60)
		if not port:
			if replyOnSiteId:
				self.MqttManager.say(text=self.TalkManager.randomTalk('noESPFound', skill='Tasmota'), client=replyOnSiteId)
			self._broadcastFlag.clear()
			return

		if replyOnSiteId:
			self.MqttManager.say(text=self.TalkManager.randomTalk('usbDeviceFound', skill='AliceCore'), client=replyOnSiteId)
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
			if replyOnSiteId:
				self.MqttManager.say(text=self.TalkManager.randomTalk('espFailed', skill='Tasmota'), client=replyOnSiteId)
			self._broadcastFlag.clear()
			return

		self.logInfo('Tasmota flash done')
		if replyOnSiteId:
			self.MqttManager.say(text=self.TalkManager.randomTalk('espFlashedUnplugReplug', skill='Tasmota'), client=replyOnSiteId)
		found = self.DeviceManager.findUSBPort(timeout=60)
		if found:
			if replyOnSiteId:
				self.MqttManager.say(text=self.TalkManager.randomTalk('espFoundReadyForConf', skill='Tasmota'), client=replyOnSiteId)
			time.sleep(10)
			uid = self.DeviceManager.getFreeUID(mac)
			tasmotaConfigs = TasmotaConfigs(deviceType=device.getDeviceType().ESPTYPE, uid=uid)
			confs = tasmotaConfigs.getBacklogConfigs(device.getMainLocation().getSaveName())
			if not confs:
				self.logError('Something went wrong getting tasmota configuration')
				if replyOnSiteId:
					self.MqttManager.say(text=self.TalkManager.randomTalk('espFailed', skill='Tasmota'), client=replyOnSiteId)
			else:
				ser = serial.Serial()
				ser.baudrate = 115200
				ser.port = port
				ser.open()

				try:
					for group in confs:
						command = ';'.join(group['cmds'])
						if len(group['cmds']) > 1:
							command = f'Backlog {cmd}'

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
					if replyOnSiteId:
						self.MqttManager.say(text=self.TalkManager.randomTalk('espFlashingDone', skill='Tasmota'), client=replyOnSiteId)

					# setting the uid marks the addition as complete
					device.pairingDone(uid=uid)
					self._broadcastFlag.clear()

				except Exception as e:
					self.logError(f'Something went wrong writting configuration to esp device: {e}')
					if replyOnSiteId:
						self.MqttManager.say(text=self.TalkManager.randomTalk('espFailed', skill='Tasmota'), client=replyOnSiteId)
					self._broadcastFlag.clear()
					ser.close()
		else:
			if replyOnSiteId:
				self.MqttManager.say(text=self.TalkManager.randomTalk('espFailed', skill='Tasmota'), client=replyOnSiteId)
			self._broadcastFlag.clear()


	@property
	def broadcastFlag(self) -> threading.Event:
		return self._broadcastFlag
