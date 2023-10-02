# Install Buf
Try installing buf using brew:
```shell
 brew install bufbuild/buf/buf
```

If this doesn't work, then try this:
```
BIN="/usr/local/bin" && \
VERSION="1.10.0" && \
  curl -sSL \
    "https://github.com/bufbuild/buf/releases/download/v${VERSION}/buf-$(uname -s)-$(uname -m)" \
    -o "${BIN}/buf" && \
  chmod +x "${BIN}/buf"
  ```

## Check Buf installation
```
buf --version
```

### Generate protobuf files
```
cd protos
buf generate
```