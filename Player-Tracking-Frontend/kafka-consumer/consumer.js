const { Kafka } = require("kafkajs");
const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());

let latestResult = null; // stores the latest Kafka result

const kafka = new Kafka({
  clientId: "frontend-consumer",
  brokers: ["redback.it.deakin.edu.au:9092"]
});

const consumer = kafka.consumer({ groupId: "frontend-result-group" });

const run = async () => {
  await consumer.connect();
  await consumer.subscribe({ topic: "results_topic", fromBeginning: false }); // or 'heatmap_results'

  await consumer.run({
    eachMessage: async ({ message }) => {
      console.log("Kafka message received");
      try {
        latestResult = JSON.parse(message.value.toString());
      } catch {
        latestResult = { raw: message.value.toString() };
      }
    }
  });
};

run().catch(console.error);

// Serve result over HTTP
app.get("/latest-result", (req, res) => {
  if (!latestResult) return res.status(404).json({ message: "No result yet" });
  res.json(latestResult);
});

app.listen(4000, () => {
  console.log("!!Kafka Result Server running on http://localhost:4000");
});

