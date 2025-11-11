
"""
IPE Logger Message ID Constants
===============================

This module contains all IPE logger message ID constants used for log analysis.
These IDs correspond to specific events, errors, and system messages in IPEmotion RT logs.

Author: LogFileAnalyzerV2 Team
Version: 3.0.0
Date: November 2025
"""

from enum import IntEnum

from enum import IntEnum

class LoggerMessageId(IntEnum):
    MSG_0000000F = 0x0000000F  # The free measurement space of the RAW partition including the info about the taotal space on RAW / Free measurement space: 3519 / 3534 MB
    MSG_00000011 = 0x00000011  # "Measurement files are existing in the fallback folder
    MSG_00000012 = 0x00000012  # All jobs are finished. There might be more then one, e.g. USB Stick download data and update config etc... / Jobs finished
    MSG_00000013 = 0x00000013  # Logger configuration update / Update complete
    MSG_00000014 = 0x00000014  # Program update complete: %s
    MSG_00000015 = 0x00000015  # USB stick with label 'STICK' for configuration update / image update / data download  connected / USB Stick connected
    MSG_00000016 = 0x00000016  # USB stick with label 'STICK' disconnected / USB Stick disconnected
    MSG_00000019 = 0x00000019  # Copy log file
    MSG_0000001A = 0x0000001A  # Start data transfer
    MSG_0000001C = 0x0000001C  # Start time update
    MSG_0000001F = 0x0000001F  # Time update finished
    MSG_00000020 = 0x00000020  # Data transfer finished
    MSG_00000023 = 0x00000023  # Time update failed
    MSG_00000024 = 0x00000024  # Data transfer failed
    MSG_00000026 = 0x00000026  # Cyclic info about measurement space (only in diagnostics mode) / Measurement space: ...
    MSG_00000027 = 0x00000027  # Cyclic info about estimated left measurement time (only in diagnostics mode) / Time Left: ...
    MSG_00000028 = 0x00000028  # Total disk space of partition with raw data / Total disk space XXXX MB
    MSG_0000002F = 0x0000002F  # generating upload file
    MSG_00000035 = 0x00000035  # ModemManager: PUK is required
    MSG_0000003D = 0x0000003D  # FTP connection established. Using <mode>!lf!with <mode>!lf!- active mode!lf!- passive mode / FTP connection established. Using <mode>
    MSG_00000043 = 0x00000043  # Start Mail
    MSG_00000044 = 0x00000044  # USB stick needs to be unplugged to reboot the logger / Unplug USB Stick to reboot
    MSG_00000047 = 0x00000047  # Mail finished
    MSG_00000048 = 0x00000048  # Mail failed
    MSG_0000004C = 0x0000004C  # USB peripheral mode is activated
    MSG_0000004D = 0x0000004D  # USB peripheral mode is disabled
    MSG_000003E9 = 0x000003E9  # IPEmotionRT-Version on the logger / *************** IPEmotionRT XXXX RX.xxxxx**************
    MSG_000003EA = 0x000003EA  # Serial number from the Logger / Serial number: 8XXXXXX
    MSG_000003EF = 0x000003EF  # Hw revision of the logger / Hw revision: XX.YY
    MSG_000003F0 = 0x000003F0  # Production date of the logger / Production date: MM/DD/YYYY
    MSG_000003F6 = 0x000003F6  # Calibration date of the logger / Calibration date: MM/DD/YYYY
    MSG_000003F7 = 0x000003F7  # About new images / New program found: bzImage.fwc
    MSG_000003F8 = 0x000003F8  # Try to continue measurement
    MSG_000003F9 = 0x000003F9  # Start date time / StartDateTime: XX:XX:XX:000000
    MSG_000003FA = 0x000003FA  # Stop date time / StopDateTime: XX:XX:XX:000000
    MSG_000003FB = 0x000003FB  # Firmware update running
    MSG_000003FC = 0x000003FC  # Time zone / (GMT) Coordinated Universal Time
    MSG_000003FD = 0x000003FD  # Data recording delay: x s
    MSG_000003FE = 0x000003FE  # The firmware update has finished / Firmware update done
    MSG_000003FF = 0x000003FF  # Exception occurred TODO: spelling OCCURRED
    MSG_00000401 = 0x00000401  # Copying and compressing files ... / Copying and compressing files before XXXX
    MSG_00000402 = 0x00000402  # Copying files... / Copying files before XXXX
    MSG_00000403 = 0x00000403  # Files ready... / Files ready before XXXX
    MSG_00000404 = 0x00000404  # USBControl : Rescue configuration found
    MSG_00000405 = 0x00000405  # The current setup might overload the logger type used.
    MSG_00000406 = 0x00000406  # iDDS
    MSG_00000407 = 0x00000407  # The user disabled the data transfer job.
    MSG_00000451 = 0x00000451  # Post processing is running
    MSG_0000045A = 0x0000045A  # The version of the configuration is too new. Please perform an image update
    MSG_0000045B = 0x0000045B  # License missing
    MSG_0000045C = 0x0000045C  # Version too old
    MSG_0000045D = 0x0000045D  # What kind of license is missing:!lf!with <TYPE>:!lf!- Storage groups unlimited!lf!- Protocols!lf!- Communication!lf!- Multimedia!lf!- Comfort Display!lf!- Control!lf!- Bus interface extension!lf!- SKB!lf!- Modbus / License missing: <TYPE>
    MSG_0000045E = 0x0000045E  # FTP: Unable to connect to IP address <IP>. Reported error: <ERR>
    MSG_00000460 = 0x00000460  # Messages from measurement kernel / <MESSAGE>
    MSG_00000461 = 0x00000461  # Messages in limit configuration configured by user / <MESSAGE>
    MSG_00000462 = 0x00000462  # <SEQUENCENAME>: The sequence was stopped due to <REASON> (Step: %u  Loop: %u Time: %lf)!lf!with <REASON>:!lf!- an error!lf!- to the stop trigger condition / <SEQUENCENAME>: The sequence was stopped due to <REASON> (Step: %u  Loop: %u Time: %lf)
    MSG_00000463 = 0x00000463  # Storage: A file split was triggered due to a buffer overrun.
    MSG_00000465 = 0x00000465  # Running in diagnostic mode
    MSG_00000466 = 0x00000466  # License key from the logger / License key: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-00000-00000
    MSG_00000467 = 0x00000467  # Shutdown reason: <NAME>!lf!- IPEmotionRT!lf!- Remote!lf!- Watchdog!lf!- Power suppply!lf!- Remote2 / Shutdown reason: IPEmotionRT
    MSG_00000468 = 0x00000468  # Run CheckDisk on <DRIVENAME> drive. <MODE>!lf!with <MODE>!lf!- Full mode.!lf!- Parallel mode. / Run CheckDisk on <DRIVENAME> drive. <MODE>
    MSG_00000469 = 0x00000469  # "Finished CheckDisk on <DRIVENAME> drive<RESULT>!lf!with <RESULT>!lf!- : Exit status could not be read.!lf!- : No (recoverable) errors detected.!lf!- : Recoverable errors detected.!lf!- : No access to the file system. / Finished CheckDisk on <DRIVENAME> drive<RESULT>
    MSG_0000046A = 0x0000046A  # Start by remote
    MSG_0000046B = 0x0000046B  # Start by remote2
    MSG_0000046C = 0x0000046C  # Start by WakeOnBus
    MSG_0000046D = 0x0000046D  # Start by NML
    MSG_0000046E = 0x0000046E  # Start by RTC
    MSG_0000046F = 0x0000046F  # Start by SMS
    MSG_00000470 = 0x00000470  # Start by undervoltage
    MSG_00000471 = 0x00000471  # Start by power bad
    MSG_00000472 = 0x00000472  # Logger type / Logger type: IPElog2 XX-X-X (In case of IPElog2)
    MSG_00000473 = 0x00000473  # CommunicationUnit: WLAN connected.
    MSG_00000474 = 0x00000474  # FTP connect to server <URL>!lf!SFTP connect to server <URL>
    MSG_00000475 = 0x00000475  # <FTP> changed to subdirectory: <SUBDIR>!lf!with <FTP>!lf!- FTP!lf!- SFTP / <FTP> changed to subdirectory: <SUBDIR>
    MSG_00000476 = 0x00000476  # Transferring files of measurement number <MEANR>
    MSG_00000477 = 0x00000477  # CheckDisk: <RESULT>!lf!with <RESULT>!lf!- CheckDisk had to truncate.!lf!- CheckDisk had to reclaim.!lf!- Free cluster summary wrong.!lf!- Dirty bit is set. Fs was not properly unmounted and some data may be corrupt.!lf!- Dirty bit is set. Fs was not properly unmounted and some data may be corrupt. Full-chkdsk necessary on Full post processing.!lf!- Large number of bad entries / CheckDisk: <RESULT>
    MSG_00000478 = 0x00000478  # SIM-Card number unlocked with <TEXT>!lf!- SIM card successfully unlocked!lf!- SIM card successfully unlocked (SIM card number): XXXXXXXXXXXXXXXXXXX / ModemManager: <TEXT>
    MSG_00000479 = 0x00000479  # Errors from ModemManager:!lf!with <TEXT>!lf!- Unable to get interface to unlock SIM. Reported error: ...!lf!- ModemManager: No modem with SIM card found!lf!- Can't enable modem. Reported error: ...!lf!- Unable to connect to <APN>. Reported error: ... / ModemManager: <TEXT>
    MSG_0000047A = 0x0000047A  # NetworkManager: Establishing Internet connection...
    MSG_0000047B = 0x0000047B  # NetworkManager: Unable to establish Internet connection
    MSG_0000047C = 0x0000047C  # NetworkManager: Internet connection successfully established
    MSG_0000047D = 0x0000047D  # Error sending email: <ERR>
    MSG_0000047E = 0x0000047E  # <TYPE> successfully sent (Subject: '<SUBJECT>').!lf!With <TYPE>!lf!- Trigger-Email <NR>!lf!- Delayed Email!lf!- Email!lf!- Info-Email / Time update ...
    MSG_0000047F = 0x0000047F  # File mismatch for %s: local and remote file are different
    MSG_00000480 = 0x00000480  # Transfer <FILENAME> failed, retry
    MSG_00000481 = 0x00000481  # Transfer <FILENAME> failed, no retry
    MSG_00000482 = 0x00000482  # Too many transfer errors, stopping data transfer.
    MSG_00000483 = 0x00000483  # Measurement stop
    MSG_00000484 = 0x00000484  # Measurement stop due to a shutdown event
    MSG_00000485 = 0x00000485  # Measurement start / Measurement start XXXX
    MSG_00000486 = 0x00000486  # e. g. File prefix: 167-578_191111_021113_ / File prefix: <VAR>
    MSG_00000487 = 0x00000487  # Configuration name / Configuration file: <NAME>
    MSG_00000488 = 0x00000488  # Remote signal on
    MSG_00000489 = 0x00000489  # Remote signal off
    MSG_0000048A = 0x0000048A  # Time update succeeded.
    MSG_0000048B = 0x0000048B  # Set NML mask: <HEX> / Set NML mask: 0x0002 (if the CAN 02 is meant)
    MSG_0000048C = 0x0000048C  # Set WakeOnBus mask: <HEX> / Set WakeOnBus mask: 0x0002 (if the CAN 02 is meant)
    MSG_0000048D = 0x0000048D  # Power supply / Power good
    MSG_0000048E = 0x0000048E  # Power supply / Power bad
    MSG_0000048F = 0x0000048F  # WLAN Connected and ready to use
    MSG_00000490 = 0x00000490  # WLAN Disconnected
    MSG_00000491 = 0x00000491  # Power supply / Power down
    MSG_00000492 = 0x00000492  # Transferring (<FILENR>/<TOTALFILES>): <FILENAME> ( <BYTES> bytes )
    MSG_00000493 = 0x00000493  # <USER>: Authentication by password failed: <ERROR_MESSAGE>
    MSG_00000494 = 0x00000494  # USB stick needs to be unplugged to restart measurement / Unplug USB Stick to restart measurement
    MSG_00000495 = 0x00000495  # Start of triggered storage groups / <StorageGroupName> Triggered storage started
    MSG_00000496 = 0x00000496  # Datalogger start failed, can't start measurement
    MSG_00000497 = 0x00000497  # Datalogger Init failed, can't start measurement
    MSG_00000498 = 0x00000498  # OBD-II vehicle identification
    MSG_00000499 = 0x00000499  # Not enough space to continue Measurement
    MSG_0000049A = 0x0000049A  # Disk space insufficient for measurement: %d / %d MB free
    MSG_0000049B = 0x0000049B  # PIN not accepted
    MSG_0000049C = 0x0000049C  # Stop of triggered storage groups / <StorageGroupName> Triggered storage stopped
    MSG_0000049D = 0x0000049D  # Restarted/splitted measurement due to disk space below limit
    MSG_0000049E = 0x0000049E  # License does not match
    MSG_0000049F = 0x0000049F  # Downloading (<FILENR>/<TOTALFILES>): <FILENAME> ( <BYTES> bytes )
    MSG_000004A0 = 0x000004A0  # OBD-II calibration identification
    MSG_000004A1 = 0x000004A1  # Not enough free disk space for copying file: <FILENAME>
    MSG_000004A2 = 0x000004A2  # Next WakeOnRTC planned for <DATE> at UTC <TIME> 
    MSG_000004A3 = 0x000004A3  # Hard drive: Model: <MODEL> Serial number: <SERIAL_NUMBER>
    MSG_000004A4 = 0x000004A4  # Restarting with synced configuration
    MSG_000004A5 = 0x000004A5  # Destination disk full : Free Space %s/%s MB. Unplug USB Stick to restart measurement.
    MSG_000004A6 = 0x000004A6  # File name with wrong serial number: <FILENAME>
    MSG_000004A8 = 0x000004A8  # OBD-II stored trouble code
    MSG_000004B0 = 0x000004B0  # OBD-II sporadic trouble code
    MSG_000004B8 = 0x000004B8  # <TYPE>: EPK <EcuEpk> match <Epk> of <EcuName> on <ConnectorName>!lf!With <TYPE>!lf!- CCP!lf!- XCP / <TYPE>: EPK <EcuEpk> match <Epk> of <EcuName> on <ConnectorName>
    MSG_000004C0 = 0x000004C0  # <TYPE>: EPK <EcuEpk> mismatch <Epk> of <EcuName> on <ConnectorName>!lf!With <TYPE>!lf!- CCP!lf!- XCP / <TYPE>: EPK <EcuEpk> mismatch <Epk> of <EcuName> on <ConnectorName>
    MSG_000004C8 = 0x000004C8  # <TYPE> measurement on <NAME>!lf!With <TYPE>!lf!- CAN!lf!- CCP!lf!- XCP / <TYPE> measurement on <NAME>
    MSG_000004D0 = 0x000004D0  # Timeout on <NAME>
    MSG_000004D8 = 0x000004D8  # Vehicle identification number: <NUMBER>
    MSG_000004E0 = 0x000004E0  # System like CAN FD or LIN or FlexRay satellite is not connected / The system is not available.
    MSG_000004E1 = 0x000004E1  # Special files like iev files have been deleted from logger / IEV data deleted
    MSG_000004E2 = 0x000004E2  # Wrong filesystem or write protected / USB Stick does not fit the requirements for coping data^! Check write protection and filesystem format.
    MSG_000004E3 = 0x000004E3  # Special files like iev are not existing on logger when trying to delete them / IEV data not existing
    MSG_000004E8 = 0x000004E8  # UDS job not completed: <Count>
    MSG_000004F0 = 0x000004F0  # UDS start ECUs failed on <Name>
    MSG_000004F8 = 0x000004F8  # Successfully switched to ECU version
    MSG_00000500 = 0x00000500  # <TYPE>: Start ECU failed on '<ConnectorName>'!lf!With <TYPE>!lf!- CCP!lf!- XCP / <TYPE>: Start ECU failed on '<ConnectorName>'
    MSG_00000508 = 0x00000508  # <TYPE> ECU not found on <NAME>!lf!With <TYPE>!lf!- CCP!lf!- XCP / <TYPE> ECU not found on <NAME>
    MSG_00000510 = 0x00000510  # <TYPE>: Second Tester on '<ConnectorName>'!lf!With <TYPE>!lf!- CCP!lf!- XCP / <TYPE>: Second Tester on '<ConnectorName>'
    MSG_00000511 = 0x00000511  # Mail: <ErrorMessage>
    MSG_00000512 = 0x00000512  # Certificate Control: Certificate expired
    MSG_00000513 = 0x00000513  # Certificate Control: Certificate installed successfully: <NAME>
    MSG_00000514 = 0x00000514  # USB Pen: No usb stick handling. Permission denied^!
    MSG_00000515 = 0x00000515  # ModemManager: Modem IMEI number: <IMEI>
    MSG_00000516 = 0x00000516  # ModemManager: SIM IMSI number: <IMSI>
    MSG_00000517 = 0x00000517  # Detected non-recoverable error. Failsafe state, waiting for manual recovery ...
    MSG_00000518 = 0x00000518  # Start of the traffic generator / <TrafficGeneratorName> traffic generator started
    MSG_00000519 = 0x00000519  # Stop of the traffic generator / <TrafficGeneratorName> traffic generator stopped
    MSG_0000051A = 0x0000051A  # Pause of the traffic generator started / <TrafficGeneratorName> traffic generator pause started
    MSG_0000051B = 0x0000051B  # Pause of the traffic generator stopped / <TrafficGeneratorName> traffic generator pause stopped
    MSG_0000051C = 0x0000051C  # Start of triggered storage groups with a defined pretrigger / <StorageGroupName> Triggered storage started. Pretrigger X s
    MSG_0000051D = 0x0000051D  # Stop of triggered storage groups with a defined posttrigger / <StorageGroupName> Triggered storage stopped. Posttrigger X s
    MSG_0000051E = 0x0000051E  # Datalogger start failed, filesystem error detected
    MSG_0000051F = 0x0000051F  # Failed to unmount USB Stick
    MSG_00000520 = 0x00000520  # CheckDisk error: <ERR>!lf!with <ERR>!lf!- No answer from CheckDisk process- CheckDisk not executed.!lf!- CheckDisk stopped by timeout.!lf! Filesystem check failed.!lf!- Remounting drives failed. / CheckDisk error: <ERR>
    MSG_00000521 = 0x00000521  # ModemManager: SIM card number: <Identifier>
    MSG_00000522 = 0x00000522  # Failsafe state entering in <Number> tries
    MSG_00000523 = 0x00000523  # Ignore new split event because the previous one hasn't finished yet 
    MSG_00000524 = 0x00000524  # ModemManager: Access technology <Access technology>
    MSG_00000525 = 0x00000525  # Postprocessing stopped as configured emergency switch off time is reached
    MSG_00000528 = 0x00000528  # Firmware differs from recommended version which will be installed via 'Update devices' function
    MSG_00000530 = 0x00000530  # Status	CPU: [CPU load], Used memory: [Memory], Free disk space (MEA/RAW): [SpaceMEA] [SpaceRAW]
    MSG_00000538 = 0x00000538  # Starting with ECU version
    MSG_00000540 = 0x00000540  # GPS: Data valid/invalid
    MSG_00000548 = 0x00000548  # Job sequence is active
    MSG_00000550 = 0x00000550  # Firmmware update start/stop
    MSG_000005F0 = 0x000005F0  # Firmware update failed.
    MSG_000005F1 = 0x000005F1  # Infos about aborting the update!lf!- Aborting firmware update ...!lf!Firmware update aborted.!lf!Firmware update abort failed. / Aborting firmware update ...
    MSG_000005F2 = 0x000005F2  # EthernetInterface [<InterfaceName>] Detected conflict of IP address (<IP>) with IP address of interface <InterfaceName>
    MSG_000005F3 = 0x000005F3  # Conflict concerning IP subnets
    MSG_000005F5 = 0x000005F5  # Error messages from unmount process / <MESSAGE>
    MSG_000005F6 = 0x000005F6  # Unmounting drive ...!lf!Drive unmounted. / <MESSAGE>
    MSG_000005F7 = 0x000005F7  # Unmount of drive aborted due to post-processing.
    MSG_000005F8 = 0x000005F8  # Remount of <DIR> failed! Error: <ERRORMESSAGE>!lf!- Can't read mount table for validation^!!lf!- Mount directory not present: <NAME>. Drive not mounted. / <MESSAGE>
    MSG_000005F9 = 0x000005F9  # Mounting of <NAME> succeeded.
    MSG_000005FA = 0x000005FA  # Remote timeout
    MSG_000005FB = 0x000005FB  # Startup watchdog timeout
    MSG_000005FC = 0x000005FC  # Runtime watchdog timeout
    MSG_0000060B = 0x0000060B  # Start by power bad
    MSG_0000060C = 0x0000060C  # Start by ethernet (ABK)
    MSG_0000060D = 0x0000060D  # Start due to reboot
    MSG_0000060E = 0x0000060E  # Start due to watchdog
    MSG_00000611 = 0x00000611  # Enable WakeOnSMS
    MSG_00000614 = 0x00000614  # Immediate shutdown request
    MSG_0000061B = 0x0000061B  # Always-Online is <enabled/disabled> for medium <medium name>.
    MSG_0000061C = 0x0000061C  # IP Settigns for Always-Online on Network <network name>.
    MSG_0000061D = 0x0000061D  # Ping to ###.###.###.### failed
    MSG_0000061E = 0x0000061E  # Ping: DNS resolving failed or IP address not valid



