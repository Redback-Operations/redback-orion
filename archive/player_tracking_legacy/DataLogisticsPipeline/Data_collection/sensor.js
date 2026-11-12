main();


function main() {
    const mqtt = require('mqtt');

    // -----------------------------------------------------------
    // Connect to the message broker
    const client = mqtt.connect(
        {
            host: 'mosquitto',
            port: 1883
        }
    );
    // -----------------------------------------------------------


    // -----------------------------------------------------------
    // Read csv
    let collectedData = (require("fs").readFileSync("./demo_data.csv", "utf8")).split("\r");
    collectedData.shift();
    // -----------------------------------------------------------


    // Once connected ...
    client.on('connect', () => {

        // Sensor connected!
        console.log('Sensor '+ process.env.HOSTNAME + ' is now connected to the MQTT broker');

        publishCollectedData(collectedData, 'Image', client);

    });

}

/**
 * Every 10 seconds publish a message!
 * @param collectedData
 * @param topic
 * @param client
 * @return void
 */
function publishCollectedData(collectedData, topic, client){

    let i = 0; // Counter to iterate the collected data

    setInterval(() => {

        let imageId = i++ % collectedData.length;

        const message = JSON.stringify({
            "sensorId": process.env.HOSTNAME,
            "image": collectedData[imageId],
            'collectedAt': new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '')
        });

        client.publish(topic, message, { qos: 0 }, (error) => {
            if (error) {
                console.error(error);
            }
            else{
                console.log("Sensor " + process.env.HOSTNAME + " has now sent a message to the server!");
            }
        });

    }, 10 * 1000);
}
