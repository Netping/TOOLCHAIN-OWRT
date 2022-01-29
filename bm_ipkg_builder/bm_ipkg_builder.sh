#!/bin/sh

usage() {
    echo "Usage: $0 <build_dir>"
    echo -e "\n<build_dir> - specify package directory\n"
    exit 1
}

error() {
    echo "[Error] $1"
    exit 1
}

warning() {
    echo "[Warning] $1"
}

if [ $# -ne 1 ] ; then
    usage
else
    directory=$1
fi

if [ ! -d "$directory" ]; then
    error "Invalid directory $directory"
fi

datadir="$directory/data/"
controlfile="$directory/control"

if [ ! -d "$datadir" ] || [ ! -f "$controlfile" ]; then
    error "Invalid directory structure"
fi

required_fields='Package Version License Section Architecture Description'
optional_fields='Alternatives Source SourceName Depends LicenseFiles Maintainer Essential'

# Check required fields
for field in ${required_fields}; do
    ok=$(grep ^$field $controlfile | awk '{print $2}')
    if [ -z "$ok" ]; then
        error "Missed $field field in controlfile"
    fi
done

# Check optional fields
for field in ${optional_fields}; do
    ok=$(grep ^$field $controlfile | awk '{print $2}')
    if [ -z "$ok" ]; then
        warning "Missed $field field in controlfile"
    fi
done

# Read control parameters
package=$(grep Package $controlfile | awk '{print $2}')
version=$(grep Version $controlfile | awk '{print $2}')
depends=$(grep Depends $controlfile | awk '{$1=""; print $0}')
arch=$(grep Architecture $controlfile | awk '{print $2}')


# Create a temporary directory and populate it
tmpdir=$(mktemp -d)

echo "2.0" > ${tmpdir}/debian-binary

install -d ${tmpdir}/control

cat >${tmpdir}/control/postinst <<\EOL
#!/bin/sh
[ "${IPKG_NO_SCRIPT}" = "1" ] && exit 0
[ -x ${IPKG_INSTROOT}/lib/functions.sh ] || exit 0
. ${IPKG_INSTROOT}/lib/functions.sh
default_postinst $0 $@
EOL

cat >${tmpdir}/control/prerm <<\EOL
#!/bin/sh
[ -x ${IPKG_INSTROOT}/lib/functions.sh ] || exit 0
. ${IPKG_INSTROOT}/lib/functions.sh
default_prerm $0 $@
EOL

chmod +x ${tmpdir}/control/postinst
chmod +x ${tmpdir}/control/prerm

tar -czf ${tmpdir}/data.tar.gz -C $directory/data/ .

data_size=$(stat --printf="%s" ${tmpdir}/data.tar.gz)

is_field==$(grep Installed-Size $controlfile)
if [ -n "$is_field" ]; then
    sed -re "s/^(Installed-Size:)\s+\w+/\1 $data_size/g" $controlfile > ${tmpdir}/control/control
else
    echo "Installed-Size: $data_size" >> ${tmpdir}/control/control
fi

if [ -f "$directory/conffiles" ]; then
    cp $directory/conffiles ${tmpdir}/control/
fi

tar -czf ${tmpdir}/control.tar.gz -C ${tmpdir}/control/ .

rm -fr ${tmpdir}/control

ipk_name="${package}_${version}_${arch}.ipk"
tar -czf $ipk_name -C ${tmpdir}/ .

rm -fr ${tmpdir}

echo "=========================================="
echo "Package: $package"
echo "  Version: $version"
if [ -n "$depends" ]; then
	echo "  Depends: $depends"
fi
echo "  Arch: $arch"
echo "<$ipk_name>"
echo "==============================="
