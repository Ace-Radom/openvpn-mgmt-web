// .numberInput
// min, max should be set in html, step=1
document.querySelectorAll('.numberInput').forEach(container => {
    const input = container.querySelector('input[type="number"]');
    container.querySelector('.increment').addEventListener('click', () => {
        input.value = Math.min(Number(input.value) + 1, input.max ? Number(input.max) : 32767);
    });
    container.querySelector('.decrement').addEventListener('click', () => {
        input.value = Math.max(Number(input.value) - 1, input.min ? Number(input.min) : 0);
    });
    input.addEventListener('change', () => {
        let value = parseFloat(input.value);
        if (isNaN(value)) {
            input.value = input.min;
        }
        else if (value < input.min) {
            input.value = input.min;
        }
        else if (value > input.max) {
            input.value = input.max;
        }
        else {
            input.value = Math.floor(input.value);
        }
    });
    input.addEventListener('blur', () => {
        input.dispatchEvent(new Event('change'));
    });
});


// ts -> str convert
const DATE_FORMATTER = new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
});

function convertTimestampToString(ts, is_sec) {
    if (ts === -1) {
        return '2199/12/31 23:59:59';
    }

    if (is_sec) {
        ts *= 1000;
    }
    const date = new Date(ts);
    return DATE_FORMATTER.format(date);
}
