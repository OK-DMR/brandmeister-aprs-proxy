CREATE TABLE `Positions` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DMRID` int(11) NOT NULL,
  `Master` int(11) NOT NULL,
  `Latitude` double unsigned NOT NULL,
  `Longitude` double unsigned NOT NULL,
  `Speed` int(10) unsigned DEFAULT NULL,
  `Course` int(10) unsigned DEFAULT NULL,
  `Altitude` int(10) unsigned DEFAULT NULL,
  `RSSI` int(10) unsigned DEFAULT NULL COMMENT 'Signal strength',
  `Repeater` int(10) DEFAULT NULL,
  `TimeStamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `dmrid_timestamp_unique` (`DMRID`,`TimeStamp`)
) ENGINE=InnoDB AUTO_INCREMENT=105378 DEFAULT CHARSET=utf8
