<p align="center">
  <img alt="drdroidlogo" src="https://uploads-ssl.webflow.com/642ad9ebc00f9544d49b1a6b/642ad9ebc00f9514ad9b1ab8_drdroidlogo.png">
</p>

- [ ] Todo: Define a deployable sandbox config that works in a much smaller machine (say 2GB or 4GB memory).

## Kenobi -- Open Source Log-to-Metrics & Log-to-Funnels platform

Kenobi helps you proactively monitor your application by defining correlations in your logs.

## Capabilities

### 1. Log to events:
You can buffer a stream of logs to Kenobi and define filters and transformations on the platform using the GROK parser built into the platform.

### 2. Event Sequences: 
Once you have events flowing in, you can define different sequences by joining them. Here are some of the examples:
1. **2-step sequence**: Define a relation, A &rarr; B with A being primary and B being secondary event (defined as a monitor)
    ![img.png](img.png)
1. **n-step sequence**: Define a set of events A<sub>1</sub> &rarr; A<sub>2</sub> &rarr; ... &rarr; A<sub>n</sub> that are expected to happen sequentially (defined as a funnel)
   - [ ] todo -- add recording here.
   ![img_2.png](img_2.png)
1. **n-step trees**: Define a set of events that are not necessarily sequential but inter-related (defined as an entity)
   - [ ] todo -- add recording here
   ![img_1.png](img_1.png)
   

### 3. Metrics:
Define aggregations on your events and sequences. Some of the allowed metric types include:
* Transition time and success rate between nodes in an event sequence or tree
* Aggregation functions on any attribute within an event
* Aggregation functions on any attribute within an event, grouped by another (enum) attribute in any other event

### 4. Alerting Rule Engine:
Kenobi enables you to create rules over your events and event sequences. Here's how the rule engine is defined:

* Event level rules:
  * Occurrence of an event
  * Occurrence of an event, more than n times (threshold)
* Sequence level rules:
  * Change in aggregated drop % between consecutive nodes
  * Change in transition times between consecutive nodes (aggregated as well as event-level configurations)
* Metric level rules:
  * Change in metric value against a static threshold
  * Change in metric value against a benchmark (previous timeline)


Here are some rules that would be possible in the platform:
* Send me an alert if node A<sub>2</sub> does not happen after node A<sub>1</sub> for every instance where attribute_value=specific_value.
* Send me an alert if more than 5% of the nodes "between" node A<sub>1</sub> and node A<sub>n</sub> are stuck at a specific node.
* Send me an alert if sequence is stuck at node A<sub>i</sub> for more than stipulated duration.

Kenobi can push alerts to itself, email and slack currently.

Sounds useful?

Play around in demo environment 👇🏽

## Exploring Kenobi in a Sandbox

For the purpose of this sandbox, we have created a sample payment application. In the sandbox, you will be able to see logs from one such application, and how we can transform it into funnels and charts.

- **Cloud Sandbox:** Play around in the cloud sandbox [here](https://sandbox.drdroid.io/) (email ID required - we will not share your PII with any external party or send you unnecessary emails)
- **Self-hosted Sandbox:** Spin a demo in your own environment, run the following on a Linux machine with Docker (recommended 2GB or 4GB memory)

 ```bash 
  /bin/bash docker_deploy.sh
 ```
- [ ] Deployment commands are insufficient. Will need your inputs here.

### Integrating your log stream to Kenobi

Before being able to create funnels, metrics or rules, you need to parse data into a kenobi readable format. 

You can stream application logs into Kenobi using:
* Native events SDK (this SDK is compatible to the events format expected on the platform)

In case you want to stream from your existing sources, you can read the following documentations:
* [Cloudwatch Logs](https://docs.drdroid.io/docs/connector-cloudwatch)
* [Segment events](https://docs.drdroid.io/docs/connector-segment)


### Cloud Hosting
Doctor Droid supports a robust cloud platform for Kenobi. If you'd like to use the cloud platform instead of managing the platform in-house, sign up on our [website](https://app.drdroid.io/signup) or [book a demo](https://calendly.com/siddarthjain/catchup-call-clone).


### License
This repo is available under the [MIT license](https://github.com/DrDroidLab/kenobi/blob/main/LICENSE).