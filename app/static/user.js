async function requestProfile(server_cn, num) {
    let res = await fetch('/api/reqprofile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ server_common_name: server_cn, num })
    });
    let data = await res.json();
    if (data.success) {
        alert('申请成功');
    }
    else {
        alert('申请失败：' + data.msg);
    }
}

async function refreshProfileStatusTable(tbody) {
    // TODO: fetch existing profiles
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
            console.log('1')
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
            const downloadCell = document.createElement('td');
            downloadCell.textContent = '';

            row.appendChild(idCell);
            row.appendChild(targetServerCell);
            row.appendChild(cnCell);
            row.appendChild(requestTimeCell);
            row.appendChild(statusCell);
            row.appendChild(downloadCell);

            tbody.appendChild(row);
        });
    }
    else {
        alert('刷新 Profiles 失败：' + data.msg);
    }
}

if (document.getElementById('userContainer')) {

    const requestProfileNumInput = document.getElementById('requestProfileNumInput');
    const requestProfileButton = document.getElementById('requestProfileButton');
    const profileStatusTable = document.getElementById('profileStatusTable');
    const profileStatusTableTbody = profileStatusTable.getElementsByTagName('tbody')[0];

    refreshProfileStatusTable(profileStatusTableTbody);

    requestProfileButton.addEventListener('click', function () {
        let num = Number(requestProfileNumInput.value)
        requestProfile('debug', num)
    });

}
