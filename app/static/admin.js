function generateInvitationCode() {
    const username = document.getElementById('invite-username').value;
    fetch('/api/invite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username })
    })
    .then(response => response.json())
    .then(data => {
        // 处理后端返回的数据
        alert('邀请码: ' + data.code);
    })
    .catch(error => {
        alert('生成失败: ' + error);
    });
}