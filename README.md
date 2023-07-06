# azlyrics-api

[![GitHub license](https://img.shields.io/github/license/Zedeldi/azlyrics-api?style=flat-square)](https://github.com/Zedeldi/azlyrics-api/blob/master/LICENSE) [![GitHub last commit](https://img.shields.io/github/last-commit/Zedeldi/azlyrics-api?style=flat-square)](https://github.com/Zedeldi/azlyrics-api/commits) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

Get song information from AZLyrics.

## Description

A Python API for AZLyrics, with a CLI front-end, supporting searching and getting lyrics.
The CLI allows search results to be selected interactively.

Songs can be exported to XML using `azlyrics_api.export`, which accepts a callable argument used for preprocessing.
[OpenSong's](http://www.opensong.org/) XML formatting is used by default.

## Usage

Install the package using `pip`:

`pip install .`

Get lyrics for a song:

`azlyrics-cli <title> <artist> [--xml export.xml]`

Search for a song and select interactively:

`azlyrics-cli <query> [--xml export.xml]`

## Libraries

- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - Web scraping
- [lxml](https://pypi.org/project/lxml/) - XML formatting
- [requests](https://pypi.org/project/requests/) - HTTP requests

## License

`azlyrics-api` is licensed under the [MIT Licence](https://mit-license.org/) for everyone to use, modify and share freely.

This program is distributed in the hope that it will be useful, but without any warranty.

## Donate

If you found this project useful, please consider donating. Any amount is greatly appreciated! Thank you :smiley:

[![PayPal](https://www.paypalobjects.com/webstatic/mktg/Logo/pp-logo-150px.png)](https://paypal.me/ZackDidcott)

My bitcoin address is: [bc1q5aygkqypxuw7cjg062tnh56sd0mxt0zd5md536](bitcoin://bc1q5aygkqypxuw7cjg062tnh56sd0mxt0zd5md536)
