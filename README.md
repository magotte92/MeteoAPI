# MeteoAPI

MeteoAPI is a weather scrapper from darksky.net .

## Installation

Requires Python 3.10 or newer. Verified on Python 3.12.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.txt.

```bash
pip install -r requirements.txt
```

`weather.py` still requests forecast pages from darksky.net. That host no longer returns the embedded forecast script this scraper reads, so `main.py` cannot print a live forecast until a replacement data source is added.

## Usage

```bash
python main.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)