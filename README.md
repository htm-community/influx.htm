![Influx HTM Logo](img/influxhtm.png)

[`influxhtm`](https://github.com/rhyolight/influx.htm) is a data interface for InfluxDB that makes it easier to use with [Hierarchical Temporal Memory (HTM)](http://numenta.com/learn/principles-of-hierarchical-temporal-memory.html) systems. 

## The World as a Temporal Data Stream

Our world is a constant stream of real-time data made up of many billions of small data feeds. Many tools are emerging to help us humans tap into those streams and make use of this data in real-time. InfluxDB is one of these tools, allowing users to store data streams quickly and efficiently into a system that is easily queryable and performant. 

HTM systems can provide real-time analysis when attached to live temporal data streams, but HTM runtimes can be tedious to set up to be resilient. There is a need to expose a common interface for streaming data storage and retrieval and aggregation for HTM systems, allowing them to contribute their analysis results for sensors in the stream back into the stream itself. 

## Objectives of `influxhtm`

I want to enable easier experimentation with HTM on live data streams. Given the fact that almost all data stored in a time-series database like InfluxDB is well-suited for HTM analysis, `influxhtm` could potentially be used to add HTM anomaly detection and prediction capabilities to any InfluxDB system.

1. Expose individual data streams as sensor objects that can have HTM models attached to them
1. Easy way to create HTM models for sensors, process their data, and store the results
1. HTM results are accessed as a part of the sensor interface
1. Enable both live HTM processing and batch processing of time slices of sensor data
1. Allow HTM users a platform for experimentation with different model params over and over against the same data sensors
1. Provide an API for the merge of raw sensor data (aggregated or not) with HTM results for easy plotting


