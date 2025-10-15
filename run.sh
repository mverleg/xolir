#!/usr/bin/env -S bash -eEu -o pipefail

base="$(dirname "$(basename "$0")")"
if [ "$(pwd)" == "$base" ]; then
  cd "$base"
  pwd
fi

function cli() {
    all_cmds='build, quickcheck, test, clean, bump, upload or help'
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
        venv
        build
        exit 0
        ;;
      ""|test)
        check
        venv
        build
        run_tests
        exit 0
        ;;
      clean)
        clean
        exit 0
        ;;
      bump)
        bump
        venv
        exit 0
        ;;
      upload)
        echo "Subcommand '$cmd' recognized, only partially implemented!" 1>&2
        check
        venv
        build
        # run_tests
        #TODO @mark: ^
        upload
        exit 0
        ;;
      -h|--help|help)
        usage
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

function venv() {
    echo 'activating virtual env'
    python3 -m venv env
    source env/bin/activate
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
    (
      echo "cleaning venv"
      rm -rf venv
      echo "cleaning venv done"
    )

    (
      echo "cleaning java"
      cd java
      mvn clean -q -T1C
      rm -f 'dependency-reduced-pom.xml'
      echo "cleaning java done"
    )

    (
      echo "cleaning rust"
      cd rust
      ./cargo-proto clean -q
      echo "cleaning rust done"
    )

    (
      echo "cleaning python"
      cd python
      rm -rf 'dist/' *'.egg-info' 'xolir/' 'README.md'
      echo "cleaning python done"
    )

    (
      echo "cleaning typescript"
      cd typescript
      npm run clean --silent 2>/dev/null || rm -rf dist/ generated/ node_modules/
      rm -rf node_modules/
      echo "cleaning typescript done"
    )

    (
      echo "cleaning tests"
      rm -rf tests/generated/
      echo "cleaning tests done"
    )

    echo 'cleaning done'
}

function build() {
    cp 'README.md' 'python/README.md'
    {
      echo "generating java"
      cd java
      mvn install -q -T1C -Drevision=local-SNAPSHOT
      echo "generating java done"
    } &
    pid_java=$!

    {
      echo "generating rust"
      cd rust
      ./cargo-proto build -q
      echo "generating rust done"
    } &
    pid_rust=$!

    {
      echo "generating python"
      cd python
      python -m pip install -q pip build grpcio-tools pytest
      bash generate.sh
      pytest -q
      python -m build 1>/dev/null
      echo "generating python done"
    } &
    pid_python=$!

    {
      echo "generating typescript"
      cd typescript
      npm install --silent
      npm run build --silent
      echo "generating typescript done"
    } &
    pid_typescript=$!

    wait $pid_java || { echo "JAVA FAILED"; exit 1; }
    wait $pid_rust || { echo "RUST FAILED"; exit 1; }
    wait $pid_python || { echo "PYTHON FAILED"; exit 1; }
    wait $pid_typescript || { echo "TYPESCRIPT FAILED"; exit 1; }
    echo 'building done'
}

function run_tests() {
    echo 'running tests'
    test_base="$(realpath tests)"
    xolir_pth="$test_base/euler2.xolir"
    pb_bin_pth="$(mktemp)"

    (
      echo 'generating sample xolir'
      pip install protobuf
      pip install --force-reinstall "python/dist/xolir-$(cat VERSION)-py3-none-any.whl"
      python3 "$test_base/create_euler2_xolir.py" "$pb_bin_pth"
      echo "generated xolir bytes in $pb_bin_pth"
    )

    (
      echo 'compiling sample xolir to java'
      cd "$test_base/generate_java"
      # "$pb_bin_pth"
      MAVEN_OPTS="-ea" mvn compile exec:java -q -Dexec.args="$xolir_pth"
    )

    echo 'test done'
}

function bump() {
    if [ ! -f "VERSION" ]; then
        echo 'no VERSION file?' 1>&2
        exit 1
    fi
    
    current_version=$(cat VERSION | tr -d '\n\r')
    if [[ ! "$current_version" =~ ^0\.([0-9]+)\.0$ ]]; then
        echo "Error: VERSION file must contain version in format 0.x.0, found: $current_version" 1>&2
        exit 1
    fi
    new_minor=$(("${BASH_REMATCH[1]}" + 1))
    new_version="0.$new_minor.0"
    
    echo "Bumping version from $current_version to $new_version"
    
    echo "$new_version" > VERSION
    
    echo "Updating Java version..."
    sed -i "s|<revision>$current_version</revision>|<revision>$new_version</revision>|" java/pom.xml
    
    echo "Updating TypeScript version..."
    sed -i "s|\"version\": \"[^\"]*\"|\"version\": \"$new_version\"|" typescript/package.json
    
    echo "Updating Python version..."
    sed -i "s|version = \"[^\"]*\"|version = \"$new_version\"|" python/pyproject.toml
    
    echo "Updating Rust version..."
    sed -i "s|version = \"[^\"]*\"|version = \"$new_version\"|" rust/Cargo.toml
    
    echo "Version bump completed: $current_version -> $new_version"
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

    (
      echo "uploading java"
      cd java
      mvn package deploy -q -T1C
      echo "java upload done"
    ) || printf "\033[0;31mJAVA UPLOAD FAILED!!\033[0m\n" 1>&2

    echo 'upload done'
}

cli "$@"
echo "should not reach this, cli should exit" 1>&2
exit 1
