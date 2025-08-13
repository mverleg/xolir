#!/usr/bin/env -S bash -eEu -o pipefail

function cli() {
    cmd="${1:-}"
    case "$cmd" in
      ""|build)
        check_proto
        build
        exit 0
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      clean|upload)
        echo "Subcommand '$cmd' recognized but not implemented yet." 1>&2
        exit 2
        ;;
      *)
        echo "Unknown subcommand: '$cmd'; expected one of build, clean, upload or help" 1>&2
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

function build() {
    (
      echo "generating java"
      cd java
      mvn package -q -T1C
      echo "java done"
    )

    (
      echo "generating rust"
      cd rust
      cargo build -q
      echo "rust done"
    )

    (
      echo "generating python"
      cd python
      python -m pip install -q pip build
      python -m build
      pytest -q
      # twine upload
      echo "python done"
    )

    echo "typescript not ready yet" 1>&2
    exit 1
}

cli "$@"
echo "should not reach this, cli should exit" 1>&2
exit 1
