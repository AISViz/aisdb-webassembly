SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
RSTSOURCEDIR="${SCRIPTPATH}/docs/source"
HTMLOUTPUTDIR="${SCRIPTPATH}/docs/html"
PKGDIR="${SCRIPTPATH}/aisdb"
ROOTDIR="${SCRIPTPATH}/"


rm -rf "$HTMLOUTPUTDIR"
mkdir -p "${RSTSOURCEDIR}/api"
mkdir -p "${HTMLOUTPUTDIR}/_images"
[[ ! -z `ls -A "${RSTSOURCEDIR}/api"` ]] && rm ${RSTSOURCEDIR}/api/*
cargo doc \
  --document-private-items \
  --manifest-path="$ROOTDIR/aisdb_rust/Cargo.toml" \
  --no-deps \
  --package=aisdb \
  --release \
  --target-dir="$HTMLOUTPUTDIR/rust" 

cp "$ROOTDIR/readme.rst" "${RSTSOURCEDIR}/readme.rst"
cp "$ROOTDIR/changelog.rst" "${RSTSOURCEDIR}/changelog.rst"
sphinx-apidoc --separate --force --implicit-namespaces --module-first --no-toc -o "${RSTSOURCEDIR}/api" "${PKGDIR}"
python -m sphinx -a -j auto -q -b=html "${RSTSOURCEDIR}" "${HTMLOUTPUTDIR}"
cp "${RSTSOURCEDIR}/scriptoutput.png" "$HTMLOUTPUTDIR/_images/"
