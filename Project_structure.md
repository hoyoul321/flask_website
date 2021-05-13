## Project structure

The project is coded using blueprints, app factory pattern, dual configuration profile (development and production) and an intuitive structure presented bellow:

> Simplified version

```bash
< PROJECT ROOT >
   |-- config/
   |    |-- config.yaml          # Configuration file (MUST be present)
   |    |-- config.yaml.example  # Sample configuration file
   |-- website/             # Implements app logic
   |    |-- blueprints/          # Flask Blueprints
   |    |    |-- admin/               # Contains the website administrator's interface - Roles, permissions, etc.
   |    |    |-- api/                 # API Blueprint - handles API requests (no UI)
   |    |    |-- auth/                # Authorization Blueprint - Login, Logout, etc.
   |    |    |-- company/             # Company Blueprint - handles company related features (e.g. dashboards)
   |    |    |-- funds/               # Funds Blueprint - handles funds related features (e.g. query for portfolio)
   |    |    |-- home/                # Home Blueprint - serve index (MAYBE: remove?)
   |    |    |-- ipo/                 # IPO Blueprint - handles IPO related input/output
   |    |    |-- kfs/                 # Handles data from KoreaFundService (accounting firm for the funds)
   |    |    |-- monitoring/          # Monitoring Blueprint - handles system monitoring related features
   |    |
   |   __init__.py               # Entry point for the module, contains the create_app factory method 
   |
   |-- app.py                    # Entry point for the whole app, calls create_app()
   |
   |-- Pipfile                   # Module requirements
   |-- Pipfile.lock              # Version locked module list
   |   |
   |-- ************************************************************************
```

<br />

> The bootstrap flow

- `app.py` executes the factory method `oam_intranet.create_app`
- Initialize the app using the specified in the .env file: *Debug* or *Production*
  - Currently there are defaults for some values even in Production, *MUST* change
- Call the app factory method `create_app` defined in oam_intranet/__init__.py
- `app.py` starts the Flask application in debug mode (`app.run()`) or Waitress (`waitress.serve(app)`)
- Redirect the guest users to Login page
- Unlock the pages served by *home* blueprint for authenticated users

<br />

> App / Base Blueprint

The *Base* blueprint handles the authentication (routes and forms) and assets management. The structure is presented below:

```bash
< PROJECT ROOT >
   |
   |-- app/
   |    |-- home/                                # Home Blueprint - serve app pages (private area)
   |    |-- base/                                # Base Blueprint - handles the authentication
   |         |-- static/
   |         |    |-- <css, JS, images>          # CSS files, Javascripts files
   |-- templates/                                # Base templates from AdminLE
   |         |-- includes/                       #
   |         |    |-- navigation.j2              # Top menu component
   |         |    |-- sidebar.j2                 # Sidebar component
   |         |    |-- footer.j2                  # App Footer
   |         |    |-- scripts.j2                 # Scripts common to all pages
   |         |-- layouts/                        # Master pages
   |         |    |-- base-fullscreen.j2         # Used by Authentication pages
   |         |    |-- base.html                  # Used by common pages
   |         |-- security/                       # Authentication pages
   |         |    |-- login.html                 # Login page
   |         |    |-- register.html              # Registration page         
   |         |-- unauthorized.html               # Unauthorized page template
   |-- ************************************************************************
```

<br />

## Deployment

The app is provided with a basic configuration to be executed in [Docker](https://www.docker.com/), and [Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/).

<br />

### [Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/)

Waitress is meant to be a production-quality pure-Python WSGI server with very acceptable performance. It has no dependencies except ones that live in the Python standard library.

> Waitress is already in Pipfile <br/>
> - Set `DEBUG` (defaults to False), `BIND_HOST` (0.0.0.0 by default), and `BIND_PORT` (80 by default) as appropriate in config.yaml
> - Start the app:
>     - `pipenv run python app.py` or
>     - `pipenv shell` followed by `python app.py`
> - Visit `http://BIND_HOST:BIND_PORT` in your browser. The app should be up & running.

<br />

### Docker

Docker is a solution for running containers ("lightweight VMs") on Linux, MacOS and Windows.

- [Install Docker](https://docs.docker.com/get-docker/)
- Build the image. E.g. build and assign tag "oam_intranet:v1.2.3":<br/>
   `docker build -t website:v1.2.3 /path/to/flask_website`
- Instantiate the image. E.g: <br/>
   `docker run --name intranet -p 0.0.0.0:8080:80 -v /opt/flask_app/config:/path/to/config website:v1.2.3`

In order to push an image to the internal registry, do the following:

- `docker tag website:v1.2.3 registry.one-asset.co.kr:5000/oam_intranet:v1.2.3`
- `docker login registry.website.co.kr:5000`      
  followed by username and password if needed
- `docker push registry.website.co.kr:5000/website:v1.2.3`

