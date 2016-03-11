![Influx HTM Logo](img/influxhtm.png)

[`influxhtm`](https://github.com/rhyolight/influx.htm) is a data interface for [InfluxDB](https://influxdata.com/time-series-platform/influxdb/) that makes it easier to use with [Hierarchical Temporal Memory (HTM)](http://numenta.com/learn/principles-of-hierarchical-temporal-memory.html) systems like [NuPIC](https://github.com/numenta/nupic), [HTM.Java](https://github.com/numenta/htm.java), and [Comportex](https://github.com/nupic-community/comportex). 

## The World as a Temporal Data Stream

Our world is a constant stream of real-time data made up of many billions of small data feeds. Tools are emerging to help us tap into those streams and make use of this data in real-time. InfluxDB is one of these tools, allowing users to store data streams quickly and efficiently into a system that is easily queryable and performant. 

HTM systems can provide real-time analysis when attached to live temporal data streams, but HTM runtimes can be tedious to configure. We need a common interface for streaming data storage, retrieval, and aggregation for HTM systems, allowing them to contribute their analysis results back into the stream itself.  `influxhtm` provides a concrete example implementation of that interface. 

## Objectives of `influxhtm`

I want to enable easier experimentation with HTM on live data streams. Almost all data stored in a time-series database like InfluxDB is well-suited for HTM analysis. `influxhtm` could potentially be used to add HTM anomaly detection and prediction capabilities to any InfluxDB system.

1. Expose individual data streams as sensor objects that can have HTM models attached to them
1. Easy way to create HTM models for sensors, process their data, and store the results
1. The underlying HTM system is not linked to this interface
1. HTM results are accessed as a part of the sensor interface
1. Enable both live HTM processing and batch processing of time slices of sensor data
1. Allow HTM users a platform for experimentation with different model params over and over against the same data sensors
1. Provide an API for the merge of raw sensor data (aggregated or not) with HTM results for easy plotting


## Usage

### The Client

The client object is the gateway to the rest of the `influxhtm` API.

```python
client = InfluxHtmClient(
  "database-name",
  host="localhost",
  port=8086,
  username="username",
  password="password",
  ssl=True
)
```

If the credentials above are not passed into the constructor, `influxhtm` will look for the credentials in the following environment variables:

```sh
INFLUX_HOST=127.0.0.1
INFLUX_PORT=8086
INFLUX_USER=username
INFLUX_PASS=password
INFLUX_SSL=1
```

### Sensors

A *Sensor* in `influxhtm` is a series of data with a unique measurement and component. The measurement represents the value being measured, like `power`, `temperature`, `motion`, `contact`, etc. The component is an identifier for a sensor that is emitting a measurement in the form of data fields. A component might be called `coffee-machine` or `hallway-motion`. It represents a physical object (usually) collecting and emitting data. To create a Sensor, you must have both.

**To create a `Sensor` and store data:**

```python
sensor = client.createSensor(
  measurement="power", component="coffee-machine"
)
sensor.write({
  "time": datetime.datetime.now(),
  "value": 23.33
})
```

Currently, sensors only support one field called `value` to be written.

**To list current sensors:**

```python
for sensor in client.listSensors():
  print sensor
```

The [`Sensor`](influxhtm/sensor.py) object has an interface that allows data retreival, storage, and the creation of an HTM model representation in InfluxDB.

### HtmSensorModels

This program does not actually *run* HTM models. That part is up to the user. This program exposes an interface for easy data retrieval and the storage of HTM results in a way that links them to the input data, allowing the easy experimentation with many model definitions (different parameters and different data aggregations).

```python
htmModelStore = sensor.createHtmModel("unique-id")

for point in sensor.getData(limit=1000):
  # Process each data point through an HTM here.
  results = myHtmModel.run(point)
  htmModelStore.writeResult(results)
```
### Getting data and predictions

The `Sensor` interface has a method for retrieving all input data and HTM results in the same data structure for easy plotting.

```python
data = sensor.getCombinedSensorData(since=oneWeekAgo, aggregation="10m")
```

If there an HTM model exists within `influxhtm` for the given sensor, the `data` object will contain columns and values for anomalies and predictions.
