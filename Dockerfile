FROM python:3.11.8
COPY src/juq/__init__.py src/juq/__init__.py
COPY pyproject.toml ./
RUN pip install -e .[test]
COPY . .
ENTRYPOINT [ "pytest", "-vvv", "tests" ]
