const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
 ws_status = document.getElementById('ws_status');
document.getElementById('debug_clear_log').addEventListener('click', clearLog);

const ant_units = [];
for (let i = 0; i < 16; i++) {
    const unit = document.getElementById(`ant-unit-${i}`);
    ant_units.push(unit);
}

let isWsConnect = false;
let isCardExpandedSpec = false; 
let isCardExpandedTarget = false; 
let isCardExpandedPf = false; 

// 檢查是否為 iSmartWave 應用
const isISmartWave = window.location.pathname.includes('ismartwave');

// 更新 WebSocket 狀態的函數
function updateWsStatus(status, message) {
    ws_status.textContent = message;
    
    if (isISmartWave) {
        // iSmartWave 使用 CSS 類別
        ws_status.className = 'status-indicator';
        switch (status) {
            case 'connected':
                ws_status.classList.add('status-connected');
                ws_status.classList.remove('status-disconnected', 'status-connecting');
                break;
            case 'disconnected':
                ws_status.classList.add('status-disconnected');
                ws_status.classList.remove('status-connected', 'status-connecting');
                break;
            case 'connecting':
                ws_status.classList.add('status-connecting');
                ws_status.classList.remove('status-connected', 'status-disconnected');
                break;
        }
    } else {
        // 原始 Dashboard 使用內聯樣式
        switch (status) {
            case 'connected':
                ws_status.style.color = 'green';
                break;
            case 'disconnected':
                ws_status.style.color = 'red';
                break;
            case 'connecting':
                ws_status.style.color = 'gray';
                break;
        }
    }
}

document.getElementById("expandButtonSpec").addEventListener("click", function() {
    const card = document.getElementById("expandableCardSpec");
    if (isCardExpandedSpec) {
        card.style.position = 'relative';
        card.style.top = '';
        card.style.left = '';
        card.style.transform = '';
        card.style.zIndex = '';
        isCardExpandedSpec = false;
    } else {
        const scaleX = (window.innerWidth * 0.9) / card.offsetWidth;
        const scaleY = (window.innerHeight * 0.9) / card.offsetHeight;
        card.style.position = 'fixed';
        card.style.top = '50%';
        card.style.left = '50%';
        card.style.transform = `translate(-50%, -50%) scale(${scaleX}, ${scaleY})`;
        card.style.zIndex = '1000';
        isCardExpandedSpec = true;
    }
});
document.getElementById("expandButtonTarget").addEventListener("click", function() {
    const card = document.getElementById("expandableCardTarget");
    if (isCardExpandedTarget) {
        card.style.position = 'relative';
        card.style.top = '';
        card.style.left = '';
        card.style.transform = '';
        card.style.zIndex = '';
        isCardExpandedTarget = false;
    } else {
        const scaleX = (window.innerWidth * 0.9) / card.offsetWidth;
        const scaleY = (window.innerHeight * 0.9) / card.offsetHeight;
        card.style.position = 'fixed';
        card.style.top = '50%';
        card.style.left = '50%';
        card.style.transform = `translate(-50%, -50%) scale(${scaleX}, ${scaleY})`;
        card.style.zIndex = '1000';
        isCardExpandedTarget = true;
    }
});
document.getElementById("expandButtonPf").addEventListener("click", function() {
    const card = document.getElementById("expandableCardPf");
    if (isCardExpandedPf) {
        card.style.position = 'relative';
        card.style.top = '';
        card.style.left = '';
        card.style.transform = '';
        card.style.zIndex = '';
        isCardExpandedPf = false;
    } else {
        const scaleX = (window.innerWidth * 0.9) / card.offsetWidth;
        const scaleY = (window.innerHeight * 0.9) / card.offsetHeight;
        card.style.position = 'fixed';
        card.style.top = '50%';
        card.style.left = '50%';
        card.style.transform = `translate(-50%, -50%) scale(${scaleX}, ${scaleY})`;
        card.style.zIndex = '1000';
        isCardExpandedPf = true;
    }
});

