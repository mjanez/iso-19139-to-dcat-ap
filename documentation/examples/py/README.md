## Running iso-19139-to-dcat-ap.py

## Prerequisites

Make sure you have Python 3.6 or higher installed on your system.

## Creating a virtual environment

To create a virtual environment, follow these steps:

1. Open a terminal and navigate to the directory containing the `iso-19139-to-dcat-ap.py` script.

2. Create a virtual environment by issuing the following command:

    - On Windows:

        ```sh
        python -m venv env
        ```

    - On MacOS and Linux:

        ```sh
        python3 -m venv env
        ```

3. Enable the virtual environment:

    - On Windows:

        ```sh
        .\env\Scripts\activate
        ```

    - On MacOS and Linux:

        ```sh
        source env/bin/activate
        ```

## Installing the prerequisites

With the virtual environment activated, install the necessary prerequisites by running the following command:

```sh
pip install -r documentation/examples/py/requirements.txt