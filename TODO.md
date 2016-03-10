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
- Standards for aggregation of fast streaming data
- Tools to create retention policies and continuous queries at different aggregation periods for HTM data input feeds

# TODO

1. Create an extension of the `InfluxDBClient` class in the `influxdb==2.12.0` python library.
1. Create a `Sensor` class to represent a `measurement` with a `tag="component"`.
1. Create a `HTMSensorModel` class to represent the HTM results while processing a `Sensor`.
1. 

# Object Model

`Sensor`: An object in spacetime emitting data at any interval. Static structure.
`HtmSensorModel`: Attached to a `Sensor` and stores HTM results, including all the data in the `HtmModelResults` object.
`HtmModelResults`: Contains all data in an [OPF](https://github.com/numenta/nupic/tree/master/src/nupic/frameworks/opf) model result. 
