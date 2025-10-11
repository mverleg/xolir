#!/usr/bin/env -S bash -eEu -o pipefail

function cli() {
    all_cmds='build, quickcheck, test, clean, upload or help'
    cmd="${1:-}"
    if [ $# -gt 1 ]; then
        echo "Error: Too many arguments provided. Expected at most one argument: $all_cmds." 1>&2
        usage 1>&2
        exit 1
    fi
    case "$cmd" in
      quickcheck)
        check
        exit 0
        ;;
      build)
        check
        build
        exit 0
        ;;
      ""|test)
        check
        build
        run_tests
        exit 0
        ;;
      clean)
        clean
        exit 0
        ;;
      -h|--help|help)
        usage
        exit 0
        ;;
      upload)
        echo "Subcommand '$cmd' recognized, only partially implemented!" 1>&2
        check
        build
        #run_tests
        #TODO @mark: ^
        upload
        exit 0
        ;;
      *)
        echo "Unknown subcommand: '$cmd'; expected one of $all_cmds" 1>&2
        usage 1>&2
        exit 1
        ;;
    esac
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [subcommand]

Subcommands:
  quickcheck Valiate the proto files
  build    Build/generate artifacts (not implemented yet)
  test     Run tests after building artifacts
  clean    Clean generated/build artifacts (not implemented yet)
  bump     Bump the version of dependencies
  upload   Upload/publish artifacts (not implemented yet)

If no subcommand is provided, the default build is executed.
EOF
}

function check() {
    bad_files=$(grep -EL '^syntax = "proto3";' proto/xolir/*.proto)
    if [ -n "$bad_files" ]; then
        printf "files without syntax 3:\n%s\n" "$bad_files" 1>&2
        exit 1
    fi

    bad_files=$(grep -EL '^package ' proto/xolir/*.proto)
    if [ -n "$bad_files" ]; then
        printf "files without package:\n%s\n" "$bad_files" 1>&2
        exit 1
    fi

    # Use protoc for comprehensive proto validation without generating code
    # Create temporary directory for output and clean up immediately
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf '$TEMP_DIR'" EXIT
    
    if ! protoc --proto_path=proto --cpp_out="$TEMP_DIR" proto/xolir/*.proto 2>&1; then
        echo "proto validation failed - protoc reported errors above" >&2
        exit 1
    fi
    
    echo "proto validation passed!"
}

function clean() {
    {
      echo "cleaning java"
      cd java
      mvn clean -q -T1C
      echo "cleaning java done"
    } &

    {
      echo "cleaning rust"
      cd rust
      ./cargo-proto clean -q
      echo "cleaning rust done"
    } &

    {
      echo "cleaning python"
      cd python
      rm -rf dist/ *.egg-info
      echo "cleaning python done"
    } &

    {
      echo "cleaning typescript"
      cd typescript
      npm run clean --silent 2>/dev/null || rm -rf dist/ generated/ node_modules/
      echo "cleaning typescript done"
    } &

    wait
    echo 'cleaning done'
}

function build() {
    cp 'README.md' 'python/README.md'
    {
      echo "generating java"
      cd java
      mvn package -q -T1C -Pfat-jar
      echo "java done"
    } &

    {
      echo "generating rust"
      cd rust
      ./cargo-proto build -q
      echo "rust done"
    } &

    {
      echo "generating python"
      cd python
      python -m pip install -q pip build
      python -m build 1>/dev/null
      pytest -q
      # twine upload
      echo "python done"
    } &

    {
      echo "generating typescript"
      cd typescript
      npm install --silent
      npm run build --silent
      echo "typescript done"
    } &

    wait
    rm 'python/README.md'
    echo 'building done'
}

function run_tests() {
    base="$(realpath tests)"
    xolir_pth="$base/euler2.xolir"

    # Must have:
    # pip install protobuf
    # pip install -e "$(git rev-parse --show-toplevel)/target/python"
    echo 'generating sample xolir'
    python3 "$base/create_euler2_xolir.py"

    (
      echo 'compiling sample xolir to java'
      cd "$base/generate_java"
      MAVEN_OPTS="-ea" mvn compile exec:java -e -q -Dexec.args="$xolir_pth"
    )

    echo 'test done'
}

function upload() {

    if [ ! -f "VERSION" ]; then
        echo 'no VERSION file?' 1>&2
        exit 1
    fi
    version=$(cat VERSION | tr -d '\n\r')

    if git rev-parse "v$version" >/dev/null 2>&1; then
        printf "\033[0;35mwarning: tag v%s already exists!\033[0m\nyou can create a new version by calling '$0 bump'\ndo you want to upload this version? (y/N): " "$version" 1>&2
        read -r response
        if ! [[ "$response" =~ ^[yY]([eE][sS])?$ ]]; then
            echo "aborting upload." >&2; exit 1
        fi
    else
        # Create new tag
        echo "creating tag v$version"
        git tag -am "v$version" "v$version"
    fi

    (
      echo "uploading python"
      cd python
      python -m twine upload dist/*
      echo "python upload done"
    ) || printf "\033[0;31mPYTHON UPLOAD FAILED!!\033[0m\n" 1>&2

    (
      echo "uploading rust"
      cd rust
      ./cargo-proto publish -q
      echo "rust upload done"
    ) || printf "\033[0;31mRUST UPLOAD FAILED!!\033[0m\n" 1>&2

    (
      echo "uploading typescript"
      cd typescript
      npm publish
      echo "typescript upload done"
    ) || printf "\033[0;31mTYPESCRIPT UPLOAD FAILED!!\033[0m\n" 1>&2

    echo 'upload done'
}

cli "$@"
echo "should not reach this, cli should exit" 1>&2
exit 1
