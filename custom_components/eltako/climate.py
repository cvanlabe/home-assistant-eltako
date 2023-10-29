"""Support for Eltako Temperature Control sources."""
from __future__ import annotations

import math
from typing import Any

import asyncio
import time

from eltakobus.util import AddressExpression
from eltakobus.eep import *

from homeassistant.components.climate import (
    ClimateEntity,
    HVACAction,
    HVACMode,
    ClimateEntityFeature
)
from homeassistant import config_entries
from homeassistant.const import CONF_ID, CONF_NAME, Platform, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .device import EltakoEntity
from .const import CONF_ID_REGEX, CONF_EEP, CONF_SENDER, DOMAIN, MANUFACTURER, DATA_ELTAKO, ELTAKO_CONFIG, ELTAKO_GATEWAY, LOGGER


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Eltako Temperature Control platform."""
    config: ConfigType = hass.data[DATA_ELTAKO][ELTAKO_CONFIG]
    gateway = hass.data[DATA_ELTAKO][ELTAKO_GATEWAY]

    entities: list[EltakoSensor] = []
    
    if Platform.CLIMATE in config:
        for entity_config in config[Platform.CLIMATE]:
            dev_id = AddressExpression.parse(entity_config.get(CONF_ID))
            dev_name = entity_config.get(CONF_NAME)
            eep_string = entity_config.get(CONF_EEP)
            
            sender_config = entity_config.get(CONF_SENDER)
            sender_id = AddressExpression.parse(sender_config.get(CONF_ID))
            sender_eep_string = sender_config.get(CONF_EEP)

            try:
                dev_eep = EEP.find(eep_string)
                sender_eep = EEP.find(sender_eep_string)
            except Exception as e:
                LOGGER.warning("Could not find EEP %s for device with address %s", eep_string, dev_id.plain_address())
                LOGGER.critical(e, exc_info=True)
                continue
            else:
                if dev_eep in [A5_10_06]:
                    entities.append(ClimateController(gateway, dev_id, dev_name, dev_eep, sender_id, sender_eep))
        
    for e in entities:
        LOGGER.debug(f"Add entity {e.dev_name} (id: {e.dev_id}, eep: {e.dev_eep}) of platform type {Platform.CLIMATE} to Home Assistant.")
    async_add_entities(entities)


async def _loop_send_command(cc: ClimateController):
    while(True):
        time.sleep(50)  # wait 50 seconds

        LOGGER.debug("Automatic status update:")
        mode = cc._get_mode_by_hvac(cc.hvac_action, cc.hvac_mode)
        temp = cc.target_temperature
        cc._send_command(mode, temp)

class ClimateController(EltakoEntity, ClimateEntity):
    """Representation of an Eltako heating and cooling actor."""

    _update_frequency = 10 # sec

    _attr_hvac_action = HVACAction.OFF
    _attr_hvac_mode = HVACMode.HEAT
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.COOL, HVACMode.OFF]
    _attr_fan_mode = None
    _attr_fan_modes = None
    _attr_is_aux_heat = None
    _attr_preset_mode = None
    _attr_preset_modes = None
    _attr_swing_mode = None
    _attr_swing_modes = None
    _attr_target_temperature = 0
    _attr_target_temperature_high = 25
    _attr_target_temperature_low = 8
    _attr_max_temp = 25
    _attr_min_temp = 8
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(self, gateway, dev_id, dev_name, dev_eep, sender_id, sender_eep):
        """Initialize the Eltako heating and cooling source."""
        super().__init__(gateway, dev_id, dev_name)
        self.dev_eep = dev_eep
        self._on_state = False
        self._sender_id = sender_id
        self._sender_eep = sender_eep
        self._attr_unique_id = f"{DOMAIN}_{dev_id.plain_address().hex()}"
        self.entity_id = f"climate.{self.unique_id}"

        self._loop = asyncio.get_event_loop()
        self._update_task = asyncio.ensure_future(self._wrapped_update(), loop=self._loop)


    async def _wrapped_update(self, *args):
        while True:
            try:
                LOGGER.debug(f"update loop wait {self._update_frequency} sec")
                await asyncio.sleep(self._update_frequency)
                
                LOGGER.debug(f"Send status every {self._update_frequency} sec.:")
                mode = self._get_mode_by_hvac(self.hvac_action, self.hvac_mode)
                await self._async_send_command(mode, self.target_temperature)
            except Exception as e:
                LOGGER.exception(e)
                # FIXME should I just restart with back-off?


    @property
    def name(self):
        """Return the name of the device if any."""
        return None

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self.dev_id.plain_address().hex())
            },
            name=self.dev_name,
            manufacturer=MANUFACTURER,
            model=self.dev_eep.eep_string,
            via_device=(DOMAIN, self.gateway.unique_id),
        )
    

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        LOGGER.info("async func")
        LOGGER.info(f"hvac_mode {hvac_mode}")
        LOGGER.info(f"self.hvac_mode {self.hvac_mode}")
        LOGGER.info(f"target temp {self.target_temperature}")
        LOGGER.info(f"current temp {self.current_temperature}")

        if hvac_mode == HVACMode.OFF:
            if hvac_mode != self.hvac_mode:
                self._send_mode_off()
                #self._send_command(A5_10_06.Heater_Mode.OFF, self.target_temperature)
            else:
                self._send_set_normal_mode()
                self._send_command(A5_10_06.Heater_Mode.NORMAL, self.target_temperature)


    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        LOGGER.info("async func")
        LOGGER.info(f"hvac_mode {self.hvac_mode}")
        LOGGER.info(f"hvac_action {self.hvac_action}")
        LOGGER.info(f"target temp {self.target_temperature}")
        LOGGER.info(f"current temp {self.current_temperature}")
        LOGGER.info(f"kwargs {kwargs}")
        new_target_temp = kwargs['temperature']

        self._send_command(A5_10_06.Heater_Mode.NORMAL, new_target_temp)
    

    def _send_command(self, mode: A5_10_06.Heater_Mode, target_temp: float) -> None:
        address, _ = self._sender_id
        if self._sender_eep == A5_10_06:
            msg = A5_10_06(mode, target_temp, self.current_temperature, self.hvac_action == HVACAction.IDLE).encode_message(address)
            self.send_message(msg)


    def _send_set_normal_mode(self):
        self.send_message(RPSMessage(self._sender_id, 0x30, b'\x70', True))

    def _send_mode_off(self):
        self.send_message(RPSMessage(self._sender_id, 0x30, b'\x10', True))

    async def _async_send_command(self, mode: A5_10_06.Heater_Mode, target_temp: float) -> None:
        self._send_command(mode, target_temp)


    def _get_mode_by_hvac(self, hvac_action: HVACAction, hvac_mode: HVACMode) -> A5_10_06.Heater_Mode:
        mode = A5_10_06.Heater_Mode.OFF
        if hvac_action == HVACAction.HEATING or hvac_action == HVACAction.COOLING:
            mode = A5_10_06.Heater_Mode.NORMAL
        elif hvac_action == HVACAction.IDLE:
            mode = A5_10_06.Heater_Mode.STAND_BY_2_DEGREES

        if hvac_mode == HVACMode.OFF:
            mode = A5_10_06.Heater_Mode.OFF

        return mode
    

    def value_changed(self, msg):
        """Update the internal state of this device."""
        try:
            if msg.org == 0x07:
                decoded = self.dev_eep.decode_message(msg)
        except Exception as e:
            LOGGER.warning("Could not decode message: %s", str(e))
            return

        if  msg.org == 0x07 and self.dev_eep in [A5_10_06]:
            
            
            if decoded.mode == A5_10_06.Heater_Mode.OFF:
                self._attr_hvac_mode = HVACMode.OFF
                self._attr_hvac_action = HVACAction.OFF
            elif decoded.mode == A5_10_06.Heater_Mode.NORMAL:
                self._attr_hvac_mode = HVACMode.HEAT
                self._attr_hvac_action = HVACAction.HEATING
            elif decoded.mode == A5_10_06.Heater_Mode.STAND_BY_2_DEGREES:
                self._attr_hvac_mode = HVACMode.HEAT
                self._attr_hvac_action = HVACAction.IDLE

            if decoded.mode != A5_10_06.Heater_Mode.OFF:
                self._attr_target_temperature = decoded.target_temp

            self._attr_current_temperature = decoded.current_temp

        self.schedule_update_ha_state()
