# wf-monitor
Monitoring of workflows for NAIADES.

## Running

The script is run with the following command `python3 main.py -w [setup]`, where `[setup]` can be one of the setups. The following are implemented:

* `carouge` - monitoring of Carouge workflow
* `alicante-salinity` - monitoring of Alicante salinity workflow
* `alicante-consumption` - monitoring of Alicante consumption workflow
* `braila-anomaly` - monitoring of Braila anomaly detection workflow
* `braila-consumption` - monitoring of Braila consumption workflow
* `braila-state-analysis` - monitoring of the Braila state analysis tool workflow
* `braila-leakage` - monitoring of the Braila leakege workflow

The analysis script is run with command `python3 analysis.py`.

## Tools for Influx

Cronograph is running on IRCAI, where you can monitor Influx data.
```docker run -p 8880:8888 --network=influx_grafana_network chronograf --influxdb-url=http://influxdb:8086```
