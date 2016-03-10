* warning: work in progress *


# Idea

Stream processing is different from other types of programming in several ways:

- low-cost life cycle
- constant persistence of model state is preferrable
- fast startup
- automatic restarts
- firehose is a good analogy


This library aims to be a stream modeller using NuPIC as an HTM implementation and storing all data in InfluxDB. 

# Goals

- Object model for scalar data, prediction, and anomaly retrieval and storage.
- Standard for storing HTM results alongside of time-series data streams from sensor type things
- Standards for easy data aggregation
- Tools to create retention policies and continuous queries at different aggregation periods for HTM data input feeds
- Representations of HTM models know where their were sourced

# TODO

1. Create an extension of the `InfluxDBClient` class in the `influxdb==2.12.0` python library.
1. Create a `Sensor` class to represent a `measurement` with a `tag="component"`.
1. Create a `HTMSensorModel` class to represent the HTM results while processing a `Sensor`.

# Object Model

`Sensor`: An object in spacetime emitting data at any interval. Static structure.
`HtmSensorModel`: Attached to a `Sensor` and has many `HtmModelResults` objects order by time.
`HtmModelResults`: Contains all data in an [OPF](https://github.com/numenta/nupic/tree/master/src/nupic/frameworks/opf) model result. One for each input row. 


# Example Usage

## Creating Objects

```python
client = InfluxHtmClient()

# Creates a new "temperature" measurement in InfluxDB, holding the component as 
# a tag in memory for future writes.
tempSensor = client.createSensor(measurement="temperature", component="Front+Door")

# Creates a new "temperature_model" measurement in InfluxDB, holding the 
# component as a tag in memory for future writes. Requires a model identifier, 
# which should be created by the HTM system and explicitly inform how to get 
# back to the original HTM model. For example, this could be a URL to a HITC
# model object or just a GUID created by the originating HTM platform. If a 
# model already exists for this Sensor, an error should raise.
htmModel = tempSensor.createModel("model-id")
```

## Retrieving Objects

```python
# Returns a list of Sensor instances.
sensors = client.getSensors()

# Returns a Sensor instance.
tempSensor = client.getSensor(measurement="temperature", component="Front+Door")

# Returns an HtmSensorModel instance.
htmModel = tempSensor.getModel()
```

Since `HtmSensorModel` isntances should not exist without corresponding `Sensor` instances, you must fetch a `Sensor` to get its accompanying `HtmSensorModel`.

## Data Storage

### Writing new data to `Sensor` stream

```python
dataPoints = [{
  "time": datetime.datetime.now(),
  "value": 84.4,
  "tags": {
    "unit": "fahrenheit"
  }
}]

# Writing data will also write the component tag to each point. Optionally, 
# additional tags can be specified with "tags={}".
tempSensor.write(dataPoints)
```

### Writing new data to `HtmSensorModel` stream

```python
# Assuming that "model" is an OPF CLAModel object...
result = model.run({
  "timestamp": timestamp,
  "value": value
})

htmModel.write(result)
```

## Data Retrieval

```python
# Returns dates of first and last data points available.
(dataStarts, dataEnds) = tempSensor.getTimeBounds()

# Returns the first 1000 points of data as dict objects.
firstData = tempSensor.getData(since=dataStarts, limit=1000)

# Returns the last 1000 points of data
lastData = tempSensor.getData(until=dataEnds, limit=1000)

# Returns aggregated mean over 10 minute time periods for entire data set.
tenMinMeanAggregated = tempSensor.getData(
  aggregation={"method": "mean", "period": "10m"}
)

# HtmSensorModel.getResults has the same function interface as Sensor.getData,
# except that the return object is a list of HtmModelResults objects, not dicts.
htmResults = htmModel.getResults()
```
