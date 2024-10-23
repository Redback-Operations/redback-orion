require('dotenv').config();
const username = process.env.MONGODB_USER;
const password = process.env.MONGODB_PASSWORD;

const mqtt = require('mqtt')
const mongoose = require('mongoose');
const kafka = require("kafka-node");

const Sensor = mongoose.model('Sensor', new mongoose.Schema(
    {
        image: Number,
        collected_at: Date,
        metadata: {
            sensor_id: String
        }
    },
    {
        timeseries: {
            timeField: 'collected_at',
            metaField: 'metadata',
            granularity: 'seconds',
        },
    }
));


const ModelPrediction = mongoose.model('Model_predictions', new mongoose.Schema(
    {
        date: Date,
        y_hat: Number,
        y_hat_lower: Number,
        y_hat_upper: Number,
        metadata: {
            sensor_id: String,
        }
    },
    {
        timestamps: true,
        timeseries: {
            timeField: 'created_at',
            metaField: 'metadata',
            granularity: 'seconds',
        },
    }
));



main();

/**
 * Main function
 * @return void
 */
function main(){
    // Connect to the database
    mongoose.connect('mongodb://'+username + ':' + password + '@mongo:27017/server?authSource=' + username);

    // Connect to the mqtt broker
    const mqttClient = mqtt.connect(
        {
            host: 'mosquitto',
            port: 1883
        }
    );

    // Connect to Kafka
    const kafkaClient = new kafka.KafkaClient({kafkaHost: "kafka:9092"});
    mqttClient.on('connect', function (){
        console.log("The server is now connected to the MQTT broker!");
        mqttClient.subscribe('image', subscribeCallback);

        const kafkaClientForTheProducer = new kafka.KafkaClient({kafkaHost: "kafka:9092"});
        const kafkaProducer = new kafka.Producer(kafkaClientForTheProducer);

        // Listen to the broker
        mqttClient.on('message', processMQTTMessage(kafkaProducer));

    });

    kafkaClient.on('ready', () => {
        console.log("The server is now waiting for the results of the analysis!");
        const kafkaConsumer = new kafka.Consumer(kafkaClient, [{topic: 'analytics_results'}]);
        kafkaConsumer.on('message', processKafkaMessage);
    });



}

/**
 * The returned function is executed when the server receives a new message from the MQTT.
 * Saves the received data in the database.
 * Sends the received data to the analytics module.
 * @param kafkaProducer
 * @return function
 */
function processMQTTMessage(kafkaProducer){
    return (topic, message) => {
        // Message received :)

        // Get json
        const data = JSON.parse(message.toString());

        console.log("Server: Message received from sensor " + data.sensorId);

        // Store sensor's collected data
        Sensor.create(
            {
                collected_at: data.collectedAt,
                image: data.image,
                metadata: {
                    sensor_id: data.sensorId
                }
            },
            createCallback
        );

        // Send the received data to the analytics module
        kafkaProducer.send([{
            topic: 'analytics',
            messages: JSON.stringify({
                v: data.image,
                ts: data.collectedAt,
                sensor: data.sensorId,
            })
        }], sendCallback(data.sensorId));


    };
}


/**
 * This function is executed when the server receives a new message from the Kafka broker.
 * Saves the data received in the database.
 * @param message
 */
function processKafkaMessage(message){
    message = JSON.parse(JSON.parse(message.value))['0'];
    console.log("Server: Message received from the analytics module!");

    // Store predictions!
    ModelPrediction.create(
        {
            date: message.ds,
            y_hat: message.yhat,
            y_hat_lower: message.yhat_lower,
            y_hat_upper: message.yhat_upper,
            metadata: {
                sensor_id: message.sensor,
            }
        },
        createCallback
    )

}


/**
 * MQTT subscribe callback function.
 * @param error
 * @param content
 */
function subscribeCallback(error, content){
    if(error){
        console.error(error);
    }
    else{
        console.log(`The server is now subscribed to image topic!`);
    }
}

/**
 * Mongoose create callback function.
 * @param err
 * @param doc
 */
function createCallback(err, doc){
    if (err) {
        console.error("Couldn't store the sensor data");
        console.error(err);
    }
}


/**
 * Kafka send callback function
 * @param sensorId
 * @return {(function(*, *): void)|*}
 */
function sendCallback(sensorId){
    return (error, result) => {
        if(error){
            console.error(error);
        }
        else{
            console.log('The server has now sent data from the sensor ' + sensorId + ' to model analysis!' )
        }
    };
}


