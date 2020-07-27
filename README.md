# Pi-Video-Security-System

### (Work-In-Progress)

This repository contains the server and video side of an object-detecting video surveillance system that is designed to run on the Raspberry Pi 4B with the
official Pi Camera Module V2. The project is part of a currently ongoing dissertation and is therefore a work in progress. It will also include an Android client which can be seen at https://github.com/ajking42/Pi-Video-Security-System-Android.

## Goals

The aim of this project is to create a flexible, privacy-focused, object-detection system that can be primarily controlled from a remote Android application.
Currently, the main focus of this project is on a home security system, detecting common things of interest in such a scenario such as people and cars. 
Due to the flexible nature of the design, it should also be possible to implement other and/or custom-trained object-detecting models for similar purposes. For example, it is hoped that
a species detecting wildlife camera could eventually be implemented from this architecture. Such purposes shoul only be limited by the complexity of the model
used and the processing power of the Raspberry Pi.
