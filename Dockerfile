
# Code generator
# - Install inspired by https://github.com/jsontypedef/json-typedef-docker/blob/master/jtd-codegen/Dockerfile
# - Genreates code with https://github.com/jsontypedef/json-typedef-codegen

FROM kubeless/unzip:latest AS download

ADD "https://github.com/jsontypedef/json-typedef-codegen/releases/latest/download/x86_64-unknown-linux-musl.zip" "/x86_64-unknown-linux-musl.zip"
RUN unzip "x86_64-unknown-linux-musl.zip"

FROM scratch
COPY --from=download /jtd-codegen /jtd-codegen
# ENTRYPOINT ["/jtd-codegen"]
