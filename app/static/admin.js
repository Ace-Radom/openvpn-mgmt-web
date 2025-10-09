const REGEX_USERNAME = /^[A-Z][a-z]*$/;

const DATE_FORMATTER = new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
});

function validateUsername(username) {
    return REGEX_USERNAME.test(username);
}

function convertTimestampToString(ts, is_sec) {
    if (ts === -1){
        return '2199/12/31 23:59:59';
    }

    if (is_sec) {
        ts *= 1000;
    }
    const date = new Date(ts);
    return DATE_FORMATTER.format(date);
}

function generateInvitationCode(username) {
    fetch('/api/invite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username })
    })
    .then(response => response.json())
    .then(data => {
        alert('邀请码: ' + data.code);
    })
    .catch(error => {
        alert('生成失败: ' + error);
    });
}

function refreshInvitationCodesTable(tbody) {
    fetch('/api/list/invites', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
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
    })
    .catch(error => {
        alert('刷新邀请码表失败：' + error);
    })
}

if (document.getElementById('adminContainer')) {

    const generateInvitationCodeInput = document.getElementById('generateInvitationCodeInput');
    const generateInvitationCodeButton = document.getElementById('generateInvitationCodeButton');
    const invitationCodesTable = document.getElementById('invitationCodesTable');
    const invitationCodesTableTbody = invitationCodesTable.getElementsByTagName('tbody')[0];

    refreshInvitationCodesTable(invitationCodesTableTbody)

    generateInvitationCodeButton.addEventListener('click', function () {
        let username = generateInvitationCodeInput.value;
        if (!validateUsername(username)) {
            alert('用户名不合法："' + username +'"');
            return;
        }

        generateInvitationCode(username);
        refreshInvitationCodesTable(invitationCodesTableTbody);
    });

}
