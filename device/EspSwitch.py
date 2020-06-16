import sqlite3

from core.device.model.Device import Device
from core.device.model.DeviceException import RequiresWIFISettings
from core.device.model.DeviceType import DeviceType
from core.dialog.model.DialogSession import DialogSession


class EspSwitch(DeviceType):
	ESPTYPE = 'switch'


	def __init__(self, data: sqlite3.Row):
		super().__init__(data, devSettings=self.DEV_SETTINGS, locSettings=self.LOC_SETTINGS, heartbeatRate=600)


	def discover(self, device: Device, replyOnSiteId: str = '', session: DialogSession = None) -> bool:
		if not self.ConfigManager.getAliceConfigByName('ssid'):
			raise RequiresWIFISettings()

		return self.parentSkillInstance.startTasmotaFlashingProcess(device, replyOnSiteId, session)


	def getDeviceIcon(self, device: Device) -> str:
		if not device.uid:
			return 'EspSwitch.png'
		if not device.connected:
			return 'switch_offline.png'

		if device.getCustomValue('on'):
			return 'switch_on.png'
		else:
			return 'switch_off.png'


	def getDeviceConfig(self):
		pass # TODO return the custom configuration of that deviceType


	def toggle(self, device: Device):
		pass # TODO toggle switch?
