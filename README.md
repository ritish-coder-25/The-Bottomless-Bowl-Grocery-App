README FILE FOR APP-DEV-2-PROJECT – BOTTOMLESS BOWL GROCERY APP

The Bottomless Bowl is a web application to shop for various products under various household categories. It is a part of the Modern App Development 1 course project.

HOW TO RUN THE APP FROM CODE – 

1.	First create a virtual environment – 
 ![image](https://github.com/ritish-coder-25/The-Bottomless-Bowl-Grocery-App/assets/96167053/47234309-c220-4553-9db8-1138f573caf6)


2.	Activate the virtual environment – 
 ![image](https://github.com/ritish-coder-25/The-Bottomless-Bowl-Grocery-App/assets/96167053/cc63f8d1-e845-491d-abf4-d2ab09ac11b4)


3.	Install the packages from requirements.txt – 
 ![image](https://github.com/ritish-coder-25/The-Bottomless-Bowl-Grocery-App/assets/96167053/1bfb8f96-aac3-490e-b6dd-2bedb3b7bd72)


4.	Start the MailHog service to open the proxy server – 
 ![image](https://github.com/ritish-coder-25/The-Bottomless-Bowl-Grocery-App/assets/96167053/96cb21cb-421e-4575-a8b2-3f074ca50adb)
 ![image](https://github.com/ritish-coder-25/The-Bottomless-Bowl-Grocery-App/assets/96167053/031930b5-ed4d-4123-8943-36fe75fe5b27)

 
5.	On another tab, like the above steps, activate the virtual environment and then start the application (the application and the celery-redis scheduler starts together)– 
 ![image](https://github.com/ritish-coder-25/The-Bottomless-Bowl-Grocery-App/assets/96167053/a9a40c1e-e2bd-4835-8e1f-f2087422291b)


AUTHENTICATION [These are dummy values. Please refer the database to make sure data is available in database] – 
	
1.	For Admin [adjust your own admin] – 
a.	Email – dummy_email, Password – estahnl

2.	For Store Manager – 
a.	Email – dummy_email2 , Password – aeiub
b.	Email – dummy_email3, Password – aeiuhgoi

3.	For Users – 
a.	Email - dummy_email4, Password – ranjan@123
b.	Email – dummy_email5, Password – ritish@123
c.	Email – ecb21070@tezu.ac.in, Password – ecb70@123

DIRECTORY STRUCTURE – 

1.	Root Folder Name – Code:
a.	Folder Name – application
i.	api.py
ii.	cache.py
iii.	config.py
iv.	database.py
v.	models.py
vi.	role_required.py
vii.	utils.py
viii.	validation.py
b.	Folder Name - db_directory
i.	database.sqlite3
c.	Folder Name – templates
i.	admin_dashboard.html
ii.	admin_login.html
iii.	cart-list-template.html
iv.	index.html
v.	manage_categories.html
vi.	manager_dashboard.html
vii.	monthly_activity_report.html
viii.	product-manager-template.html
ix.	request_sender.html
x.	request_viewer.html
xi.	shopping-template.html
xii.	store_manager_login.html
xiii.	store_manager_register.html
xiv.	user_dashboard.html
xv.	user_login.html
xvi.	user_register.html
xvii.	user_login.html
xviii.	user_register.html

d.	celeryconfig.py
e.	main.js
f.	main.py
g.	requirements.txt
2.	Project Documentation.pdf 
