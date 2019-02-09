# BeamDesign
A Python library intended to carry out beam / column design checks for structural engineers.

Currently this is very definitely a work in progress. Initially, the library will start with a check to AS4100, the current Australian Standard for steel design. It is intended that version 0.1 will be released when a full AS4100 check is implemented. Other Australian and International standards may follow.

It is intended that this library will:

* Be simple to use.
* Have a strict distinction between code that represents real world objects such as beams / columns and the code that carries out the design checks using the engineering "useful fiction" that are design codes.
* Allow for easy addition of other design codes.

Currently working towards release 0.1 (see [project board](https://github.com/skane88/BeamDesign/projects/1) for release plans)

This library is NOT intended for use by persons who do not have an appropriate structural or mechanical engineering background. Design standards have many assumptions built into them that may not be realised by those without appropriate training. Assumptions made by the designer when calculating the loads on a beam may also affect the checks required by the design codes. Use of this library by those without appropriate knowledge could lead to serious structural failure.
