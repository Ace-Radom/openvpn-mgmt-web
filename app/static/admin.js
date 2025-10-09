const REGEX_USERNAME = /^[A-Z][a-z]*$/;

function validateUsername(username) {
    return REGEX_USERNAME.test(username);
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

if (document.getElementById('adminContainer')) {

    const generateInvitationCodeInput = document.getElementById('generateInvitationCodeInput');
    const generateInvitationCodeButton = document.getElementById('generateInvitationCodeButton');

    generateInvitationCodeButton.addEventListener('click', function () {
        let username = generateInvitationCodeInput.value;
        if (!validateUsername(username)) {
            alert('用户名不合法："' + username +'"');
            return;
        }

        generateInvitationCode(username);
    });

}
