#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aprs

class LocationFrame(aprs.Frame):
    def __init__(self, frame=None):
        self.source = ''
        self.destination = 'APRS'
        self.path = []
        self.text = ''
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.course = None
        self.speed = None
        self.symboltable = None
        self.symbolcode = None
        self.comment = 'Python APRS Tracker'
        super(LocationFrame, self) #.__init__(frame)

    def validate(self):
        self.latitude = self.latitude or 0
        self.longitude = self.longitude or 0
        self.course = self.course or 0
        self.altitude = self.altitude or 0
        self.speed = self.speed or 0

    def make_frame(self):
        self.validate()
        self.text = ''.join([
            self.source,
            '>',
            self.destination,
            ':!',
            self.latitude,
            self.symboltable,
            self.longitude,
            self.symbolcode,
            "%03d" % self.course,
            '/',
            "%03d" % self.speed,
            '/',
            'A=',
            "%06d" % self.altitude,
            ' ',
            self.comment
        ])
        self.text = bytes(self.text, 'UTF-8')
