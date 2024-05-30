import { WebSocketServer } from 'ws';
import { readFile } from 'fs/promises';

// 读取静态数据
const staticData = JSON.parse(await readFile(new URL('./data.json', import.meta.url)));

// 创建 WebSocket 服务器
const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', ws => {
    console.log('Client connected');

    // 发送静态数据
    let index = 0;

    const sendData = () => {
        if (index < staticData['time'].length) {
            ws.send(JSON.stringify({
                'data': staticData['hcn'].map(d => d[index]),
                'time': staticData['time'][index][0]
            }));
            index++;
            setTimeout(sendData, 50); // 每秒发送一条数据
        } else {
            ws.close();
        }
    };

    sendData();

    ws.on('close', () => {
        console.log('Client disconnected');
    });
});

console.log('WebSocket server is running on ws://localhost:8080');
