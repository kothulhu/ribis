# README

ribis is a static site generator inspired by [werc](http://werc.cat-v.org). It has support for blogging. The website content is typed in markdown. 
<br>

## Requirements

- Python >= 3.6
- [cmark](https://github.com/commonmark/cmark)
- uWSGI
<br>

## Running

Download ribis to your desired location. Open `ribis/bin/ribis.py` and change the value of `rootdir` to the location of your ribis directory. For instance:

    rootdir = '/home/your_homedir/src/ribis' 
    

<br>

`ribis/bin/ribis.py` is the uWSGI program that you need to run. 


    $ uwsgi --plugin python -s 127.0.0.1:9999 --wsgi-file ~/src/ribis/bin/ribis.py

<br>

ribis requires your site's name to be the `HTTP_HOST` value sent to it, so it might be necessary to add a rule to your hosts file assigning localhost to your domain name like so:


    /etc/hosts
	-------------------------------------------

    127.0.0.1        ribis.loc        ribis.loc

<br>

You can run ribis under nginx:


    /etc/nginx/sites-enabled/ribis
	------------------------------------------------------------------------

    server {
    	listen 80 ;
    	listen [::]:80 ;
    
    	root /var/www/html;
    
    	index index.html index.htm index.nginx-debian.html;
    
    	server_name ribis.loc;
    
    	location / {
    
    		include /etc/nginx/uwsgi_params;
    		uwsgi_param Host $host;
    		uwsgi_param X-Real-IP $remote_addr;
    		uwsgi_param X-Forwarded-For $proxy_add_x_forwarded_for;
    		uwsgi_param X-Forwarded-Proto $http_x_forwarded_proto;
    
    		uwsgi_pass 127.0.0.1:9999;
    
    	}
    
    }

<br>

Now you can navigate to `http://ribis.loc` in your web browser and the ribis site should appear.

<br>

## Using

- Similar to werc, ribis presents the contents of the `index.md`, `_header.md` and `_footer.md` files in a directory. The lack of an `index.md` file will cause it to present a directory listing. 
- Some configuration is done through modifying the files present in the `_ribis` subdirectory. Go through the files in `sites/ribis.loc/_ribis` and `sites/ribis.loc/blag/_ribis`.

<br>

## Pictures

- [home page](pics/homepage.png "Home page")
- [blog page](pics/blogpage.png "Blog page")


