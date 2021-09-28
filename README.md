
# Project installation

Open command prompt and input these commands:

    > cd folder/to/clone-into/
    > git clone https://github.com/olehratinskiy/ap_virtualenv_6_variant.git
    > pyenv install 3.7.0
    > cd ap_virtualenv_6_variant
    > pip install virtualenv (if you don't already have virtualenv installed)
    > virtualenv venv
    > .\venv\Scripts\activate
    > pip install -r requirements.txt
   Then open project ap_virtualenv_6_variant and run <span>app.py</span>.
   While running <span>app.py</span> input in command prompt:
   
    > curl -v -XGET http://localhost:5000/api/v1/hello-world-6
	  
Good luck!!!
