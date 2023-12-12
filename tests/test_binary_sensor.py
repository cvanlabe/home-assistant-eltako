import unittest
from mocks import *
from unittest import mock
from homeassistant.helpers.entity import Entity
from custom_components.eltako.binary_sensor import EltakoBinarySensor
from eltakobus import *

# mock update of Home Assistant
Entity.schedule_update_ha_state = mock.Mock(return_value=None)
# EltakoBinarySensor.hass.bus.fire is mocked by class HassMock


class TestBinarySensor(unittest.TestCase):

    def create_binary_sensor(self, eep_string:str="F6-02-01", device_class = "none", invert_signal:bool=False) -> EltakoBinarySensor:
        gateway = GatewayMock()
        dev_id = AddressExpression.parse("00-00-00-01")
        dev_name = "device name"
        
        dev_eep = EEP.find(eep_string)

        bs = EltakoBinarySensor(gateway, dev_id, dev_name, dev_eep, device_class, invert_signal)
        bs.hass = HassMock()
        self.assertEqual(bs._attr_is_on, None)     

        return bs

    def test_binary_sensor_rocker_switch(self):
        bs = self.create_binary_sensor()
        
        switch_address = b'\xfe\xdb\xb6\x40'
        msg = RPSMessage(switch_address, status=b'\x30', data=b'\x70')
                
        bs.value_changed(msg)
        
        # test if processing was finished and event arrived on bus
        self.assertEqual(len(bs.hass.bus.fired_events), 2)

        # check event type
        fired_event_0 = bs.hass.bus.fired_events[0]
        self.assertEqual(fired_event_0['event_type'], 'eltako.gw_FF-AA-80-00.btn_pressed.sid_FE-DB-B6-40')

        fired_event_1 = bs.hass.bus.fired_events[1]
        self.assertEqual(fired_event_1['event_type'], 'eltako.gw_FF-AA-80-00.btn_pressed.sid_FE-DB-B6-40.d_RT')

        # check event data
        exprected_data = {
            'id': 'eltako.gw_FF-AA-80-00.btn_pressed.sid_FE-DB-B6-40', 
            "data": 112,
            'switch_address': 'FE-DB-B6-40', 
            'pressed_buttons': ['RT'], 
            'pressed': True, 
            'two_buttons_pressed': False, 
            'rocker_first_action': 3, 
            'rocker_second_action': 0
        }
        self.assertEqual(fired_event_0['event_data'], exprected_data)


    def test_binary_sensor_window_contact_triggered_via_FTS14EM(self):
        bs = self.create_binary_sensor(eep_string="D5-00-01", device_class = "window", invert_signal =  True)

        # test if sensor object is newly created
        self.assertEqual(bs._attr_is_on, None)       
        
        # test if state is set to no contact
        bs._attr_is_on = False
        self.assertEqual(bs._attr_is_on, False)

        msg = Regular1BSMessage(address=b'\x00\x00\x10\x08', data=b'\x09', status=b'\x00')
        
        # test if signal is processed correctly (switch on)
        bs.value_changed(msg)
        self.assertEqual(bs._attr_is_on, True)

        # test if signal is processed correctly (switch on)
        bs.value_changed(msg)
        self.assertEqual(bs._attr_is_on, True)

        # test if signal is processed correctly (switch off)
        msg.data = b'\x08'
        bs.value_changed(msg)
        self.assertEqual(bs._attr_is_on, False)

        # test if signal is processed correctly (switch off)
        bs.value_changed(msg)
        self.assertEqual(bs._attr_is_on, False)