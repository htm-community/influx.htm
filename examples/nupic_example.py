#!/usr/bin/env python
from datetime import datetime
import simplejson as json

from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.algorithms import anomaly_likelihood
from nupic.data.inference_shifter import InferenceShifter

from influxhtm import InfluxHtmClient

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def createModel(paramPath):
  with open(paramPath, "r") as dataIn:
    modelParams = json.loads(dataIn.read())
  model = ModelFactory.create(modelParams["modelParams"])
  model.enableInference({"predictedField": "value"})
  return model


def main():
  # Create the influxhtm client and get a sensor.
  client = InfluxHtmClient("smartthings_htm_bridge")
  fridge = client.getSensor(measurement="power", component="Mini+Fridge")
  # Make sure there are is no existing HTM data for this sensor.
  fridge.deleteHtmModels()
  # And create a new storage space for this model I'm creating.
  modelStore = fridge.createHtmModel("mtaylor_local_mini_fridge")
  # Create a real HTM model object through the NuPIC OPF.
  htmModel = createModel("./model_params/anomaly_params.json")

  shifter = InferenceShifter()
  anomalyLikelihood = anomaly_likelihood.AnomalyLikelihood()

  # This is the function that will process each data point through the real HTM
  # model we created above.
  def htmProcessor(point):
    # Time strings are evil! We have to make sure it is formatted properly for
    # NuPIC.
    timeString = point[0]
    if "." in timeString:
      timeString = timeString.split(".").pop(0)
    else:
      timeString = timeString.split("Z").pop(0)
    timestamp = datetime.strptime(timeString, DATE_FORMAT)

    # This is the value.
    value = point[1]

    # Here's where the magic happens ;)
    result = htmModel.run({
      "timestamp": timestamp,
      "value": value
    })
    # Shifting results because we are plotting.
    result = shifter.shift(result)
    # Prepare a result object for writing into InfluxDB.
    inferences = result.inferences
    anomalyScore = inferences["anomalyScore"]
    likelihood = anomalyLikelihood.anomalyProbability(
      value, anomalyScore, timestamp)
    return {
      "inferences": result.inferences,
      "anomalyLikelihood": likelihood
    }

  modelStore.processData(
    htmProcessor,
    since=datetime(2016, 2, 16),
    until=datetime(2016, 2, 26),
    aggregate="10m"
  )

if __name__ == "__main__":
  main()
