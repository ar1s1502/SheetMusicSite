// This is a public sample test API key.
// Don’t submit any personally identifiable information in requests made with this key.
const stripe = Stripe("pk_test_51SlWzmCxn1NVP4jx0w3tmJ7ax4cVcrkuLfr0WeDDpR3eclQc3fbgyRxRgP8rBMhHRrqW34mPFBfL4BWQWoC9bQ7q00iJiPGFF1");

var sheet_id = JSON.parse(document.getElementById('arr-id').textContent)
console.log("id of sheet: " + sheet_id)
const POSTdata = {
    'sheet_id': sheet_id
}


initialize();

//skeleton code from https://docs.stripe.com/checkout/embedded/quickstart
//Create a Checkout Session
async function initialize() {

  const fetchClientSecret = async () => {
    //query app server (views.checkout) to create Stripe payment sesh, then return the sesh secret
    const response = await fetch(checkoutview_appurl, {
      method: "POST",
      headers: { 
        'Content-Type': 'application/json',
        //must include csrftoken, else app server denies request with error 403
        //by default, django expects the csrf_header_name to be X_CSRFTOKEN (see https://docs.djangoproject.com/en/6.0/ref/settings/#std-setting-CSRF_HEADER_NAME)
        'X-CSRFTOKEN': csrftoken
      },
      mode: 'same-origin',
      body: JSON.stringify(POSTdata)
    });
    const {clientSecret} = await response.json();
    return clientSecret;
  };

  //after getting session key, pass to stripe so they can build their checkout form
  const checkout = await stripe.initEmbeddedCheckout({
    fetchClientSecret,
  });

  // Stripe builds an iframe with the form, and places it in <div id="checkout">
  checkout.mount('#checkout');
}

