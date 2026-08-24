# Teltonika Telematics Tracker 
Home Assistant Integration of Teltonika Telematics Tracker ([more info](https://www.teltonika-gps.com/)) using UDP and Teltonika [Codec8](https://wiki.teltonika-gps.com/view/Codec).

## Configuration
When unsing this integration, you need specify a port for the UDP-Server. This port needs to be reachable for the tracker. 

You need to configure the tracker to use your Home Assistant installation with the specified port as endpoint for the datagrams.

If a datagram is send to the integration from an unknown tracker, the Integration will create this tracker in Home Assistant. 

## Trademark Notice
Teltonika and the Teltonika logo are trademarks of Teltonika.

The Teltonika logo included in this repository is used solely to identify
compatibility with Teltonika products. This project is independent and is
not affiliated with, sponsored by, or endorsed by Teltonika.

The Teltonika logo and other Teltonika brand assets are not licensed under
the Apache License 2.0 applicable to this project's source code.
