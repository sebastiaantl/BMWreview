# Technical Design


# Routes
- Homepage
- Search Results page
- Profile page
- Car page
- Favorites page
- Register page


**Homepage**
<br>
Users have to be able to search for cars, no matter if they are logged in or not. When doing so, they will be redirected to the Search Result Page, where results will be shown for the search query. Now they can filter the results by filling in the filter parameters they would like to apply. Furthermore the homepage will display the highest rated cars by our members and it will suggest cars you may like and show recent reviews made by users.

**Search Results page**
<br>
After a search query has been submitted, the user will be redirected to this page. On this page users can apply filters to their search query. After the filters have been submitted, a filtered result will show up of the cars with the corresponding details. Everyone must be able to access this page, users are not required to be logged in. 

**Profile Page**
<br>
On the profile page users will see their own name, liked cars and reviews they have submitted. This page must be accessible to everyone, users are not required to be logged in to be able to see other people's profile.

**Car Page**
<br>
After you have filtered your search query on the Search Results page, users can click on cars they want to get more details about and will be redirected to a unique page per car. Every page will show one car, with it's specifications and the reviews of the car.

**Favorites Page**
<br>
On this page logged in users can see the cars they have added to their favorite car selection.

**Register page**
<br>
On this page users are able to create a new account. 

# Functions
- Search
- Login
- Register 
- Review
- Favorite

# Views


**Home view**<br><br><br>
<img src="https://github.com/sebastiaantl/UVA2019/blob/master/homepage.jpg" width="400"></img><br><br><br><br>

**Search Results view**<br><br><br>
<img src="https://github.com/sebastiaantl/UVA2019/blob/master/searchresults.jpg" width="400"></img><br><br><br><br>

**Car view**<br><br><br>
<img src="https://github.com/sebastiaantl/UVA2019/blob/master/car%20page.jpg" width="400"></img><br><br><br><br>

**Favorite view**<br><br><br>
<img src="https://github.com/sebastiaantl/UVA2019/blob/master/favourites%20page.jpg" width="400"></img><br><br><br><br>

**Profile view**<br><br><br>
<img src="https://github.com/sebastiaantl/UVA2019/blob/master/profile%20page.jpg" width="400"></img><br><br><br><br>

**Register view**<br><br><br>
<img src="https://github.com/sebastiaantl/UVA2019/blob/master/registration%20page.jpg" width="400"></img><br><br><br><br>

**Login view**<br><br><br>
<img src="https://github.com/sebastiaantl/UVA2019/blob/master/login.jpg" width="400"></img><br><br><br>


# Models/Helpers
- search()
- placereview()
- deletereview()
- favorite()
- unfavorite()
- calcmean()
- login()
- register()
- logout()

# Plugins/Framework
- Bootstrap: https://getbootstrap.com/
