# fixmydjango-lib [![Travis CI](https://travis-ci.org/vintasoftware/fixmydjango-lib.svg?branch=master)](https://travis-ci.org/vintasoftware/fixmydjango-lib.svg?branch=master) [![Coverage Status](https://coveralls.io/repos/vintasoftware/fixmydjango-lib/badge.svg?branch=master&service=github)](https://coveralls.io/github/vintasoftware/fixmydjango-lib?branch=master)
Fix My Django is a library for helping Django developers to find solutions for common Django exceptions. While developing a Django project, if you get any exception in development server and [fixmydjango.com](http://www.fixmydjango.com) has a solution for it, this library will display a link to the solution in the error 500 debug template. Don't waste your time searching for exceptions on Google or Stack Overflow, just install this lib and be happy!

## How to use
1. Install

    ```
    pip install fixmydjango
    ```

2. Configure `settings.py` of your project by adding `'fixmydjango'` app
    
    ```
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',

        'yourapp',
        'fixmydjango',  # <-- add me!
    )
    ```

3. Profit! If any known Django exception bite you, something like this will appear:
    
    ![Fix My Django example](https://s3.amazonaws.com/fixmydjango/screenshots/Screen+Shot+2015-07-25+at+19.36.50.png)


## Privacy
We only look for solutions to exceptions thown from inside Django source-code and we don't use exception message to search for similar ones. Take a look at [`client.py`](https://github.com/vintasoftware/fixmydjango-lib/blob/master/fixmydjango/client.py) to see how it's implemented. The API code is open-sourced at [https://github.com/vintasoftware/fixmydjango](https://github.com/vintasoftware/fixmydjango).

## Contribute
Feel free to fork this project and contribute with it!

## Authors
Made by pythonistas at [Vinta Software Studio: vinta.com.br](http://www.vinta.com.br/?fixmydjango).
