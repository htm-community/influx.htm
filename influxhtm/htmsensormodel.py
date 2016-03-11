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

class HtmSensorModel:

  def __init__(self, modelDef, influxHtmClient):
    self._name = modelDef["name"]
    self._tags = modelDef["tags"]
    self._component = self._tags["component"]
    self._client = influxHtmClient
    pass


  def getTags(self):
    return self._tags


  def getMeasurement(self):
    return self._name.split("_").pop(0)


  def getComponent(self):
    return self._component


  def getName(self):
    return "{0} {1} HTM Model".format(self.getComponent(), self.getMeasurement())


  def writeResult(self, time, modelResult):
    payload = [{
      "time": time,
      "tags": {
        "component": self.getComponent()
      },
      "measurement": self.getMeasurement() + "_model",
      "fields": {
        "anomalyScore": modelResult["inferences"]["anomalyScore"],
        "anomalyLikelihood": modelResult["anomalyLikelihood"]
      }
    }]
    self._client.getInfluxClient().write_points(payload)



  def __str__(self):
    return self.getName()
