const REGEX_PSWD = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^\s]{6,}$/;

function validatePswd(pswd) {
    return REGEX_PSWD.test(pswd);
}

function validatePswdConfirm(pswd, pswd2) {
    return pswd === pswd2 && REGEX_PSWD.test(pswd);
}

if (document.getElementById('newpswd-form')) {

    const oldPswdInput = document.getElementById('old_pswd');
    const oldPswdIcon = document.getElementById('old_pswd_icon');
    const newPswdInput = document.getElementById('new_pswd');
    const newPswdIcon = document.getElementById('new_pswd_icon');
    const newPswd2Input = document.getElementById('new_pswd_confirm');
    const newPswd2Icon = document.getElementById('new_pswd_confirm_icon');

    newPswdInput.addEventListener('input', function () {
        if (!newPswdInput.value) {
            setIcon(newPswdIcon, null);
        }
        else {
            setIcon(newPswdIcon, validatePswd(newPswdInput.value));
        }
    });

    newPswd2Input.addEventListener('input', function () {
        if (!newPswd2Input.value) {
            setIcon(newPswd2Icon, null);
        }
        else {
            setIcon(newPswd2Icon, validatePswdConfirm(newPswdInput.value, newPswd2Input.value));
        }
    });

    document.getElementById('newpswd-form').onsubmit = async function (e) {
        e.preventDefault();
        let msg = document.getElementById('msg');

        let oldPswd = oldPswdInput.value;
        let newPswd = newPswdInput.value;
        let newPswd2 = newPswd2Input.value;

        if (!validatePswd(newPswd)) {
            msg.style.color = 'red';
            msg.innerHTML = '无效新密码。';
        } else if (!validatePswdConfirm(newPswd, newPswd2)) {
            msg.style.color = 'red';
            msg.innerHTML = '两次输入的新密码不一致。';
        } else {
            msg.style.color = 'green';
            msg.innerHTML = '';
        }

        if (msg.innerHTML) {
            return;
        }

        try {
            let res = await fetch('/api/newpswd', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ old_password: oldPswd, new_password: newPswd })
            });
            let data = await res.json();
            msg.innerText = data.msg;
            msg.style.color = data.success ? 'green' : 'red';
            if (data.success) {
                window.location.href = `/success?msg=更改成功！&next=/user`;
            }
        } catch (err) {
            alert('请求失败：' + err.message);
        }
    }
}
