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

class Sensor:

  def __init__(self, sensorDef, influxHtmClient):
    self._name = sensorDef["name"]
    self._tags = sensorDef["tags"]
    self._component = self._tags["component"]
    self._client = influxHtmClient
    pass


  def _writePoints(self, points):
    payload = []
    for p in points:
      payload.append({
        "tags": {
          "component": self.getComponent(),
        },
        "time": p["time"],
        "measurement": self.getMeasurement(),
        "fields": {
          "value": p["value"]
        }
      })
    self._client.getInfluxClient().write_points(payload)


  def getTags(self):
    return self._tags


  def getMeasurement(self):
    return self._name


  def getComponent(self):
    return self._component


  def getHtmModel(self):
    for model in self._client.getHtmModels():
      if model.getName() == "{} HTM Model".format(self.getName()):
        return model


  def getName(self):
    return "{0} {1}".format(self.getComponent(), self.getMeasurement())


  def write(self, data):
    if isinstance(data, list):
      self._writePoints(data)
    else:
      self._writePoints([data])


  def getData(self, **kwargs):
    return self._client._query(
      self.getMeasurement(), self.getComponent(), **kwargs
    )


  def createHtmModel(self, id):
    return self._client.createHtmModel(
      id, measurement=self.getMeasurement(), component=self.getComponent()
    )


  def __str__(self):
    return self.getName()
