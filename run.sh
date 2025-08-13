#!/usr/bin/env -S bash -eEu -o pipefail

function cli() {
    cmd="${1:-}"
    case "$cmd" in
      ""|build)
        check_proto
        build
        exit 0
        ;;
      test)
        check_proto
        build
        run_tests
        exit 0
        ;;
      clean)
        clean
        exit 0
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      upload)
        echo "Subcommand '$cmd' recognized but not implemented yet." 1>&2
        exit 2
        ;;
      *)
        echo "Unknown subcommand: '$cmd'; expected one of build, clean, upload, test or help" 1>&2
        usage 1>&2
        exit 1
        ;;
    esac
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [subcommand]

Subcommands:
  build    Build/generate artifacts (not implemented yet)
  test     Run tests after building artifacts
  clean    Clean generated/build artifacts (not implemented yet)
  upload   Upload/publish artifacts (not implemented yet)

If no subcommand is provided, the default build is executed.
EOF
}

function check_proto() {
    bad_files=$(grep -EL '^syntax = "proto3";' proto/xolir/*.proto)
    if [ -n "$bad_files" ]; then
        printf "Files without syntax 3:\n%s\n" "$bad_files" 1>&2
        exit 1
    fi

    bad_files=$(grep -EL '^package ' proto/xolir/*.proto)
    if [ -n "$bad_files" ]; then
        printf "Files without package:\n%s\n" "$bad_files" 1>&2
        exit 1
    fi
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
      cargo clean -q
      echo "cleaning rust done"
    } &

    {
      echo "cleaning python"
      cd python
      rm -rf dist/ *.egg-info
      echo "cleaning python done"
    } &

    wait

    echo "typescript not ready yet" 1>&2
    exit 1
}

function build() {
    {
      echo "generating java"
      cd java
      mvn package -q -T1C -Pfat-jar
      echo "java done"
    } &

    {
      echo "generating rust"
      cd rust
      cargo build -q
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

    wait

    echo "typescript not ready yet" 1>&2
    exit 1
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

    echo 'done'
}

cli "$@"
echo "should not reach this, cli should exit" 1>&2
exit 1