from typing import Dict

MESSAGE_TITLES: Dict[LoggerMessageId, str] = {
    LoggerMessageId.MSG_0000000F: "Free measurement space",
    LoggerMessageId.MSG_00000011: "Fallback folder has measurement files",
    LoggerMessageId.MSG_00000012: "Jobs finished",
    LoggerMessageId.MSG_00000013: "Update complete",
    LoggerMessageId.MSG_00000014: "Program update complete",
    LoggerMessageId.MSG_00000015: "USB Stick connected",
    LoggerMessageId.MSG_00000016: "USB Stick disconnected",
    LoggerMessageId.MSG_00000019: "Copy log file",
    LoggerMessageId.MSG_0000001A: "Start data transfer",
    LoggerMessageId.MSG_0000001C: "Start time update",
    LoggerMessageId.MSG_0000001F: "Time update finished",
    LoggerMessageId.MSG_00000020: "Data transfer finished",
    LoggerMessageId.MSG_00000023: "Time update failed",
    LoggerMessageId.MSG_00000024: "Data transfer failed",
    LoggerMessageId.MSG_00000026: "Measurement space (cyclic)",
    LoggerMessageId.MSG_00000027: "Time left (cyclic)",
    LoggerMessageId.MSG_00000028: "Total disk space",
    LoggerMessageId.MSG_0000002F: "Generating upload file",
    LoggerMessageId.MSG_00000035: "PUK required",
    LoggerMessageId.MSG_0000003D: "FTP connection established",
    LoggerMessageId.MSG_00000043: "Start mail",
    LoggerMessageId.MSG_00000044: "Unplug USB Stick to reboot",
    LoggerMessageId.MSG_00000047: "Mail finished",
    LoggerMessageId.MSG_00000048: "Mail failed",
    LoggerMessageId.MSG_0000004C: "USB peripheral mode enabled",
    LoggerMessageId.MSG_0000004D: "USB peripheral mode disabled",
    LoggerMessageId.MSG_000003E9: "IPEmotionRT version",
    LoggerMessageId.MSG_000003EA: "Serial number",
    LoggerMessageId.MSG_000003EF: "Hardware revision",
    LoggerMessageId.MSG_000003F0: "Production date",
    LoggerMessageId.MSG_000003F6: "Calibration date",
    LoggerMessageId.MSG_000003F7: "New program found",
    LoggerMessageId.MSG_000003F8: "Try continue measurement",
    LoggerMessageId.MSG_000003F9: "Start date/time",
    LoggerMessageId.MSG_000003FA: "Stop date/time",
    LoggerMessageId.MSG_000003FB: "Firmware update running",
    LoggerMessageId.MSG_000003FC: "Time zone",
    LoggerMessageId.MSG_000003FD: "Data recording delay",
    LoggerMessageId.MSG_000003FE: "Firmware update done",
    LoggerMessageId.MSG_000003FF: "Exception occurred",
    LoggerMessageId.MSG_00000401: "Copy & compress files",
    LoggerMessageId.MSG_00000402: "Copying files",
    LoggerMessageId.MSG_00000403: "Files ready",
    LoggerMessageId.MSG_00000404: "Rescue configuration found",
    LoggerMessageId.MSG_00000405: "Setup might overload logger",
    LoggerMessageId.MSG_00000406: "iDDS",
    LoggerMessageId.MSG_00000407: "Data transfer disabled by user",
    LoggerMessageId.MSG_00000451: "Post-processing running",
    LoggerMessageId.MSG_0000045A: "Config version too new",
    LoggerMessageId.MSG_0000045B: "License missing",
    LoggerMessageId.MSG_0000045C: "Version too old",
    LoggerMessageId.MSG_0000045D: "License missing (type)",
    LoggerMessageId.MSG_0000045E: "FTP: Unable to connect",
    LoggerMessageId.MSG_00000460: "Kernel message",
    LoggerMessageId.MSG_00000461: "Limit message",
    LoggerMessageId.MSG_00000462: "Sequence stopped",
    LoggerMessageId.MSG_00000463: "File split: buffer overrun",
    LoggerMessageId.MSG_00000465: "Diagnostic mode",
    LoggerMessageId.MSG_00000466: "License key",
    LoggerMessageId.MSG_00000467: "Shutdown reason",
    LoggerMessageId.MSG_00000468: "Run CheckDisk",
    LoggerMessageId.MSG_00000469: "Finished CheckDisk",
    LoggerMessageId.MSG_0000046A: "Start by remote",
    LoggerMessageId.MSG_0000046B: "Start by remote2",
    LoggerMessageId.MSG_0000046C: "Start by WakeOnBus",
    LoggerMessageId.MSG_0000046D: "Start by NML",
    LoggerMessageId.MSG_0000046E: "Start by RTC",
    LoggerMessageId.MSG_0000046F: "Start by SMS",
    LoggerMessageId.MSG_00000470: "Start by undervoltage",
    LoggerMessageId.MSG_00000471: "Start by power bad",
    LoggerMessageId.MSG_00000472: "Logger type",
    LoggerMessageId.MSG_00000473: "WLAN connected",
    LoggerMessageId.MSG_00000474: "FTP/SFTP connect",
    LoggerMessageId.MSG_00000475: "Changed subdirectory",
    LoggerMessageId.MSG_00000476: "Transferring measurement files",
    LoggerMessageId.MSG_00000477: "CheckDisk result",
    LoggerMessageId.MSG_00000478: "SIM unlocked / ModemManager",
    LoggerMessageId.MSG_00000479: "ModemManager error",
    LoggerMessageId.MSG_0000047A: "Establishing Internet connection",
    LoggerMessageId.MSG_0000047B: "Internet connection failed",
    LoggerMessageId.MSG_0000047C: "Internet connection established",
    LoggerMessageId.MSG_0000047D: "Email send error",
    LoggerMessageId.MSG_0000047E: "<TYPE> sent",
    LoggerMessageId.MSG_0000047F: "File mismatch",
    LoggerMessageId.MSG_00000480: "Transfer failed (retry)",
    LoggerMessageId.MSG_00000481: "Transfer failed (no retry)",
    LoggerMessageId.MSG_00000482: "Too many transfer errors",
    LoggerMessageId.MSG_00000483: "Measurement stop",
    LoggerMessageId.MSG_00000484: "Measurement stop (shutdown)",
    LoggerMessageId.MSG_00000485: "Measurement start",
    LoggerMessageId.MSG_00000486: "File prefix",
    LoggerMessageId.MSG_00000487: "Configuration name",
    LoggerMessageId.MSG_00000488: "Remote signal on",
    LoggerMessageId.MSG_00000489: "Remote signal off",
    LoggerMessageId.MSG_0000048A: "Time update succeeded",
    LoggerMessageId.MSG_0000048B: "Set NML mask",
    LoggerMessageId.MSG_0000048C: "Set WakeOnBus mask",
    LoggerMessageId.MSG_0000048D: "Power good",
    LoggerMessageId.MSG_0000048E: "Power bad",
    LoggerMessageId.MSG_0000048F: "WLAN ready",
    LoggerMessageId.MSG_00000490: "WLAN disconnected",
    LoggerMessageId.MSG_00000491: "Power down",
    LoggerMessageId.MSG_00000492: "Transferring file",
    LoggerMessageId.MSG_00000493: "Auth by password failed",
    LoggerMessageId.MSG_00000494: "Unplug USB to restart measurement",
    LoggerMessageId.MSG_00000495: "Triggered storage started",
    LoggerMessageId.MSG_00000496: "Datalogger start failed",
    LoggerMessageId.MSG_00000497: "Datalogger init failed",
    LoggerMessageId.MSG_00000498: "OBD-II vehicle identification",
    LoggerMessageId.MSG_00000499: "Not enough space to continue",
    LoggerMessageId.MSG_0000049A: "Disk space insufficient",
    LoggerMessageId.MSG_0000049B: "PIN not accepted",
    LoggerMessageId.MSG_0000049C: "Triggered storage stopped",
    LoggerMessageId.MSG_0000049D: "Measurement restarted/splitted (low space)",
    LoggerMessageId.MSG_0000049E: "License does not match",
    LoggerMessageId.MSG_0000049F: "Downloading file",
    LoggerMessageId.MSG_000004A0: "OBD-II calibration identification",
    LoggerMessageId.MSG_000004A1: "No space to copy file",
    LoggerMessageId.MSG_000004A2: "Next WakeOnRTC planned",
    LoggerMessageId.MSG_000004A3: "Hard drive info",
    LoggerMessageId.MSG_000004A4: "Restart with synced configuration",
    LoggerMessageId.MSG_000004A5: "Destination disk full",
    LoggerMessageId.MSG_000004A6: "Wrong serial in filename",
    LoggerMessageId.MSG_000004A8: "OBD-II stored DTC",
    LoggerMessageId.MSG_000004B0: "OBD-II sporadic DTC",
    LoggerMessageId.MSG_000004B8: "EPK match",
    LoggerMessageId.MSG_000004C0: "EPK mismatch",
    LoggerMessageId.MSG_000004C8: "<TYPE> measurement on <NAME>",
    LoggerMessageId.MSG_000004D0: "Timeout on <NAME>",
    LoggerMessageId.MSG_000004D8: "VIN",
    LoggerMessageId.MSG_000004E0: "System not available",
    LoggerMessageId.MSG_000004E1: "IEV data deleted",
    LoggerMessageId.MSG_000004E2: "USB Stick not suitable / write-protected",
    LoggerMessageId.MSG_000004E3: "IEV data not existing",
    LoggerMessageId.MSG_000004E8: "UDS job not completed",
    LoggerMessageId.MSG_000004F0: "UDS start ECUs failed",
    LoggerMessageId.MSG_000004F8: "Switched to ECU version",
    LoggerMessageId.MSG_00000500: "Start ECU failed",
    LoggerMessageId.MSG_00000508: "ECU not found",
    LoggerMessageId.MSG_00000510: "Second tester detected",
    LoggerMessageId.MSG_00000511: "Mail error",
    LoggerMessageId.MSG_00000512: "Certificate expired",
    LoggerMessageId.MSG_00000513: "Certificate installed",
    LoggerMessageId.MSG_00000514: "USB pen permission denied",
    LoggerMessageId.MSG_00000515: "Modem IMEI",
    LoggerMessageId.MSG_00000516: "SIM IMSI",
    LoggerMessageId.MSG_00000517: "Failsafe state",
    LoggerMessageId.MSG_00000518: "Traffic generator started",
    LoggerMessageId.MSG_00000519: "Traffic generator stopped",
    LoggerMessageId.MSG_0000051A: "Traffic generator pause started",
    LoggerMessageId.MSG_0000051B: "Traffic generator pause stopped",
    LoggerMessageId.MSG_0000051C: "Triggered storage with pretrigger",
    LoggerMessageId.MSG_0000051D: "Triggered storage with posttrigger",
    LoggerMessageId.MSG_0000051E: "Filesystem error (start failed)",
    LoggerMessageId.MSG_0000051F: "Failed to unmount USB",
    LoggerMessageId.MSG_00000520: "CheckDisk error",
    LoggerMessageId.MSG_00000521: "SIM card number",
    LoggerMessageId.MSG_00000522: "Failsafe entering (retries)",
    LoggerMessageId.MSG_00000523: "Split ignored (previous pending)",
    LoggerMessageId.MSG_00000524: "Access technology",
    LoggerMessageId.MSG_00000525: "Postprocessing stopped (emergency off time)",
    LoggerMessageId.MSG_00000528: "Firmware differs from recommended",
    LoggerMessageId.MSG_00000530: "System status",
    LoggerMessageId.MSG_00000538: "Starting with ECU version",
    LoggerMessageId.MSG_00000540: "GPS data state",
    LoggerMessageId.MSG_00000548: "Job sequence active",
    LoggerMessageId.MSG_00000550: "Firmware update start/stop",
    LoggerMessageId.MSG_000005F0: "Firmware update failed",
    LoggerMessageId.MSG_000005F1: "Firmware update aborted",
    LoggerMessageId.MSG_000005F2: "IP conflict detected",
    LoggerMessageId.MSG_000005F3: "Subnet conflict",
    LoggerMessageId.MSG_000005F5: "Unmount error",
    LoggerMessageId.MSG_000005F6: "Unmounting drive",
    LoggerMessageId.MSG_000005F7: "Unmount aborted (post-processing)",
    LoggerMessageId.MSG_000005F8: "Remount failed",
    LoggerMessageId.MSG_000005F9: "Mount succeeded",
    LoggerMessageId.MSG_000005FA: "Remote timeout",
    LoggerMessageId.MSG_000005FB: "Startup watchdog timeout",
    LoggerMessageId.MSG_000005FC: "Runtime watchdog timeout",
    LoggerMessageId.MSG_0000060B: "Start by power bad",
    LoggerMessageId.MSG_0000060C: "Start by ethernet (ABK)",
    LoggerMessageId.MSG_0000060D: "Start due to reboot",
    LoggerMessageId.MSG_0000060E: "Start due to watchdog",
    LoggerMessageId.MSG_00000611: "Enable WakeOnSMS",
    LoggerMessageId.MSG_00000614: "Immediate shutdown request",
    LoggerMessageId.MSG_0000061B: "Always-Online state",
    LoggerMessageId.MSG_0000061C: "Always-Online IP settings",
    LoggerMessageId.MSG_0000061D: "Ping failed",
    LoggerMessageId.MSG_0000061E: "Ping: DNS failed / invalid IP",
}

def title_for(message_id: LoggerMessageId) -> str:
    """Return a short, human-friendly title for a LoggerMessageId."""
    return MESSAGE_TITLES.get(message_id, message_id.name)


# Critical message IDs for filtering (used in log analysis)
CRITICAL_MESSAGE_IDS = {
    0x000003FF,  # ExceptionOccurred
    0x000005F0,  # FirmwareUpdateFailed
    0x000005F1,  # FirmwareUpdateAbort
    0x00000517,  # FailsafeState
    0x000005FB,  # StartupWatchdogTimeout
    0x000005FC,  # RuntimeWatchdogTimeout
    0x00000485,  # MeasurementStart
    0x00000483,  # MeasurementStop
    0x00000484,  # MeasurementStopShutdown
    0x00000490,  # WlanDisconnected
    0x000003F9,  # StartDateTime
    0x000003FA,  # StopDateTime
    0x000003EA,  # LoggerSerialNumber
    0x000003E9,  # IpeRtVersion
    0x00000472,  # LoggerType
}
