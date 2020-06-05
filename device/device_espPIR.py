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


class device_espPIR(DeviceType):

	DEV_SETTINGS = ""
	LOC_SETTINGS = ""
	ESPTYPE = "pir"

	def __init__(self, data: sqlite3.Row):
		super().__init__(data, self.DEV_SETTINGS, self.LOC_SETTINGS)


	def discover(self, device: Device, uid: str, replyOnSiteId: str = "", session:DialogSession = None) -> bool:
		if not self.getAliceConfig('ssid'):
			raise requiresWIFISettings()

		self.parentSkillInstance.startTasmotaFlashingProcess(device, uid, replyOnSiteId, session)
		pass


	def getDeviceIcon(self, device: Device) -> str:
		if not device.uid:
			return 'device_espPIR.png'
		if not device.connected:
			return 'PIR_offline.png'
		if device.getCustomValue('disabled'):
			return 'PIR_disabled.png'
		if device.getCustomValue('cooldown'):
			return 'PIR_justActivated.png'
		if not device.uid:
			return 'device_espPIR.png'
		return 'device_espPIR.png'


	def getDeviceConfig(self):
		# return the custom configuration of that deviceType
		pass


	def toggle(self, device: Device):
		# todo enable/disable sensor?
		pass
