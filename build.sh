versions=( '3.8' '3.9' '3.10' '3.11' )
for version in "${versions[@]}";
do
    docker image build --build-arg PYTHON_VERSION=$version -t mpcurses:$version .
done