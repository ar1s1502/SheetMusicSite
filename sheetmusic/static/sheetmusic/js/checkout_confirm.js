
//skeleton code from https://docs.stripe.com/checkout/embedded/quickstart

var btn,
    checkout_banner = document.getElementById('checkout_banner'),
    banner_header = document.getElementById('banner_header'),
    banner_text = document.getElementById('banner_text');

async function validateCheckoutSession() {
    const response = await fetch(sessionview_appurl);
    const session = await response.json();
  
    if (session.status == 'open') {
        checkout_banner.classList.add("alert-danger");
        banner_header.textContent = "Please complete checkout first";
        return;
    } else if (session.status == 'complete') {
        // console.log(session)
        if (session.display_download) { //checkout success (paid + complete)
            // show btns
            document.getElementById('checkout_confirm_btns').style.setProperty('display', 'block');

            checkout_banner.classList.add("alert-success");
            banner_header.textContent = "Thank you for your purchase!";
            banner_text.textContent = `Please check your Downloads folder for 
                ${session.download_title}.${session.filetype}. A copy of the receipt will be sent to ${session.customer_email}.`;

            btn = document.getElementById('downloadbtn');
            btn.onclick = ()=> {
                link = document.createElement('a');
                link.href = `data:application/${session.filetype};base64,${session.download_content}`;
                link.download = session.download_title + "." + session.filetype;
                link.click();
            }
            btn.click()
        } else {
            checkout_banner.classList.add("alert-danger");
            banner_header.textContent = "Something went wrong";
            banner_text.textContent = 
            "Either this order has already been fulfilled (check your Downloads folder) or your payment didn't go through. If you have questions about your order, please fill out the Contact form"
        }

        btn = document.getElementById('closebtn');
        btn.onclick = ()=> {
            window.location.href = home_appurl;
        }
    }

    checkout_banner.style.setProperty('display', 'block');
  }

validateCheckoutSession();
