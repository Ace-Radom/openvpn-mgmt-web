async function initRequestProfileServerSelectOptions(select) {
    try {
        let res = await fetch('/api/list/servers', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        let data = await res.json();
        if (data.success) {
            data.common_names.forEach(cn => {
                const option = document.createElement("option");
                option.text = cn;
                option.value = cn;
                select.appendChild(option);
            });
        }
        else {
            alert('获取服务器列表失败：' + data.msg);
        }
    } catch (err) {
        alert('请求失败：' + err.message);
    }
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
    } catch (err) {
        alert('请求失败：' + err.message);
    }
}

async function refreshProfilesTable(tbody) {
    try {
        let res = await fetch('/api/list/profiles', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        let data = await res.json();
        if (data.success) {
            tbody.innerHTML = '';
            let i = 0;
            Object.entries(data.common_names).forEach(([server_cn, cns]) => {
                cns.forEach(cn => {
                    const row = document.createElement('tr');
                    i++;

                    const idCell = document.createElement('td');
                    idCell.textContent = i;
                    const targetServerCell = document.createElement('td');
                    targetServerCell.textContent = server_cn;
                    const cnCell = document.createElement('td');
                    cnCell.textContent = cn;
                    const downloadLinkCell = document.createElement('td');
                    downloadLinkCell.textContent = '下载';

                    row.appendChild(idCell);
                    row.appendChild(targetServerCell);
                    row.appendChild(cnCell);
                    row.appendChild(downloadLinkCell);

                    tbody.appendChild(row);
                });
            });
        }
        else {
            alert('刷新 Profiles 失败：' + data.msg);
        }
    } catch (err) {
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
                if (request.is_rejected) {
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
            alert('刷新 Profiles 申请失败：' + data.msg);
        }
    } catch (err) {
        alert('请求失败：' + err.message);
    }
}

if (document.getElementById('userContainer')) {

    const profilesTable = document.getElementById('profilesTable');
    const profilesTableTbody = profilesTable.getElementsByTagName('tbody')[0];
    const requestProfileServerSelect = document.getElementById('requestProfileServerSelect');
    const requestProfileNumInput = document.getElementById('requestProfileNumInput');
    const requestProfileButton = document.getElementById('requestProfileButton');
    const profileRequestsTable = document.getElementById('profileRequestsTable');
    const profileRequestsTableTbody = profileRequestsTable.getElementsByTagName('tbody')[0];

    initRequestProfileServerSelectOptions(requestProfileServerSelect);
    refreshProfilesTable(profilesTableTbody);
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
