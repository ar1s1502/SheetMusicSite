### Tech stack: 
- Frontend: HTML/Bootstrap/JS
- Backend: Python (Django)
- DB: PostgreSQL
- deployment: Nginx -> Gunicorn/Django, hosted on an Ubuntu AMI in an AWS EC2 t4g.small instance. 

### Cool features:
- Stripe handles the payments securely through SSL, and I embedded their checkout form in my website (as opposed to routing to a new tab). I also set up a webhook to listen for Stripe payment events to fulfill orders.
- When an order is fulfilled, the client will get a .zip file of the product downloaded through their browser.
- The django backend authenticates to a SMTP (simple mail transfer protocol) gmail server, and sends an email to the client with the musescore project (.mscz) file. Because I don't require a login
and there's no way to store state (eg. if a customer has previously purchased the sheet), I send an email as confirmation of purchase, as well as linking the .mscz file which allows them to re-export
the pdf and mp3's, or even to modify the score if they wish.
- Customers can submit a questions/feedback form and an arrangement request form. Django has a built-in form object which makes generating HTML forms very handy. It allows you to specify default values, initial values, placeholder text, 
and even CSS styling in Django. Form submissions are validated in the backend; and invalid inputs (eg. wrong email format) will trigger a warning banner to display with the error message, which Django automatically generates
while form validating as well.
- I used porkbun to purchase a domain name, and every purchase also comes with free SSL certification. I've also routed all http requests to the app to https in the nginx/default.conf, so that all Stripe payments are secure.


### Stuff I learned 
- Stripe payment webhook must be csrf exempt, both in dev and in prod. This is because it originates from Stripe servers, and it doesn't know the csrf cookie in the user's browser. Meanwhile, the post request to generate a CheckoutSession object
in the Django backend can and should include the crsf token, which you have to manually specify and include by iterating through the browser's cookie jar. This is because Django only automatically
includes the csrf cookie in post requests if it's a form submission, and the form has the template tag {% csrf_token %} inside.
- You can simulate the whole payment process, including successful and unsucessful transactions, for testing using the fake credit card numbers Stripe provides in their sandbox version of your account, and prompting your payment webhook through the Stripe CLI
- I chose to use this js library called PDF.js to handle displaying the sheet music. I wanted to only display 3 pages of the sheets that cost money, and I thought that using this library would enable me to
have more control over what I could display (as opposed to manually exporting the first 3 pages out of each pdf and using the browser's built-in pdf viewer), but ultimately I should have just used the built-in pdf viewer instead.
PDF.js draws the supplied PDF (in b64-encoded bytes) onto a specific canvas element on the html, and getting the drawn canvas to scale correctly and not be a pixelated mess in dynamically-resizable 
Bootstrap cards was an absolute pain. I ended up having to do some weird hack from Stack Overflow where you render the pdf on 2x scale (for better resolution), but later scale the actual rendered pdf
down to fit in the desired dimensions, hence the weird stuff with canvas.height/width (the actual internal buffer of the canvas that the pdf is drawn on) and canvas.style.height/width (actual displayed sizing).
- This and the Stripe integration meant a lot more time spent on javascript than I was hoping, but it did make me a lot more comfortable with working with javascript.
- SMTP gmail server only lets you authenticate if you use SSL connection
- How to use Docker compose. To be honest, I still don't feel very confident with Docker. There are 3 containers: nginx (the proxy server that also serves the static files), web (the Django app with Gunicorn WSGI), and 
db (The postgres db). I think it was worth the extra headache of learning Docker though, since after setting it up correctly I could start all these services and stop them with singular commands: ```sudo docker compose up --build``` and ```sudo docker compose down```,
as opposed to manually starting and stopping a postgres service, a gunicorn service, and an nginx service every time I had to update some code.
- Adding the ```-v``` flag to sudo docker compose down also deletes the volumes (persistent data storage) in Docker. Don't do this on the live server without a backup.sql, because the postgres db is a docker volume.
- Working with AWS EC2 instances. I have never deployed a website before, so learning how to set up an AWS instance was pretty interesting. I learned about the different kinds of compute available for rent. (I used t4g.small because it's free until 12/26,
but I'm probably going to switch to t4g.micro after that since I don't actually need 2GB of RAM, 1 is enough _I think_), and how to associate an Elastic IP with my instance so that rebooting the server doesn't change my website's IP address (this nomenclature is confusing
tbh, why is it called an _elastic_ IP if it doesn't change? Maybe because it can be reassociated with different instances? idk)
- Linux CLI tools: systemctl, apt, tmux
- Working with nginx. I initially started with Apache and mod_wsgi, since I don't expect my app to have much traffic, but apparently the more "modern" way to do things is with Nginx and Gunicorn WSGI. To be honest, I prefer Nginx
even if it's a little overkill; it's a lot easier to setup because you only have to work with one config file to set up your forwarding, your server IP / servername, SSL, etc., and the syntax is relatively intuitive.
I found the default given httpd (apache) server config given by homebrew to be very verbose and hard to navigate,
but to be fair, I'm not very familiar with Apache either.





