# ----------------------------------------------------------------------
# Copyright (C) 2016, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# ----------------------------------------------------------------------

import os
from influxdb import InfluxDBClient

from sensor import Sensor
from htmsensormodel import HtmSensorModel


DEFAULT_HOST = os.environ["INFLUX_HOST"]
DEFAULT_PORT = os.environ["INFLUX_PORT"]
DEFAULT_USER = os.environ["INFLUX_USER"]
DEFAULT_PASS = os.environ["INFLUX_PASS"]
DEFAULT_SSL = "INFLUX_SSL" in os.environ \
              and os.environ["INFLUX_SSL"] != "" \
              and os.environ["INFLUX_SSL"] != "0" \
              and os.environ["INFLUX_SSL"].lower() != "false"


class InfluxHtmClient:


  @staticmethod
  def _seriesIsModel(name):
    return name.endswith("_model") or name.endswith("_inference")


  def __init__(self,
               database,
               host=DEFAULT_HOST,
               port=DEFAULT_PORT,
               username=DEFAULT_USER,
               password=DEFAULT_PASS,
               ssl=DEFAULT_SSL,
               verbose=False
               ):

    self._database = database
    self._verbose = verbose

    if self._verbose:
      print("Connecting to {0}:{1}@{2}:{3} (SSL? {4})".format(
        username, "***********", host, port, ssl
      ))

    self._client = InfluxDBClient(
      host=host,
      port=port,
      username=username,
      password=password,
      ssl=ssl
    )

    # TODO: having IO in the constructor is a bad idea, but this is a prototype.
    databases = self._client.get_list_database()
    if database not in [d["name"] for d in databases]:
      if self._verbose:
        print "Creating Influx database '%s'..." % database
      self._client.create_database(database)

    if self._verbose:
      print "Using Influx database '%s'." % database
    self._client.switch_database(database)


  def listSeries(self):
    measurements = self._client.get_list_series()
    # First we need to split out measurements into series.
    series = []
    for measurement in measurements:
      name = measurement["name"]
      for tags in measurement["tags"]:
        series.append({"name": name, "tags": tags})
    return series



  def getSensors(self):
    return [Sensor(s, self)
            for s in self.listSeries()
            if not self._seriesIsModel(s["name"])]


  def getHtmModels(self):
    return [HtmSensorModel(s, self)
            for s in self.listSeries()
            if self._seriesIsModel(s["name"])]


  def getSensor(self, measurement=None, component=None):
    sensors = self.getSensors()
    for s in sensors:
      if s.getMeasurement() == measurement and s.getComponent() == component:
        return s


