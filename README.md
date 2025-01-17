[![Generic badge](https://img.shields.io/badge/HACS-Custom-3498db.svg)](https://github.com/hacs/integration)
[![Generic badge](https://img.shields.io/github/commit-activity/y/grimmpp/home-assistant-eltako.svg?style=flat&color=3498db)](https://github.com/grimmpp/home-assistant-eltako/commits/main)
[![Generic badge](https://img.shields.io/badge/Community-Forum-3498db.svg)](https://community.home-assistant.io/)
[![Generic badge](https://img.shields.io/badge/Community_Forum-Eltako_Integration_Debugging-3498db.svg)](https://community.home-assistant.io/t/eltako-baureihe-14-rs485-enocean-debugging/49712)
[![Generic badge](https://img.shields.io/badge/License-MIT-3498db.svg)](/LICENSE)
[![Generic badge](https://img.shields.io/badge/SUPPORT_THIS_PROJECT-PayPal.me-27ae60.svg)](https://paypal.me/grimmpp)

# Eltako Bus Integration (RS485 - EnOcean) for Home Assistant

This repo contains an Home Assistant Integration for Eltako Baureihe 14. 
This integration allows you to get all information of the Eltako 14 Bus and it allows you to control all the devices via Home Assistant. (See supported devices.) You can also react on sensors like weather station, rocker switches, window contacts ... with automations in Home Assistant.

For more details check out the provided [docs](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs) and links listed at the end.
Check out the [example configuration](https://github.com/grimmpp/home-assistant-eltako/tree/main/ha.yaml). (It gets verifided by an unit test and should not be outdated.)

# Supported EEPs and devices

The following EnOcean Equipment Profiles (EEPs) and devices are currently supported. In general, this is not limited to Eltako devices, mainly to the EnOcean standard. 
Elatko devices are exemplarily mentioned. You can find [here](https://www.eltako.com/fileadmin/downloads/de/Gesamtkatalog/Eltako_Gesamtkatalog_KapT_low_res.pdf) a nice overview about which EEPs are provided/required by which Eltako devices.

**Supported sensor EEPs**
* Binary sensor
  * F6-02-01 ([Rocker switch](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/rocker_switch/readme.md), FTS14EM)
  * F6-02-02 ([Rocker switch](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/rocker_switch/readme.md))
  * F6-10-00 (Window handle, FTS14EM)
  * D5-00-01 (Contact sensor, FTS14EM) incl. signal inverter
  * A5-08-01 (Occupancy sensor, FTS14EM)
* Sensor
  * A5-04-02 (Temperature and Humidity Sensor, FLGTF, FLT58)
  * A5-09-0C (Air Quality / VOC⁠ (Volatile Organic Compounds) e.g. [FLGTF](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/flgtf_temp_humidity_air_quality/readme.md))
  * A5-10-06 (Temperature Sensor and Controller e.g. FUTH)
  * A5-10-12 (Temperature Sensor and Controller and Humidity Sensor e.g. FUTH)
  * A5-12-01 (Automated meter reading - electricity, FSDG14)
  * A5-12-02 (Automated meter reading - gas, F3Z14D)
  * A5-12-03 (Automated meter reading - water, F3Z14D)
  * A5-13-01 (Weather station, FWG14)
  * F6-10-00 (Window handle, FTS14EM)
* Light
  * A5-38-08 (Central command - gateway, FUD14)
  * M5-38-08 (Eltako relay, FSR14)
* Switch
  * M5-38-08 (Eltako relay, FSR14)
* Cover
  * G5-3F-7F (Eltako cover, FSB14)

**Supported sender EEPs**
* Light
  * A5-38-08 (Central command - gateway, FUD14)
* [Switch](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/rocker_switch/readme.md)
  * F6-02-01 (Rocker switch)
* Cover
  * H5-3F-7F (Eltako cover, FSB14)
* [Climate](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/heating-and-cooling/readme.md) (**Experimental** - Not properly test. Interaction and synchronization of temperature controllers may change.)
  * A5-10-06 (Eltako FAE14, FHK14, F4HK14, F2L14, FHK61, FME14)
 
[**Gateway**](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/gateways/readme.md) (See also [multiple gateway support](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/multiple-gateway-support/readme.md))
  * **Eltako FAM14** and Eltako **FGW14-USB** (based on ESP2, rs485 bus and baud rate 57600, uses library [eltako14bus](https://github.com/grimmpp/eltako14bus)) 
  * **Eltako FAM-USB** (based on ESP2, baud rate 9600, uses library [eltako14bus](https://github.com/grimmpp/eltako14bus)) 
  * **EnOcean USB300** (**NOT YET IMPLEMENTED**) (based on ESP3 and baud rate 57600, uses library [Python EnOcean](https://github.com/kipe/enocean))
    * Library is integrated and USB300 can be configured. Message conversion from ESP3 to ESp2 and back is not yet implemented. This means this dongle is not yet working.


# Installation and Configuration

While this is not integrated into home assistant's repositories. You need to install first [Home Assistant Commuinty Sore (HACS)](https://hacs.xyz/) in order to install custom components. After that you need to do the following steps:
1. **Install repo via HACS**: 
  
   Click on the button below to automatically navigate to the repository within HACS, add and download it.

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=grimmpp&repository=home-assistant-eltako&category=integration)
   
   *Alternative1:* Simply enter the URL of this repo. It will then be listed in HACS and also shows when new updates are available. [Detailed Docs in HACS Custom Repositories](https://hacs.xyz/docs/faq/custom_repositories/)

   *Alternative 2:* Copying directory ``eltako``** from this repository into your home assistant's ``/config/custom_components`` directory.
   For easy installation just clone this repository ``git clone https://github.com/grimmpp/home-assistant-eltako.git`` and execute the installation script of this repo ``./install_custom_component_eltako.sh``. 
4. To **enable this component**, go to your integrations, press the "add" button and select "Eltako". In the presented sheet either select the detected USB gateway or enter the path manually.
5. **Update Home Assistant configuration** ``/config/configuration.yaml`` and add all devices and sensors you want to integrate. See [How to update Home Assistant Configuration](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/update_home_assistant_configuration.md) to see how the configuration should look like. 
There is also a scipt which can detect devices and sensors and creates a prepared configuration because in big setups it can be a little effort doing that manually. For more details have a look into [Device and Sensor Discovery for Home Assistant Configuration](https://github.com/grimmpp/home-assistant-eltako/tree/main/eltakodevice_discovery/)

# Testing

Testing this integration via Home Assistant development container or updating it in a Home Assistant instance is quite time consuming. Therefore I've added some basic tests to ensure quickly a base quality. 

Unit and component tests for this integration are located in the folder tests. There is already a vscode settings.json prepared to start them via vscode or you can just run the following command from the repo folder.

```
python -m unittest discover tests -v
```

# Documentation
* [Create Home Assistant Configuration File for Eltako Integration](https://github.com/grimmpp/home-assistant-eltako/tree/main/eltakodevice_discovery/)
* [Eltako Home Automation](https://github.com/cvanlabe/Eltako-home-automation) from [Cedric Van Labeke](https://github.com/cvanlabe)
* [Simple Eltako Setup](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/simple_eltako_setup.md)
* [How to detect Switch Signals and react on thoese in Home Assistant](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/rocker_switch/readme.md)
* [How to configure heating and cooling](https://github.com/grimmpp/home-assistant-eltako/tree/main/docs/heating-and-cooling/readme.md)


# Dependencies
* [Eltako Software PCT14](https://www.eltako.com/en/software-pct14/) for programming and configuring Eltako Baureihe 14 devices natively.
* [Home Assistant Community Store](https://hacs.xyz/) is needed to be able to install this repository. It allows you to install custom_components.
* [Eltako14Bus Python Library](https://github.com/grimmpp/eltako14bus) is used by Home Assistant Eltako Integration for serial communication for device Eltako FAM14 and FGW14-USB.
* [Python EnOcean](https://github.com/kipe/enocean) is used by Home Assistant Eltako Integration for serial communication for device USB300.


# Useful Home Assistant Addons
* [File Editor](https://github.com/home-assistant/addons/tree/master/configurator)
* [Log Viewer](https://github.com/hassio-addons/addon-log-viewer)
* [Terminal & SSH](https://github.com/home-assistant/addons/tree/master/ssh)
* [Studio Code Server](https://github.com/hassio-addons/addon-vscode)


# External Documentation
* [Full setup journey and automation project with Eltako](https://github.com/cvanlabe/Eltako-home-automation/tree/main) from [Cedric Van Labeke](https://github.com/cvanlabe) **RECOMMENDED!!!**
* [Home Assistant Developer Docs](https://developers.home-assistant.io/)
* [EnOcean Equipment Profiles - EEP2.1](https://www.trio2sys.fr/images/media/EnOcean_Equipment_Profiles_EEP2.1.pdf)
* [EnOcean Equipment Profiles - EEP v2.6.7](https://www.enocean-alliance.org/wp-content/uploads/2017/05/EnOcean_Equipment_Profiles_EEP_v2.6.7_public.pdf)
* [Eltako Technical Specification of Devices](https://www.eltako.com/fileadmin/downloads/de/Gesamtkatalog/Eltako_Gesamtkatalog_KapT_low_res.pdf) contains as well mapping of EEPs to devices
* [OpenHAB Binding for EnOcean/Binding](https://github.com/fruggy83/openocean)

# Credits
Credits for this code goes to [chrysn](https://gitlab.com/chrysn) and [Johannes Bosecker](https://github.com/JBosecker) who initiated and made this code publicly available on their Gitlab repos, and shared it in the Home Assistant community ([Eltako “Baureihe 14 – RS485” (Enocean) Debugging](https://community.home-assistant.io/t/eltako-baureihe-14-rs485-enocean-debugging/49712)). Because of many many changes to the original repository the fork was decoupled. <br/>
Big thanks as well to [Cedric Van Labeke](https://github.com/cvanlabe) who provides a very good [documentation](https://github.com/cvanlabe/Eltako-home-automation/tree/main) and helped me to make my first steps into this world.
