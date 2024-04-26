const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 1207 });

let activeConnections = 0; // Счетчик активных подключений

wss.on('connection', function connection(ws)
{
    activeConnections++; // Увеличиваем счетчик при новом подключении
    console.log('Client connected. Total connections: ', activeConnections);

    ws.on('close', function close() {
        activeConnections--; // Уменьшаем счетчик при закрытии подключения
        console.log('Client disconnected. Total connections: ', activeConnections);
    });

    const sendLiveData = () => {
        var liveStatus = activeConnections > 0; // Трансляция активна, если есть подключения
        var viewersCount = activeConnections; // Количество зрителей равно количеству подключений

        var data = JSON.stringify(
            {
            type: 'status',
            live: liveStatus,
            viewers: viewersCount
        });

        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN)
            {
                client.send(data, function error(err)
                {
                    if (err)
                    {
                        console.log('Failed to send data', err);
                    }
                });
            }
        });
    };

    // Отправка данных каждые 5 секунд
    var interval = setInterval(sendLiveData, 5000);

    ws.on('close', function close() {
        clearInterval(interval);
    });
});

console.log('WebSocket server started on port 1207');