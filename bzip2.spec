%define	major	1
%define	libname	%mklibname %{name}_ %{major}
%define	devname	%mklibname %{name} -d

%bcond_without	uclibc
%bcond_with	pdf

Summary:	Extremely powerful file compression utility
Name:		bzip2
Version:	1.0.6
Release:	7
License:	BSD
Group:		Archiving/Compression
URL:		http://www.bzip.org/index.html
Source0:	http://www.bzip.org/%{version}/%{name}-%{version}.tar.gz
Source1:	bzgrep
Source2:	bzme
Source3:	bzme.1
Patch0:		bzip2-1.0.6-makefile.diff
Requires:	mktemp
Requires:	%{libname} = %{version}-%{release}
%if %{with pdf}
BuildRequires:	tetex-dvips
BuildRequires:	tetex-latex
%endif
BuildRequires:	texinfo
BuildRequires:	libtool
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-9
%endif

%description
Bzip2 compresses files using the Burrows-Wheeler block-sorting text
compression algorithm, and Huffman coding. Compression is generally
considerably better than that achieved by more conventional LZ77/LZ78-based
compressors, and approaches the performance of the PPM family of statistical
compressors.

The command-line options are deliberately very similar to those of GNU Gzip,
but they are not identical.

%package -n	%{libname}
Summary:	Libraries for developing apps which will use bzip2
Group:		System/Libraries

%description -n	%{libname}
Library of bzip2 functions, for developing apps which will use the
bzip2 library (aka libz2).

%if %{with uclibc}
%package -n	uclibc-%{libname}
Summary:	uClibc linked libraries for developing apps which will use bzip2
Group:		System/Libraries

%description -n	uclibc-%{libname}
Library of bzip2 functions, for developing apps which will use the
bzip2 library (aka libz2).
%endif

%package -n	%{devname}
Summary:	Header files for developing apps which will use bzip2
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname bzip2_ 1 -d} < 1.0.5-3
Provides:	%{mklibname bzip2_ 1 -d}
%if %{with uclibc}
Requires:	uclibc-%{libname} = %{EVRD}
%endif

%description -n	%{devname}
Header files and static library of bzip2 functions, for developing apps which
will use the bzip2 library (aka libz2).

%prep

%setup -q
%patch0 -p1 -b .makefile

echo "lib = %{_lib}" >> config.in
echo "CFLAGS = %{optflags}" >> config.in
echo "LDFLAGS = %{ldflags}" >> config.in

cp %{SOURCE1} bzgrep
cp %{SOURCE2} bzme
cp %{SOURCE3} bzme.1

%build
%if %{with uclibc}
%make -f Makefile-libbz2_so CC="%{uclibc_cc}" CFLAGS="%{uclibc_cflags}" LDFLAGS="%{ldflags}"
mkdir -p uclibc
mv libbz2.so.%{major}* uclibc
make clean
%endif

%make -f Makefile-libbz2_so
%make

%if %{with pdf}
texi2dvi --pdf manual.texi
%endif

%install
%if %{with uclibc}
mkdir -p %{buildroot}%{uclibc_root}%{_libdir}
cp -a uclibc/libbz2.so.%{major}* %{buildroot}%{uclibc_root}%{_libdir}
rm %{buildroot}%{uclibc_root}%{_libdir}/libbz2.so
ln -rs %{buildroot}%{uclibc_root}%{_libdir}/libbz2.so.%{major}.*.* %{buildroot}%{uclibc_root}%{_libdir}/libbz2.so
%endif


%makeinstall_std

install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/bzgrep
install -m755 %{SOURCE2} -D %{buildroot}%{_bindir}/bzme
install -m644 %{SOURCE3} -D %{buildroot}%{_mandir}/man1/bzme.1

cat > %{buildroot}%{_bindir}/bzless <<EOF
#!/bin/sh
%{_bindir}/bunzip2 -c "\$@" | %{_bindir}/less
EOF
chmod 755 %{buildroot}%{_bindir}/bzless

# cleanup
rm %{buildroot}%{_libdir}/*.*a

%files
%doc README LICENSE CHANGES
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libname}
%doc LICENSE
%{_libdir}/libbz2.so.%{major}*

%if %{with uclibc}
%files -n uclibc-%{libname}
%doc LICENSE
%{uclibc_root}%{_libdir}/libbz2.so.%{major}*
%endif

%files -n %{devname}
%doc *.html LICENSE
%if %{with pdf}
%doc manual.pdf
%endif
%{_libdir}/libbz2.so
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libbz2.so
%endif
%{_includedir}/*.h
