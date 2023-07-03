# Airport Stats Reporter
### TL;DR - Queries for arrived and departed flights and reports data to Honeycomb

This project is meant to populate a Honeycomb dataset with flight reports from 
AeroAPI.  By sending up flattened wide flight event data we should be able to easily
* **Watch trending flight performance over time.**  Ex. number of delayed flights, severity
of delays, number of cancellations, etc. with a simple Honeycomb dashboard
* **Alert on flight perf degradation** When delays and cancellations start piling up, this
should be easily linkable to whatever webhooks we want via Honeycomb triggers. 
* **Break down performance by {all the things}.** With wide data in place, we should be
able to see performance breakdowns by Airline, originating (or destination) airport, 
time of day, route, etc etc.  This part will be a fun pattern matching exercise. 

## Arch & Costs
Architecture here is real basic (and real free).

#### Flight API in use is [FlightAware's AeroAPI](https://flightaware.com/commercial/aeroapi/).  
Free tier supports up to 10 requests per minute.  We're running on a once-per-minute cron, so 
nothing to worry about here. 

#### Data storage and visualization is through [Honeycomb](https://www.honeycomb.io/).
Free tier here supports 20 million events per month.  Initially running this for my 
own use covering KSEA, which is doing ~35,000 flights per month.  Plenty of headroom.

#### Execution is run via [Github Actions](https://github.com/features/actions)
As a public repository, GH actions are free, so the scheduled cron (1x minute) will
run at no cost on Github hosted runners. 


## Accepted shortcomings
This is mostly a POC + some fun trend data for my own use.  As such, it's not really that 
accurate.  The most obvious failing here is that we're doing a lookback of 6m for flights 
even though we're running every 5m.  This will help cover some weird time boundary and 
downtime conditions (none of the above services offer an amazing availability SLA), in 
exchange for some data duplication (up to 2x per flight).  We could be a bit smarter here 
and just store the last successful execution time somewhere (maybe even in GHA), but 
that's a project for another day.