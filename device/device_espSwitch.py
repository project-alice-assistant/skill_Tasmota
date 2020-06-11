from core.device.model.Device import Device
from core.device.model.Location import Location
from core.device.model.DeviceType import DeviceType
from core.commons import constants
import sqlite3
import threading
import socket
from core.base.model.ProjectAliceObject import ProjectAliceObject
from core.dialog.model.DialogSession import DialogSession
from skills.Tasmota import Tasmota
from core.device.model.DeviceException import requiresWIFISettings


class device_espSwitch(DeviceType):

	DEV_SETTINGS = ""
	LOC_SETTINGS = ""
	ESPTYPE = "switch"
	tasmotaLink = 'https://github.com/arendst/Tasmota/releases/download/v8.3.1/tasmota.bin'

	def __init__(self, data: sqlite3.Row):
		super().__init__(data, devSettings=self.DEV_SETTINGS, locSettings=self.LOC_SETTINGS, heartbeatRate=600)


	def discover(self, device: Device, uid: str, replyOnSiteId: str = "", session:DialogSession = None) -> bool:
		if not self.ConfigManager.getAliceConfigByName('ssid'):
			raise requiresWIFISettings()

		return self.parentSkillInstance.startTasmotaFlashingProcess(device, replyOnSiteId, session)


	def getDeviceIcon(self, device: Device) -> str:
		if not device.uid:
			return 'device_espSwitch.png'
		if not device.connected:
			return 'switch_offline.png'

		if device.getCustomValue('on'):
			return 'switch_on.png'
		else:
			return 'switch_off.png'


	def getDeviceConfig(self):
		# return the custom configuration of that deviceType
		pass


	def toggle(self, device: Device):
		# todo toggle switch?
		pass
