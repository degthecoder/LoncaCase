# Lonca Case Study

This is a case study for Lonca firm. The python code and the example XML file is found in the repository. The study follows the guidelines outlined in the pdf. 

## Installation

### Prerequisites

Python 3.8 or later

pip 

MongoDB 

### Installation

Clone the repository:

```bash
git clone git@github.com:degthecoder/LoncaCase.git
cd LoncaCase
```

Create and activate a virtual environment (for mac):
```bash
python -m venv venv
source venv/bin/activate
```

Install the dependencies: The only external dependency used is `pymongo`.
``` bash
pip install -r requirements.txt
```


## Usage

### Before You Run

**Configuration:** Update the database name, collection name, and MongoDB URI inside the code if needed:

```python
if __name__ == "__main__":
    parser = ProductParser("lonca-sample.xml")
    products = parser.parse_products()

    db_conn = DatabaseConnection(db_name="lonca", collection_name="products")
    db_conn.create_entry(products)
```

The default MongoDB URI is configured for a localhost setup:

```python
def __init__(self, db_name, collection_name, mongo_uri="mongodb://localhost:27017/"):
```
**Prepare MongoDB:** Ensure your MongoDB server is running locally or remotely and is accessible via the provided URI.

### Running the program

You can run the program by executing the following command in the terminal:

```bash
python lonca_case.py
```

## Features

This project is designed to process product data from an XML file and store it in a MongoDB collection. Below are the key features implemented:

### XML Parsing 

Extracts products from a provided XML and sets the data according to the asked format. 

The ProductParser class takes a XML file path and parses the data it has, including data inside the description, and readies the product data for database entry.

### MongoDB Integration

Stores the data in a MongoDB collection, in the intended format. 

DatabaseConnection class takes in the db_name, collection name and the uri of MongoDB to insert the data. Periodic execution of the program does not create duplicate entries. 

### Some other key features

I tried to keep the data as consistent as possible.

The XML file path and MongoDB connection is easily configurable. 

I tried to create classes to keep an OOP based approach.

