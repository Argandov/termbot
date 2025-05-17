#!/usr/bin/env bash
set -euo pipefail

# Common ldflags
LDFLAGS="-s -w -buildid="

# Where to put your binaries
OUTDIR=dist
mkdir -p "$OUTDIR"

# List of GOOS/GOARCH pairs
TARGETS=(
  "linux/amd64"
  "linux/arm64"
  "darwin/arm64"
)

for targ in "${TARGETS[@]}"; do
  # Split into GOOS and GOARCH
  IFS="/" read -r GOOS GOARCH <<<"$targ"
  BINNAME="termbot-${GOOS}-${GOARCH}"

  echo "Building $BINNAME …"

  CGO_ENABLED=0 \
  GOOS=$GOOS GOARCH=$GOARCH \
    go build \
      -trimpath \
      -ldflags "$LDFLAGS" \
      -o "$OUTDIR/$BINNAME" \
      .

  echo " → $OUTDIR/$BINNAME"
done

echo "All builds complete. Binaries in $OUTDIR/"
