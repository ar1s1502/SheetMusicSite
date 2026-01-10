

var checkout_banner = document.getElementById('checkout_banner');

checkout_banner.style.setProperty('display', 'block');
document.getElementById('closebtn').onclick = ()=> {
    window.location.href = contact_form_appurl;
}

if (document.getElementById('error_dict')) {
    checkout_banner.classList.add("alert-danger");
} else {
    checkout_banner.classList.add("alert-success");
}