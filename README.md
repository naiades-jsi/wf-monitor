# wf-monitor
Monitoring of workflows for NAIADES.

## Running

The script is run with the following command `python3 main.py -w [setup]`, where `[setup]` can be one of the setups. The following are implemented:

* `carouge` - monitoring of Carouge workflow


## Tools for Influx

Cronograph is running on IRCAI, where you can monitor Influx data.
```docker run -p 8880:8888 --network=influx_grafana_network chronograf --influxdb-url=http://influxdb:8086```
