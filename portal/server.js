const WebSocket = require('ws');
const http = require('http');
const wss = new WebSocket.Server({ port: 1207 });

wss.on('connection', function connection(ws) {
    console.log('Client connected');

    const sendLiveData = () => {
        // Запрос к серверу трансляций для получения количества зрителей
        http.get('https://live.pprfnk.tech/api/stats', (resp) => {
            let data = '';

            // A chunk of data has been received.
            resp.on('data', (chunk) => {
                data += chunk;
            });

            // The whole response has been received.
            resp.on('end', () => {
                let viewersCount = JSON.parse(data).viewers;
                let liveStatus = viewersCount > 0; // Если есть зрители, трансляция активна

                ws.send(JSON.stringify({
                    type: 'status',
                    live: liveStatus,
                    viewers: viewersCount
                }));
            });
        }).on("error", (err) => {
            console.log("Error: " + err.message);
        });
    };

    var interval = setInterval(sendLiveData, 5000);

    ws.on('close', function close() {
        console.log('Client disconnected');
        clearInterval(interval);
    });
});