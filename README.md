# w4111-proj1

- Same requirements as given by professor plus
- pip install Flask-WTF 
-> this is for handling images will be added in part 4 

1. Same DB used as in part 2:
- rm3932 -h 34.28.53.86

2. URL of application for demo below:
- 

3. What we implented from our proposal from part 1 and what we did not
- We implemented the core aspects. We allowed implemnted functonality for each account type.
-> Admin can view orders, approve sellers, and approve seller requests.
-> consumer can shop, view their orders, and view products in general
-> seller can make sale requsts and can view their requests
- We did not implement the ability to display all the most popular products. 
-> Admin cannot view products/edit them atm 
-> We did not add pictures yet 
-> A consumer's balance is not being taken into account will be added as constraint for part 4
-> Can register new accounts, but need to update values in children table that were not added 
when like consumer.address vs consumer.balance vs seller.included_status will handle in part 4
4. The two most interesting pages and why we believe those to be so.
- admin/approve-sale-request
-> We believe this page was intersting because it impacts the ability of the seller.
This is because without the admin approving a sales-request it cannot become a product. It has the most relations interacting with one 
another, and we thought it was cool to see everything come together like such.
- consumer/shopping-cart
-> We thought this was an interesting as it is one of the most flexible pages on the application. 
A consumer is able to make many request/queries by adding and deleting from their shopping cart. It is the main page that does not get
redirected after completion of it's main task and can be toyed with to the user's content within the constraints of our project.