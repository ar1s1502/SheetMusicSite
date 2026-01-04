
//skeleton code from https://docs.stripe.com/checkout/embedded/quickstart

async function validateCheckoutSession() {
    const response = await fetch(sessionview_appurl);
    const session = await response.json();
  
    if (session.status == 'open') {
        return;
    } else if (session.status == 'complete') {
        document.getElementById('client_email').textContent = session.customer_email;
        document.getElementById('session_status').textContent = session.status;
        // document.getElementById('success').classList.remove('hidden');
        // document.getElementById('customer-email').textContent = session.customer_email
    }
  }

validateCheckoutSession();
