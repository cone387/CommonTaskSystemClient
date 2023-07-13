rm -rf ./dist/*

# Build the project
python setup.py sdist
twine upload dist/*


# build image

# docker build -t common-task-system-client .