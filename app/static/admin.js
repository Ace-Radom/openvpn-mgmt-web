const REGEX_USERNAME = /^[A-Z][a-z]*$/;

function validateUsername(username) {
    return REGEX_USERNAME.test(username);
}

async function operateProfileRequest(serverCn, cn, op) {
    try {
        let res = await fetch('/api/operate/profilereq', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "server_common_name": serverCn,
                "common_name": cn,
                "operation": op
            })
        });
        let data = await res.json();
        if (data.success) {
            alert('操作成功');
        }
        else {
            alert('操作失败：' + data.msg);
        }
    } catch (err) {
        alert('请求失败：' + err.message);
    }
}

async function approveProfileRequest(serverCn, cn) {
    await operateProfileRequest(serverCn, cn, "approve");
}

async function rejectProfileRequest(serverCn, cn) {
    await operateProfileRequest(serverCn, cn, "reject");
}

async function generateInvitationCode(username) {
    try {
        let res = await fetch('/api/invite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username })
        });
        let data = await res.json();
        if (data.success) {
            alert('邀请码: ' + data.code);
        }
        else {
            alert('生成失败: ' + data.msg);
        }
    } catch (err) {
        alert('请求失败：' + err.message);
    }
}

async function refreshInvitationCodesTable(tbody) {
    try {
        let res = await fetch('/api/list/invites', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        let data = await res.json();
        if (data.success) {
            tbody.innerHTML = '';
            data.codes.forEach(code => {
                const row = document.createElement('tr');

                const idCell = document.createElement('td');
                idCell.textContent = code.id;
                const usernameCell = document.createElement('td');
                usernameCell.textContent = code.username;
                const invitationCodeCell = document.createElement('td');
                invitationCodeCell.textContent = code.invitation_code;
                const createTimeCell = document.createElement('td');
                createTimeCell.textContent = convertTimestampToString(code.create_time_ts, true);
                const expireTimeCell = document.createElement('td');
                expireTimeCell.textContent = convertTimestampToString(code.expire_time_ts, true);

                row.appendChild(idCell);
                row.appendChild(usernameCell);
                row.appendChild(invitationCodeCell);
                row.appendChild(createTimeCell);
                row.appendChild(expireTimeCell);

                tbody.appendChild(row);
            });
        }
        else {
            alert('刷新邀请码失败：' + data.msg);
        }
    } catch (err) {
        alert('请求失败：' + err.message);
    }
}

async function refreshProfileRequestsComfirmTable(tbody) {
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
                const operateCell = document.createElement('td');
                const approveLink = document.createElement('a');
                approveLink.href = '#';
                approveLink.textContent = '通过';
                approveLink.style.marginRight = '8px';
                approveLink.addEventListener('click', async (e) => {
                    e.preventDefault();
                    await approveProfileRequest(request.server_common_name, request.common_name);
                });
                const rejectLink = document.createElement('a');
                rejectLink.href = '#';
                rejectLink.textContent = '驳回';
                rejectLink.style.marginRight = '8px';
                rejectLink.addEventListener('click', async (e) => {
                    e.preventDefault();
                    await rejectProfileRequest(request.server_common_name, request.common_name);
                });
                operateCell.appendChild(approveLink);
                operateCell.appendChild(rejectLink);

                row.appendChild(idCell);
                row.appendChild(targetServerCell);
                row.appendChild(cnCell);
                row.appendChild(requestTimeCell);
                row.appendChild(operateCell);

                tbody.appendChild(row);
            });
        }
        else {
            alert('刷新 Profile 申请失败：' + data.msg);
        }
    } catch (err) {
        alert('请求失败：' + err.message);
    }
}

if (document.getElementById('adminContainer')) {

    const generateInvitationCodeInput = document.getElementById('generateInvitationCodeInput');
    const generateInvitationCodeButton = document.getElementById('generateInvitationCodeButton');
    const invitationCodesTable = document.getElementById('invitationCodesTable');
    const invitationCodesTableTbody = invitationCodesTable.getElementsByTagName('tbody')[0];
    const profileRequestsConfirmTable = document.getElementById('profileRequestsConfirmTable');
    const profileRequestsConfirmTableTbody = profileRequestsConfirmTable.getElementsByTagName('tbody')[0];

    refreshInvitationCodesTable(invitationCodesTableTbody);
    refreshProfileRequestsComfirmTable(profileRequestsConfirmTableTbody);

    generateInvitationCodeButton.addEventListener('click', async function () {
        let username = generateInvitationCodeInput.value;
        if (!validateUsername(username)) {
            alert('用户名不合法："' + username + '"');
            return;
        }

        await generateInvitationCode(username);
        await refreshInvitationCodesTable(invitationCodesTableTbody);
    });

}
