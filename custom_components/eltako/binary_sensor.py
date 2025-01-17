"""Support for Eltako binary sensors."""
from __future__ import annotations

from eltakobus.util import AddressExpression, b2a
from eltakobus.eep import *

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant import config_entries
from homeassistant.const import *
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import ConfigType

from .device import *
from .const import *
from .gateway import EnOceanGateway
from .schema import CONF_EEP_SUPPORTED_BINARY_SENSOR
from . import config_helpers, get_gateway_from_hass, get_device_config_for_gateway

import json

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Binary Sensor platform for Eltako."""
    gateway: EnOceanGateway = get_gateway_from_hass(hass, config_entry)
    config: ConfigType = get_device_config_for_gateway(hass, config_entry, gateway)
    
    entities: list[EltakoEntity] = []
    
    platform = Platform.BINARY_SENSOR

    for platform in [Platform.BINARY_SENSOR, Platform.SENSOR]:
        if platform in config:
            for entity_config in config[platform]:
                try:
                    dev_conf = config_helpers.DeviceConf(entity_config, [CONF_DEVICE_CLASS, CONF_INVERT_SIGNAL])
                    if dev_conf.eep.eep_string in CONF_EEP_SUPPORTED_BINARY_SENSOR:
                        entities.append(EltakoBinarySensor(platform, gateway, dev_conf.id, dev_conf.name, dev_conf.eep, 
                                                        dev_conf.get(CONF_DEVICE_CLASS), dev_conf.get(CONF_INVERT_SIGNAL)))

                except Exception as e:
                            LOGGER.warning("[%s] Could not load configuration", platform)
                            LOGGER.critical(e, exc_info=True)

    # dev_id validation not possible because there can be bus sensors as well as decentralized sensors.
    log_entities_to_be_added(entities, platform)
    async_add_entities(entities)
    

class EltakoBinarySensor(EltakoEntity, BinarySensorEntity):
    """Representation of Eltako binary sensors such as wall switches.

    Supported EEPs (EnOcean Equipment Profiles):
    - F6-02-01 (Light and Blind Control - Application Style 2)
    - F6-02-02 (Light and Blind Control - Application Style 1)
    - F6-10-00
    - D5-00-01
    """

    def __init__(self, platform: str, gateway: EnOceanGateway, dev_id: AddressExpression, dev_name:str, dev_eep: EEP, device_class: str, invert_signal: bool):
        """Initialize the Eltako binary sensor."""
        super().__init__(platform, gateway, dev_id, dev_name, dev_eep)
        self.invert_signal = invert_signal
        self._attr_device_class = device_class

    @property
    def last_received_signal(self):
        """Return timestamp of last received signal."""
        return self._attr_last_received_signal
    
    @property
    def data(self):
        """Return telegram data for rocker switch."""
        return self._attr_data

    def value_changed(self, msg: Regular4BSMessage):
        """Fire an event with the data that have changed.

        This method is called when there is an incoming message associated
        with this platform.

        Example message data:
        - 2nd button pressed
            ['0xf6', '0x10', '0x00', '0x2d', '0xcf', '0x45', '0x30']
        - button released
            ['0xf6', '0x00', '0x00', '0x2d', '0xcf', '0x45', '0x20']
        """
        
        try:
            decoded = self.dev_eep.decode_message(msg)
            LOGGER.debug("decoded : %s", json.dumps(decoded.__dict__))
            # LOGGER.debug("msg : %s, data: %s", type(msg), msg.data)
        except Exception as e:
            LOGGER.warning("[Binary Sensor] Could not decode message: %s", str(e))
            return

        if self.dev_eep in [F6_02_01, F6_02_02]:
            pressed_buttons = []
            pressed = decoded.energy_bow == 1
            two_buttons_pressed = decoded.second_action == 1
            fa = decoded.rocker_first_action
            sa = decoded.rocker_second_action

            # Data is only available when button is pressed. 
            # Button cannot be identified when releasing it.
            # if at least one button is pressed
            if pressed:
                if fa == 0:
                    pressed_buttons += ["LB"]
                if fa == 1:
                    pressed_buttons += ["LT"]
                if fa == 2:
                    pressed_buttons += ["RB"]
                if fa == 3:
                    pressed_buttons += ["RT"]
            if two_buttons_pressed:
                if sa == 0:
                    pressed_buttons += ["LB"]
                if sa == 1:
                    pressed_buttons += ["LT"]
                if sa == 2:
                    pressed_buttons += ["RB"]
                if sa == 3:
                    pressed_buttons += ["RT"]
            else:
                # button released but no detailed information available
                pass

            switch_address = config_helpers.format_address((msg.address, None))
            event_id = config_helpers.get_bus_event_type(self.gateway.dev_id, EVENT_BUTTON_PRESSED, AddressExpression((msg.address, None)))
            event_data = {
                    "id": event_id,
                    "data": int.from_bytes(msg.data, "big"),
                    "switch_address": switch_address,
                    "pressed_buttons": pressed_buttons,
                    "pressed": pressed,
                    "two_buttons_pressed": two_buttons_pressed,
                    "rocker_first_action": decoded.rocker_first_action,
                    "rocker_second_action": decoded.rocker_second_action,
                }
            
            LOGGER.debug("[Binary Sensor] Send event: %s, pressed_buttons: '%s'", event_id, json.dumps(pressed_buttons))
            self.hass.bus.fire(event_id, event_data)

            event_id = config_helpers.get_bus_event_type(self.gateway.dev_id, EVENT_BUTTON_PRESSED, AddressExpression((msg.address, None)), '-'.join(pressed_buttons))
            event_data = {
                    "id": event_id,
                    "data": int.from_bytes(msg.data, "big"),
                    "switch_address": switch_address,
                    "pressed_buttons": pressed_buttons,
                    "pressed": pressed,
                    "two_buttons_pressed": two_buttons_pressed,
                    "rocker_first_action": decoded.rocker_first_action,
                    "rocker_second_action": decoded.rocker_second_action,
                }
            LOGGER.debug("[Binary Sensor] Send event: %s, pressed_buttons: '%s'", event_id, json.dumps(pressed_buttons))
            self.hass.bus.fire(event_id, event_data)

            return
        elif self.dev_eep in [F6_10_00]:
            action = (decoded.movement & 0x70) >> 4
            
            if action == 0x07:
                self._attr_is_on = False
            elif action in (0x04, 0x06):
                self._attr_is_on = False
            else:
                return

        elif self.dev_eep in [D5_00_01]:
            # learn button: 0=pressed, 1=not pressed
            if decoded.learn_button == 0:
                return
            
            # contact: 0=open, 1=closed
            if not self.invert_signal:
                self._attr_is_on = decoded.contact == 0
            else:
                self._attr_is_on = decoded.contact == 1

        elif self.dev_eep in [A5_08_01]:
            if decoded.learn_button == 1:
                return
                
            self._attr_is_on = decoded.pir_status == 1

        elif self.dev_eep in [A5_07_01]:

            self._attr_is_on = decoded.pir_status_on == 1

        else:
            return
        
        if self.is_on:
            switch_address = config_helpers.format_address((msg.address, None))
            event_id = config_helpers.get_bus_event_type(self.gateway.base_id, EVENT_CONTACT_CLOSED, AddressExpression((msg.address, None)))
            self.hass.bus.fire(
                event_id,
                {
                    "id": event_id,
                    "contact_address": switch_address,
                },
            )

        self.schedule_update_ha_state()

