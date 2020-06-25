import sqlite3

from core.device.model.Device import Device
from core.device.model.DeviceException import RequiresWIFISettings
from core.device.model.DeviceType import DeviceType
from core.dialog.model.DialogSession import DialogSession


class EspPir(DeviceType):
	ESPTYPE = 'pir'


	def __init__(self, data: sqlite3.Row):
		super().__init__(data, devSettings=self.DEV_SETTINGS, locSettings=self.LOC_SETTINGS, heartbeatRate=600)


	def discover(self, device: Device, uid: str, replyOnSiteId: str = '', session: DialogSession = None) -> bool:
		if not self.ConfigManager.getAliceConfigByName('ssid'):
			raise RequiresWIFISettings()

		return self.parentSkillInstance.startTasmotaFlashingProcess(device, replyOnSiteId, session)


	def getDeviceIcon(self, device: Device) -> str:
		if not device.uid:
			return 'EspPir.png'
		if not device.connected:
			return 'PIR_offline.png'
		if device.getCustomValue('disabled'): # TODO please implement "disabled" status - I don't own a PIR
			return 'PIR_disabled.png'
		if device.getCustomValue('cooldown'): # TODO please implement some kind of cooldown so you can see recent acivities
			return 'PIR_justActivated.png'
		return 'EspPir.png'


	def toggle(self, device: Device):
		pass # Implement me
