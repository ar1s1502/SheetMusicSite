
//skeleton code from https://docs.stripe.com/checkout/embedded/quickstart

async function validateCheckoutSession() {
    const response = await fetch(sessionview_appurl);
    const session = await response.json();
  
    if (session.status == 'open') {
        return;
    } else if (session.status == 'complete') {
        // console.log(session)
        document.getElementById('client_email').textContent = session.customer_email;
        document.getElementById('session_status').textContent = session.status;

        if (session.display_download) {
            // display btns
            document.getElementById('checkout_confirm_btns').style.setProperty('display', 'block')

            btn = document.getElementById('downloadbtn');
            btn.onclick = ()=> {
                link = document.createElement('a');
                link.href = `data:application/${session.filetype};base64,${session.download_content}`;
                link.download = session.download_title + "." + session.filetype;
                link.click();
            }
            btn.click()
        }
    }
    // window.location.href = home_appurl
  }

validateCheckoutSession();
