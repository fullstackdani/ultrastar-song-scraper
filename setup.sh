echo "Installing python..."
apt install python3 python3-pip

echo ""
echo "Installing scrapper dependencies..."
pip3 install requests
pip3 install youtube-dl
pip3 install beautifulsoup4
pip3 install youtube-search-python
pip3 install unidecode