async function main() {
    try {
        const response = await fetch('/api/get_dashboard_ws/', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({}) // 空对象作为示例
        });
        // 等待 JSON 解析
        const result = await response.json();
        const websocketUrl = result['websocket_url'];
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const ws_url = `${protocol}//` + window.location.host + websocketUrl;
        const ws = new WebSocket(ws_url);

        ws.onopen = function(event){
            console.log('Websocket 連線成功!');
            updateWsStatus('connected', 'Websocket connected!');
            isWsConnect = true;
        }
        
        ws.onmessage = function(event){
            const data = JSON.parse(event.data);
            const topic = data['topic'];
            const count = data['count'];
            const json_data = data['data'];
            const timestamp = Date.now() - data['time'];
            console.log(`Websocket 收到資料 ${topic} ${count} (${timestamp}ms)`);
            switch (topic) {
                case 'radar': {
                    fetchRadarData(json_data);
                    break;
                }
                case 'simulate': {
                    fetchRadarData(json_data);
                    break;
                }
                case 'spec': {
                    fetchSpecData(json_data);
                    break;
                }
                case 'message': {
                    fetchMessageData(json_data);
                    break;
                }
                case 'target': {
                    fetchTargetData(json_data);
                    break;
                }
                case 'pf': {
                    fetchPfData(json_data);
                    break;
                }
                case 'ant':{
                    fetchAntData(json_data);
                    break;
                }
            }
        }

        ws.onclose = function(event){
            console.log('Websocket 連線中斷！重新連線中');
            updateWsStatus('disconnected', 'Websocket reconnecting...');
            clearRadarData();
            isWsConnect = false;
        }
    
        
    } catch (error) {
        console.log('Websocket 連線失敗，請檢查伺服器狀態！');
        updateWsStatus('disconnected', 'Websocket server disconnect');
        return;
        // throw error;
    }    
}

async function fetchRadarData(json_data) {
    const statusDiv = document.getElementById('polygon-status');
    statusDiv.innerHTML = `${json_data['svg']}`;
  }
async function clearRadarData() {
    const statusDiv = document.getElementById('polygon-status');
    statusDiv.innerHTML = ``;
  }

async function fetchSpecData(json_data) {
    const base64Image = json_data['fig'];
    const imgElement = document.getElementById('spectrogramDisplay');
    const card = imgElement.parentNode;
    if (isCardExpandedSpec) {
        imgElement.src = `data:image/png;base64,${base64Image}`;
        return;
    }
    imgElement.src = `data:image/png;base64,${base64Image}`;
    const cardWidth = card.clientWidth*0.97;
    const cardHeight = card.clientHeight*0.97;
    const scale = Math.min(cardWidth / imgElement.naturalWidth, cardHeight / imgElement.naturalHeight);
    imgElement.style.width = `${scale * imgElement.naturalWidth}px`;
    imgElement.style.height = `${scale * imgElement.naturalHeight}px`;
}

async function fetchSpecData_(json_data) {
    const base64Image = json_data['fig'];
    const canvas = document.getElementById('spectrogramDisplay');
    const parent = canvas.parentElement;

    canvas.width = parent.clientWidth*0.98;
    canvas.height = parent.clientHeight*0.98;

    canvas.style.width = parent.offsetWidth + 'px';
    canvas.style.height = parent.offsetHeight + 'px';

    // 設定 canvas 的內部繪圖尺寸，保證高解析度
    canvas.width = parent.offsetWidth * window.devicePixelRatio;
    canvas.height = parent.offsetHeight * window.devicePixelRatio;

    const context = canvas.getContext('2d');
    const img = new Image();
    img.src= `data:image/webp;base64,${base64Image}`;
    img.onload = () => {
        drawImageScaled(context, img, canvas.width / window.devicePixelRatio, canvas.height / window.devicePixelRatio);
    };
    
}
function drawImageScaled(ctx, img, canvasWidth, canvasHeight, isExapnd) {
    const imgAspect = img.width / img.height;
    const canvasAspect = canvasWidth / canvasHeight;
  
    let drawWidth, drawHeight;
    let offsetX = 0, offsetY = 0;
  
    // 確定繪製大小
    if (imgAspect > canvasAspect) {
      drawWidth = canvasWidth;
      drawHeight = canvasWidth / imgAspect;
      offsetY = (canvasHeight - drawHeight) / 2; // 垂直置中
    } else {
      drawHeight = canvasHeight;
      drawWidth = canvasHeight * imgAspect;
      offsetX = (canvasWidth - drawWidth) / 2; // 水平置中
    }
    if (isExapnd){
        drawHeight = canvasHeight;
        drawWidth = canvasWidth;
    }
  
    // 繪製圖片
    ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
  }

