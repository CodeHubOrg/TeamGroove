FROM ubuntu
EXPOSE 8000/tcp

# Fetch basic tools
RUN apt update && apt upgrade -y
# We need python3 to run Django
RUN apt install python3 -y
# We need curl to fetch poetry and distutils to run it
RUN apt install curl -y
RUN apt install python3-distutils -y
# And we need git to fetch the teamgroove source
RUN apt install git -y

# Fetch poetry and modify the $PATH (Poetry install cannot do this for Docker)
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
ENV PATH="/root/.poetry/bin:${PATH}"

# As this is a demo, we do everything as the root user.
WORKDIR /root
RUN git clone https://github.com/CodeHubOrg/TeamGroove.git
WORKDIR /root/TeamGroove

# Teamgroove needs a secret key and Django needs some parameters for the 
# createsuperuser command.
ENV SECRET_KEY=123456
ENV DJANGO_SUPERUSER_USERNAME=tgadmin
ENV DJANGO_SUPERUSER_PASSWORD=123456
ENV DJANGO_SUPERUSER_EMAIL=tgadmin@mailinator.com

# Now we are inside the fetch Teamgroove sources, set up poetry and Django.
RUN poetry install
RUN poetry run python3 manage.py migrate
RUN poetry run python3 manage.py createsuperuser --noinput

# HACK: workaround the issue of Django not serving non-local requests.
# Add nginx as a reverse proxy, forwarding 8080 to 8081.
RUN DEBIAN_FRONTEND=noninteractive apt install nginx -y
RUN printf 'server {\nlisten 8080;\nlocation / {\nproxy_pass http://localhost:8081;\n}\n}\n' > /etc/nginx/sites-enabled/default
RUN echo "service nginx start && poetry run python3 manage.py runserver 8081" > RUN

# On launch we use the manage.py script to invoke runserver on port 8000. We
# need to run inside a poetry shell. 
# Commented out: this is the command we would like to use.
#ENTRYPOINT ["/root/.poetry/bin/poetry", "run", "python3", "manage.py", "runserver", "8081"]
# However we need to launch nginx too, so this is the workaround script.
ENTRYPOINT ["/bin/dash", "RUN"]
