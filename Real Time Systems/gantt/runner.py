#!/usr/bin/env python
"""
Wrapper function to use the Gantt class
"""
from gantt import Gantt

g = Gantt('./real_time_schedule.json')
g.render()
g.show()
