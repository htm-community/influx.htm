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
    self._verbose = False
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


  def _zipSensorAndInferenceData(self, sensorData, inferenceData):
    # If there is no inferenceData, we're going to fake it so the schema matches
    if inferenceData is None:
      inferenceData = {
        "series": [{
          "values": [],
          "columns": ["time", "anomalyScore", "anomalyLikelihood"]
        }]
      }
    sensorSeries = sensorData["series"][0]
    inferenceSeries = inferenceData["series"][0]

    sensorValues = sensorSeries["values"]
    sensorColumns = sensorSeries["columns"]
    sensorTimeIndex = sensorColumns.index("time")
    inferenceValues = inferenceSeries["values"]
    inferenceColumns = inferenceSeries["columns"]
    inferenceTimeIndex = inferenceColumns.index("time")

    columnsOut = sensorColumns + inferenceColumns[1:]
    valuesOut = []
    prevSensor = None
    prevAnomScore = None
    prevAnomLikely = None

    while len(sensorValues) > 0:
      sensorTime = sensorValues[0][sensorTimeIndex]

      if len(inferenceValues) > 1:
        inferenceTime = inferenceValues[0][inferenceTimeIndex]

      if len(inferenceValues) == 0:
        # When there are no inference values, we just add None values.
        sensorValue = sensorValues.pop(0)
        valuesOut.append(sensorValue + [None, None])
        prevSensor = sensorValue[1]
      elif sensorTime == inferenceTime:
        # When times are the same, we add all the data.
        sensorValue = sensorValues.pop(0)
        inferenceValue = inferenceValues.pop(0)
        valuesOut.append(sensorValue + inferenceValue[1:])
        prevSensor = sensorValue[1]
        prevAnomScore = inferenceValue[1]
        prevAnomLikely = inferenceValue[2]
      elif sensorTime < inferenceTime:
        # When model data is ahead, we only add the sensor data and the previous
        # values for the model.
        sensorValue = sensorValues.pop(0)
        valuesOut.append(sensorValue + [prevAnomScore, prevAnomLikely])
        prevSensor = sensorValue[1]
      else:
        # When the sensor is ahead, we only add the model data and use the
        # previous sensor value.
        inferenceValue = inferenceValues.pop(0)
        valuesOut.append([inferenceValue[0], prevSensor] + inferenceValue[1:])
        prevAnomScore = inferenceValue[1]
        prevAnomLikely = inferenceValue[2]

    dataOut = {
      "series": [{
        "values": valuesOut,
        "name": sensorSeries["name"],
        "columns": columnsOut,
      }]
    }

    return dataOut



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


  def deleteHtmModels(self):
    for htmModel in self._client.getHtmModels():
      htmModel.delete()


  def getEarliestTimestamp(self):
    measurement = self.getMeasurement()
    component = self.getComponent()
    query = ("SELECT * FROM {0} WHERE component = '{1}' "
             "ORDER BY time LIMIT 1").format(measurement, component)
    if self._verbose:
      print query
    response = self._client._client.query(query)
    return response.raw["series"][0]["values"][0][0]


  def getCombinedSensorData(self,
                    limit=None,
                    since=None,
                    aggregation=None):
    if since is None and aggregation is not None:
      since = self.getEarliestTimestamp()
    sensorData = self.getData(
      limit=limit, since=since, aggregation=aggregation
    )
    sensorValues = sensorData["series"][0]["values"]
    # Use the first and last points of the sensor data to bound the model query.
    firstPointTime = sensorValues[0][0]
    lastPointTime = sensorValues[-1][0]
    model = self.getHtmModel()
    if model is None:
      return sensorData
    inferenceData = model.getModelResults(
      since=firstPointTime, until=lastPointTime
    )
    return self._zipSensorAndInferenceData(sensorData, inferenceData)


  def __str__(self):
    return self.getName()
