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


  def _listSeries(self):
    measurements = self._client.get_list_series()
    # First we need to split out measurements into series.
    series = []
    for measurement in measurements:
      name = measurement["name"]
      for tags in measurement["tags"]:
        series.append({"name": name, "tags": tags})
    return series


  def _query(self, measurement, component, **kwargs):
    toSelect = "value"
    aggregation = None
    if "aggregation" in kwargs and kwargs["aggregation"] is not None:
      aggregation = kwargs["aggregation"]
      toSelect = "MEAN(value)"

    query = "SELECT {0} FROM {1} WHERE component = '{2}'"\
      .format(toSelect, measurement, component)

    if "since" in kwargs:
      since = kwargs["since"]
      # since might be an integer timestamp or a time string. If it is a time
      # string, we'll just put single quotes around it to play nice with Influx.
      if isinstance(since, basestring):
        since = "'{}'".format(since)
      query += " AND time > {0}".format(since)

    if aggregation is None:
      query += " GROUP BY *"
    else:
      query += " GROUP BY time({0}) fill(previous)".format(
        kwargs["aggregation"]
      )

    query += " ORDER BY time DESC"

    limit = kwargs["limit"]
    if limit is not None:
      query += " LIMIT {0}".format(limit)

    if self._verbose:
      print query

    response = self._client.query(query)

    # Don't process empty responses
    if len(response) < 1:
      return []

    data = response.raw
    # Because of the descending order in the query, we want to reverse the data
    # so it is actually in ascending order. The descending order was really just
    # to get the latest data.
    data["series"][0]["values"] = list(reversed(data["series"][0]["values"]))
    return data


  def createSensor(self, measurement=None, component=None):
    if measurement is None or component is None:
      raise ValueError("You must provide both measurement and component when "
                       "creating a new influxhtm.Sensor object.")
    return Sensor({
      "name": measurement,
      "tags": {
        "component": component
      }
    }, self)


  def getInfluxClient(self):
    return self._client


  def getSensors(self):
    return [Sensor(s, self)
            for s in self._listSeries()
            if not self._seriesIsModel(s["name"])]


  def getHtmModels(self):
    return [HtmSensorModel(s, self)
            for s in self._listSeries()
            if self._seriesIsModel(s["name"])]


  def getSensor(self, measurement=None, component=None):
    sensors = self.getSensors()
    for s in sensors:
      if s.getMeasurement() == measurement and s.getComponent() == component:
        return s
