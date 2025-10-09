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
