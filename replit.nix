
{ pkgs }: {
  deps = [
    pkgs.python310Full
    pkgs.python310Packages.pip
    pkgs.python310Packages.setuptools
    pkgs.python310Packages.wheel
    pkgs.python310Packages.fastapi
    pkgs.python310Packages.uvicorn
    pkgs.python310Packages.sqlalchemy
    pkgs.python310Packages.psycopg2
    pkgs.python310Packages.alembic
    pkgs.python310Packages.pydantic
    pkgs.python310Packages.python-multipart
    pkgs.python310Packages.requests
    pkgs.python310Packages.python-dotenv
    pkgs.python310Packages.passlib
    pkgs.python310Packages.python-jose
    pkgs.python310Packages.pandas
    pkgs.python310Packages.numpy
    pkgs.python310Packages.scikit-learn
    pkgs.postgresql
  ];
}
