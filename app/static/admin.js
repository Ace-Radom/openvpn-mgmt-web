const REGEX_USERNAME = /^[A-Z][a-z]*$/;

function validateUsername(username) {
    return REGEX_USERNAME.test(username);
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
                operateCell.textContent = '通过 驳回';

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
