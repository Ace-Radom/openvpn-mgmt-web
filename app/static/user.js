let serverCns = null;
let serverCnsLoaded = false;

const loadServerCnsPromise = new Promise(async (resolve) => {
    try {
        let res = await fetch('/api/list/servers', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        let data = await res.json();
        if (data.success) {
            serverCns = data.common_names;
            serverCnsLoaded = true;
        }
        else {
            alert('获取服务器列表失败：' + data.msg);
        }
    } catch(err) {
        alert('请求失败：' + err.message);
    }
    resolve();
});

function initRequestProfileServerSelectOptions(select) {
    serverCns.forEach(cn => {
        const option = document.createElement("option");
        option.text = cn;
        option.value = cn;
        select.appendChild(option);
    });
}

async function requestProfile(serverCn, num) {
    try {
        let res = await fetch('/api/reqprofile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ server_common_name: serverCn, num })
        });
        let data = await res.json();
        if (data.success) {
            alert('申请成功');
        }
        else {
            alert('申请失败：' + data.msg);
        }
    } catch(err) {
        alert('请求失败：' + err.message);
    }
}

async function refreshProfileRequestsTable(tbody) {
    try {
        let res = await fetch('/api/list/profilereqs', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        let data = await res.json();
        if (data.success) {
            tbody.innerHTML = '';
            let i = 0;
            data.requests.forEach(request => {
                const row = document.createElement('tr');
                i++;
    
                const idCell = document.createElement('td');
                idCell.textContent = i;
                const targetServerCell = document.createElement('td');
                targetServerCell.textContent = request.server_common_name;
                const cnCell = document.createElement('td');
                cnCell.textContent = request.common_name;
                const requestTimeCell = document.createElement('td');
                requestTimeCell.textContent = convertTimestampToString(request.request_time_ts, true);
                const statusCell = document.createElement('td');
                if (data.is_rejected) {
                    statusCell.textContent = '审核未通过';
                }
                else {
                    statusCell.textContent = '等待审核';
                }
    
                row.appendChild(idCell);
                row.appendChild(targetServerCell);
                row.appendChild(cnCell);
                row.appendChild(requestTimeCell);
                row.appendChild(statusCell);
    
                tbody.appendChild(row);
            });
        }
        else {
            alert('刷新 Profiles 失败：' + data.msg);
        }
    } catch(err) {
        alert('请求失败：' + err.message);
    }
}

if (document.getElementById('userContainer')) {

    const requestProfileServerSelect = document.getElementById('requestProfileServerSelect');
    const requestProfileNumInput = document.getElementById('requestProfileNumInput');
    const requestProfileButton = document.getElementById('requestProfileButton');
    const profileRequestsTable = document.getElementById('profileRequestsTable');
    const profileRequestsTableTbody = profileRequestsTable.getElementsByTagName('tbody')[0];

    loadServerCnsPromise.then(() => {
        if (serverCnsLoaded) {
            initRequestProfileServerSelectOptions(requestProfileServerSelect);
        }
    });
    refreshProfileRequestsTable(profileRequestsTableTbody);

    requestProfileButton.addEventListener('click', async function () {
        let serverCn = requestProfileServerSelect.value;
        if (serverCn === "") {
            alert('请选择服务器。');
            return;
        }
        let num = Number(requestProfileNumInput.value);
        await requestProfile(serverCn, num);
        await refreshProfileRequestsTable(profileRequestsTableTbody);
    });

}
