async function loadSVG(url) {
    const res = await fetch(url);
    return await res.text();
}

let iconCheck = null;
let iconCross = null;
let iconLoaded = false;
Promise.all([
    loadSVG('/static/icons/check.svg').then(svg => iconCheck = svg),
    loadSVG('/static/icons/cross.svg').then(svg => iconCross = svg)
]).then(() => {
    iconLoaded = true;
});

function setIcon(element, valid) {
    if (!iconLoaded) {
        return;
    }

    if (valid === null) {
        element.innerHTML = '';
        element.className = 'input-icon';
        return;
    }
    element.innerHTML = valid ? iconCheck : iconCross;
    element.className = 'input-icon ' + (valid ? 'valid' : 'invalid');
    return;
}