async function fetchAntData(json_data) {
    ant_units.forEach((unit, index) => {
        const power_element = unit.querySelector('.power');
        const received_element = unit.querySelector('.received-ant, .received-ant-received');
        const ant_element = unit.querySelector('.ant-id, .ant-id-selected');
        power_element.textContent = json_data['powers'][index];
        if (json_data['received'][index] != null){
            received_element.textContent = json_data['received'][index];
            received_element.className = 'received-ant-received';
        }
        else{
            received_element.textContent = '';
            received_element.className = 'received-ant';
        }
        if (json_data['selected'].includes(index)){
            ant_element.className = 'ant-id-selected';
        }
        else{
            ant_element.className = 'ant-id';
        }
    });
}

async function fetchMessageData(json_data) {
    const data = json_data;
    const log_content = document.getElementById('log_content');
    const logItem = document.createElement("div");
    logItem.textContent = `[${data['level']}] ${data['text']}`;
    logItem.style.whiteSpace = "pre-wrap";
    log_content.appendChild(logItem);
    
    if (document.getElementById('debug_auto_scroll').checked == true){
        log_content.scrollTop = log_content.scrollHeight;
    }
}

function clearLog(){
    const log_content = document.getElementById('log_content');
    while (log_content.firstChild) {
        log_content.removeChild(log_content.firstChild);
    }
    console.log('Clear log.');
}

async function fetchTargetData(json_data) {
    const base64Image = json_data['fig'];
    const imgElement = document.getElementById('targetDisplay');
    const card = imgElement.parentNode;
    if (isCardExpandedTarget) {
        imgElement.src = `data:image/png;base64,${base64Image}`;
        return;
    }
    imgElement.src = `data:image/png;base64,${base64Image}`;
    const cardWidth = card.clientWidth*0.97;
    const cardHeight = card.clientHeight*0.97;
    const scale = Math.min(cardWidth / imgElement.naturalWidth, cardHeight / imgElement.naturalHeight);
    imgElement.style.width = `${scale * imgElement.naturalWidth}px`;
    imgElement.style.height = `${scale * imgElement.naturalHeight}px`;
}

async function fetchPfData(json_data) {
    const base64Image = json_data['fig'];
    const imgElement = document.getElementById('pfDisplay');
    const card = imgElement.parentNode;
    if (isCardExpandedPf) {
        imgElement.src = `data:image/png;base64,${base64Image}`;
        return;
    }
    imgElement.src = `data:image/png;base64,${base64Image}`;
    const cardWidth = card.clientWidth*0.97;
    const cardHeight = card.clientHeight*0.97;
    const scale = Math.min(cardWidth / imgElement.naturalWidth, cardHeight / imgElement.naturalHeight);
    imgElement.style.width = `${scale * imgElement.naturalWidth}px`;
    imgElement.style.height = `${scale * imgElement.naturalHeight}px`;
}

async function init() {
    if (isWsConnect){
        return;
    }
    else{
        main();
    }
}

setInterval(init, 5000);
init();
