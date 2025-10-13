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

async function downloadProfile(serverCn, cn) {
    try {
        let endpoint = `/download/profiles/${serverCn}/${cn}`
        let res = await fetch(endpoint, {
            method: 'GET'
        });
        if (!res.ok) {
            let data = await res.json();
            alert('下载失败：' + data.msg);
            return;
        }

        const blob = await res.blob();
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = `${cn}.ovpn`;
        document.body.appendChild(a);
        a.click();

        document.body.removeChild(a);
        URL.revokeObjectURL(blobUrl);
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
            Object.entries(data.common_names).forEach(([serverCn, cns]) => {
                cns.sort((a, b) => a.localeCompare(b, 'en'));
                cns.forEach(cn => {
                    const row = document.createElement('tr');
                    i++;

                    const idCell = document.createElement('td');
                    idCell.textContent = i;
                    const cnCell = document.createElement('td');
                    cnCell.textContent = cn;
                    const targetServerCell = document.createElement('td');
                    targetServerCell.textContent = serverCn;
                    const downloadLinkCell = document.createElement('td');
                    const downloadLink = document.createElement('a');
                    downloadLink.href = '#';
                    downloadLink.textContent = '下载';
                    downloadLink.addEventListener('click', async (e) => {
                        e.preventDefault();
                        await downloadProfile(serverCn, cn);
                    });
                    downloadLinkCell.appendChild(downloadLink);

                    row.appendChild(idCell);
                    row.appendChild(cnCell);
                    row.appendChild(targetServerCell);
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
                const cnCell = document.createElement('td');
                cnCell.textContent = request.common_name;
                const targetServerCell = document.createElement('td');
                targetServerCell.textContent = request.server_common_name;
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
                row.appendChild(cnCell);
                row.appendChild(targetServerCell);
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
