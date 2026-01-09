var feedback_btn = document.getElementById('feedback_btn'),
    request_btn = document.getElementById('request_btn'),
    f_div = document.getElementById('feedback_div'),
    r_div = document.getElementById('request_div'),
    f_form = document.getElementById('feedback_form'),
    r_form = document.getElementById('request_form');

feedback_btn.onclick = () => {
    f_div.style.setProperty('display', 'block');
    r_div.style.setProperty('display', 'none');

    f_form.style.setProperty('disabled', 'false');
    r_form.style.setProperty('disabled', 'true');

    feedback_btn.style.setProperty('opacity', '1.0');
    request_btn.style.setProperty('opacity', '0.65');
}

request_btn.onclick = () => {
    r_div.style.setProperty('display', 'block');
    f_div.style.setProperty('display', 'none');

    r_form.style.setProperty('disabled', 'false');
    f_form.style.setProperty('disabled', 'true');

    request_btn.style.setProperty('opacity', '1.0');
    feedback_btn.style.setProperty('opacity', '0.65');
}

//TODO: client-side form validation