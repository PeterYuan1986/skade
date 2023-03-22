import stripe
STRIPE_PUBLIC_KEY = 'pk_test_51MjNu7ApoV55x5o7WyiWhNYJmEEe3DMGwhSSw4fdMNwFaB0yxVVvVlSYuqupWa5fU72jmQ9bDW9vqbkUqsV7Z5p000tGuHx0cn'
STRIPE_SECRET_KEY = 'sk_test_51MjNu7ApoV55x5o7EpY6TsPj82xk842nIEIQrQTktqxwUPBjdDQ0A30cRGJhsoAgIhE5T5QRvLGEQ6rKqB8vTlnO00IZcVruAy'
stripe.api_key = STRIPE_SECRET_KEY
checkout_session = stripe.checkout.Session.create(
            success_url='http://www.skade.us/success.html?session_id={CHECKOUT_SESSION_ID}',
            cancel_url= 'http://www.skade.us/canceled.html',
            mode='payment',
            # automatic_tax={'enabled': True},
            line_items=[{
                'price': 'price_1MnuTdApoV55x5o7AkA4WSCT',
                'quantity': 1,
            }]
        )
a=stripe.checkout.Session.expire(checkout_session['id'])
print(a['id'])