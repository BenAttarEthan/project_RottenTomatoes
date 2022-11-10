# project_RottenTomatoes ITC DS OCT 2022

#Members
Ethan BEN ATTAR
Meïr AMAR

#Introduction
For this project, we decide to scrap all the movies avaible on streaming platforms rated on the website https://www.rottentomatoes.com/browse/movies_at_home/

#Milestone 1
We create a webscraper using the packages "REQUESTS", "BS4" and "SELENIUM".

"REQUESTS" was used to validate that the datas are avaible.
"BS4" was used to register the HTML datas and to find the informations needed.
"SELENIUM" was used to navigate into the main page.

For each movie, we exeplored the related link to take a maximum of informations (date, type, rate...)

The main challenge we faced is on the main page. Rotten Tomatoes provides a big amount of movies. That means a big amount of pages.
The pages are scrolled behind each others, and to open a new one, it needed to 'click' on a "LOAD MORE" button.
But at each update, the website authorized 5 pages. That means, we can't extract the list of the films on the other pages, even if we loaded it before.
To solve this challenge, we used "SELENIUM" and a nice team spirit to improve the code.
We first add lines to click on the button until the button deseappears.
The "REQUESTS" updates the page, so all the HTML code was lost. Then, we added lines to extract the HTML code before this update.