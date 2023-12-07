# bzip2 is used by elfutils, which is used by
# glib2.0, which is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

%define major 1
%define oldlibname %mklibname bz2_ %{major}
%define libname %mklibname bz2
%define devname %mklibname bz2 -d
%define oldlib32name libbz2_%{major}
%define lib32name libbz2
%define dev32name libbz2-devel

# (tpg) optimize it a bit
%global optflags %{optflags} -O3 -fPIC

# (tpg) enable PGO
%if %{cross_compiling}
%bcond_with pgo
%else
%bcond_without pgo
%endif

Summary:	Extremely powerful file compression utility
Name:		bzip2
Version:	1.0.8
Release:	7
License:	BSD
Group:		Archiving/Compression
URL:		http://www.bzip.org/index.html
Source0:	https://sourceware.org/pub/bzip2/bzip2-%{version}.tar.gz
Source1:	bzgrep
Source2:	bzme
Source3:	bzme.1
Source4:	bzip2.rpmlintrc
Patch0:		https://build.opensuse.org/package/view_file/openSUSE:Factory/bzip2/bzip2-1.0.6.2-autoconfiscated.patch
# (tpg) ClearLinux Patches
Patch10:	https://raw.githubusercontent.com/clearlinux-pkgs/bzip2/master/0001-Improve-file-access.patch
Requires:	%{libname} = %{EVRD}
BuildRequires:	libtool
Requires:	pbzip2 > 1.1.13-1

%description
Bzip2 compresses files using the Burrows-Wheeler block-sorting text
compression algorithm, and Huffman coding. Compression is generally
considerably better than that achieved by more conventional LZ77/LZ78-based
compressors, and approaches the performance of the PPM family of statistical
compressors.

The command-line options are deliberately very similar to those of GNU Gzip,
but they are not identical.

%package -n %{libname}
Summary:	Libraries for developing apps which will use bzip2
Group:		System/Libraries
Obsoletes:	%{mklibname bzip2_ 1} < 1.0.6-26
%rename %{oldlibname}

%description -n %{libname}
Library of bzip2 functions, for developing apps which will use the
bzip2 library (aka libz2).

%package -n %{devname}
Summary:	Header files for developing apps which will use bzip2
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname bzip2_ 1 -d} < 1.0.5-3
Provides:	%{mklibname bzip2_ 1 -d} = %{version}-%{release}
Obsoletes:	%{mklibname bzip2 -d} < 1.0.6-26
Provides:	%{mklibname bzip2 -d} = %{version}-%{release}

%description -n %{devname}
Header files and static library of bzip2 functions, for developing apps which
will use the bzip2 library (aka libz2).

%if %{with compat32}
%package -n %{lib32name}
Summary:	Libraries for developing apps which will use bzip2 (32-bit)
Group:		System/Libraries
%rename %{oldlib32name}

%description -n %{lib32name}
Library of bzip2 functions, for developing apps which will use the
bzip2 library (aka libz2).

%package -n %{dev32name}
Summary:	Header files for developing apps which will use bzip2 (32-bit)
Group:		Development/C
Requires:	%{devname} = %{version}-%{release}
Requires:	%{lib32name} = %{version}-%{release}

%description -n %{dev32name}
Header files and static library of bzip2 functions, for developing apps which
will use the bzip2 library (aka libz2).
%endif

%prep
%autosetup -p1

autoreconf -fiv

%build
export CONFIGURE_TOP=$(pwd)

%if %{with compat32}
mkdir build32
cd build32
%configure32
cd ..
%endif

mkdir build
cd build

%if %{with pgo}
export LD_LIBRARY_PATH="$(pwd)"

CFLAGS="%{optflags} -fprofile-generate -mllvm -vp-counters-per-site=4" \
CXXFLAGS="%{optflags} -fprofile-generate" \
LDFLAGS="%{build_ldflags} -fprofile-generate" \
%configure
%make_build
%make_build test
cp %{_bindir}/%{_target_platform}-gcc .
LD_LIBRARY_PATH=. ./bzip2 -9 ../manual.ps
LD_LIBRARY_PATH=. ./bzip2 -9 ../bzip2.c
LD_LIBRARY_PATH=. ./bzip2 %{_target_platform}-gcc
LD_LIBRARY_PATH=. ./bzip2 -d ../manual.ps.bz2
LD_LIBRARY_PATH=. ./bzip2 -d ../bzip2.c.bz2
LD_LIBRARY_PATH=. ./bzip2 -d %{_target_platform}-gcc.bz2

rm -f bzip2 *.o
make clean

unset LD_LIBRARY_PATH
llvm-profdata merge --output=../%{name}-llvm.profdata *.profraw
PROFDATA="$(realpath ../%{name}-llvm.profdata)"

CFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
LDFLAGS="%{build_ldflags} -fprofile-use=$PROFDATA" \
%endif
%configure

cd ..

%if %{with compat32}
%make_build -C build32
%endif
%make_build -C build

%install
%if %{with compat32}
%make_install -C build32
%endif
%make_install -C build

install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/bzgrep
install -m755 %{SOURCE2} -D %{buildroot}%{_bindir}/bzme
install -m644 %{SOURCE3} -D %{buildroot}%{_mandir}/man1/bzme.1

# prolly needed for steam and other stuff
ln -s libbz2.so.1 %{buildroot}%{_libdir}/libbz2.so.1.0
%if %{with compat32}
ln -s libbz2.so.1 %{buildroot}%{_prefix}/lib/libbz2.so.1.0
%endif

cat > %{buildroot}%{_bindir}/bzless <<EOF
#!/bin/sh
%{_bindir}/bunzip2 -c "\$@" | %{_bindir}/less
EOF
chmod 755 %{buildroot}%{_bindir}/bzless

# (tpg) we are using pigz, so move these
for i in bzip2 bunzip2 bzcat; do
    mv %{buildroot}%{_bindir}/"$i" %{buildroot}%{_bindir}/"$i"-st
done

%if ! %{cross_compiling}
%check
%make_build test CC="%{__cc}"
%endif

%files
%doc README LICENSE CHANGES
%{_bindir}/*
%doc %{_mandir}/man1/*

%files -n %{libname}
%{_libdir}/libbz2.so.%{major}*

%files -n %{devname}
%doc *.html
%{_libdir}/libbz2.so
%{_includedir}/*.h
%{_libdir}/pkgconfig/*.pc

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/libbz2.so.%{major}*

%files -n %{dev32name}
%{_prefix}/lib/libbz2.so
%{_prefix}/lib/pkgconfig/*.pc
%endif
