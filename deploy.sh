rm -rf ./dist/*

# Build the project
python setup.py sdist
twine upload dist/*