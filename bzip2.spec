%define	major 1
%define	libname %mklibname bz2_ %{major}
%define	devname %mklibname bz2 -d

%bcond_with pdf

# (tpg) optimize it a bit
%global optflags %optflags -Ofast

Summary:	Extremely powerful file compression utility
Name:		bzip2
Version:	1.0.6
Release:	26
License:	BSD
Group:		Archiving/Compression
URL:		http://www.bzip.org/index.html
Source0:	http://www.bzip.org/%{version}/%{name}-%{version}.tar.gz
Source1:	bzgrep
Source2:	bzme
Source3:	bzme.1
Source4:	bzip2.pc
Source5:	bzip2.rpmlintrc
Patch0:		bzip2-1.0.6-makefile.diff
Patch1:		bzip2-1.0.6-improve-makefile.patch
Patch2:		build_good-so-lib.patch
# (tpg) ClearLinux Patches
Patch10:		fasterfile.patch
Patch11:		cve-2016-3189.patch
Requires:	%{libname} = %{EVRD}
Requires:	coreutils
%if %{with pdf}
BuildRequires:	tetex-dvips
BuildRequires:	tetex-latex
%endif
BuildRequires:	texinfo
BuildRequires:	libtool

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

%prep
%setup -q
%apply_patches

echo "lib = %{_lib}" >> config.in
echo "CFLAGS = %{optflags} -Ofast" >> config.in
echo "LDFLAGS = %{ldflags}" >> config.in

cp %{SOURCE1} bzgrep
cp %{SOURCE2} bzme
cp %{SOURCE3} bzme.1
cp %{SOURCE4} bzip2.pc
sed -i "s|^libdir=|libdir=%{_libdir}|" bzip2.pc

%build
%setup_compile_flags
%make CC="%{__cc}" AR="%{__ar}" RANLIB="%{__ranlib}" -f Makefile-libbz2_so
%make CC="%{__cc}" AR="%{__ar}" RANLIB="%{__ranlib}" -f Makefile

%if %{with pdf}
texi2dvi --pdf manual.texi
%endif

%install
%makeinstall_std -f Makefile-libbz2_so
make install-bin install-dev -f Makefile DESTDIR=%{buildroot}

install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/bzgrep
install -m755 %{SOURCE2} -D %{buildroot}%{_bindir}/bzme
install -m644 %{SOURCE3} -D %{buildroot}%{_mandir}/man1/bzme.1
mkdir -p %{buildroot}%{_libdir}/pkgconfig
install -m0644 bzip2.pc %{buildroot}%{_libdir}/pkgconfig

cat > %{buildroot}%{_bindir}/bzless <<EOF
#!/bin/sh
%{_bindir}/bunzip2 -c "\$@" | %{_bindir}/less
EOF
chmod 755 %{buildroot}%{_bindir}/bzless

%check
make -f Makefile test

%files
%doc README LICENSE CHANGES
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libname}
/%{_lib}/libbz2.so.%{major}*

%files -n %{devname}
%doc *.html
%if %{with pdf}
%doc manual.pdf
%endif
%{_libdir}/libbz2.so
%{_includedir}/*.h
%{_libdir}/pkgconfig/*.pc
