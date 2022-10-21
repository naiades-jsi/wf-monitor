# wf-monitor
Monitoring of workflows for NAIADES.

## Running

In WF_MONITOR create a file config_mail.json (look at config_mail_example.json). To get the password (16-character code), you have to go through [2-Step Verification](https://myaccount.google.com/signinoptions/two-step-verification/enroll-welcome). Then go to [App Passwords](https://myaccount.google.com/u/1/apppasswords) and create a new password.
The script is run with the following command `python3 scheduler.py`.
A mail reporting ... is sent to the receiver specified in the `configs/config_mail.json` file.
An example file is located in `configs/config_mail_example.json`.

### Other

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

## API times

**Braila**

|API update		        |Update time	        |Scheduled      |Expected delay |
|-----------------------|-----------------------|---------------|---------------|
|Pressure-5770		    |05:30	                |06:00          |1h             |
|Pressure-5771		    |05:30	                |06:00          |1h             |
|Pressure-5772		    |05:30	                |06:00          |1h             |
|Pressure-5773		    |05:30	                |06:00          |1h             |
|Water Demand 		    |every 2h (6:30; 8:30…) |11:00          |2h             |
|Noise sensor 2182		|11:00	                |12:00          |2h             |
|Noise sensor 5980		|11:00	                |12:00          |2h             |
|Noise sensor 5981		|11:00	                |12:00          |2h             |
|Noise sensor 5982		|11:00	                |12:00          |2h             |

**Alicante**

|API update             |Update time	        |Scheduled     |Expected delay  |
|-----------------------|-----------------------|--------------|----------------|
|Weather-observed	    |20:00                  |10:00         |3h              |
|Rambla-flow		    |22:00                  |10:00         |13h             |
|Autobuses-flow		    |22:00                  |10:00         |13h             |
|Montaneta-flow		    |21:30                  |10:00         |13h             |
|Benalua-flow		    |22:00                  |10:00         |13h             |
|Alipark-flow		    |21:30                  |10:00         |13h             |
|Diputacion-flow		|21:30                  |10:00         |13h             |
|Mercado-flow		    |03:30                  |10:00         |31h             |
|EA001-202		        |22:00                  |01:00         |16h             |
|EA002-26		        |22:00                  |01:00         |16h             |
|EA003-21		        |22:00                  |01:00         |16h             |
|EA004-21		        |22:00                  |01:00         |16h             |
|EA005-21		        |22:00                  |01:00         |16h             |
|EA008-36		        |22:00                  |01:00         |16h             |
|EA001-36		        |22:00                  |01:00         |16h             |
|EA007-36		        |22:00                  |01:00         |16h             |
|EA003-36		        |22:00                  |01:00         |16h             |

**Carouge**

|API update		        |Update time	        |Scheduled     |Expected delay  |
|-----------------------|-----------------------|--------------|----------------|
|Weather-observed       |??	                    |12:00         |??              |
|FlowerBeds		        |every hour             |12:00         |1h              |
