Home Automation integration server that provides status information for devices
=========================================

This server listens to ISY events and updates an AWS DynamoDB database with their
status.  An Alexa Skill then queries that database to allow voice retrieval of the
state of those devices.

##### Current Devices Supported
- Lights/Lamps
- Fans
